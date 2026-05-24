import uuid
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.angle_agent import AngleAgent
from app.agents.base import AgentContext, AgentResult
from app.agents.draft_writer_agent import DraftWriterAgent
from app.agents.editor_agent import EditorAgent
from app.agents.fact_checker_agent import FactCheckerAgent
from app.agents.insight_agent import InsightAgent
from app.agents.media_director_agent import MediaDirectorAgent
from app.agents.outline_agent import OutlineAgent
from app.agents.research_agent import ResearchAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.style_reviewer_agent import StyleReviewerAgent
from app.core.exceptions import NotFoundError
from app.models.draft import Draft
from app.models.project import ContentProject
from app.services.llm_service import LLMService
from app.services.media_service import MediaService
from app.services.style_service import StyleService


@dataclass
class WorkflowInput:
    project_id: uuid.UUID
    user_id: uuid.UUID
    content_type: str = "text_post"
    angle: dict[str, Any] | None = None
    additional_instructions: str | None = None
    style_sample_ids: list[uuid.UUID] | None = None
    source_ids: list[uuid.UUID] | None = None
    include_media: bool = False
    media_preferences: dict[str, Any] | None = None


@dataclass
class WorkflowOutput:
    draft: Draft
    agent_results: list[AgentResult] = field(default_factory=list)
    media_assets: list[Any] = field(default_factory=list)


class ContentWorkflow:
    def __init__(self, session: AsyncSession, llm: Optional[LLMService] = None) -> None:
        self.session = session
        self.llm = llm or LLMService()

    async def generate_angles(
        self,
        project: ContentProject,
        *,
        count: int = 5,
        additional_context: str | None = None,
    ) -> tuple[list[dict[str, Any]], list[AgentResult]]:
        context = AgentContext(
            session=self.session,
            user_id=project.user_id,
            project_id=project.id,
            llm=self.llm,
        )
        results: list[AgentResult] = []
        research = await ResearchAgent().execute(
            context, {"topic": project.topic}
        )
        results.append(research)

        retrieval = await RetrievalAgent().execute(
            context, {"topic": project.topic}
        )
        results.append(retrieval)

        insights = await InsightAgent().execute(
            context,
            {
                "topic": project.topic,
                "research": research.output.get("results", []),
                "rag_chunks": retrieval.output.get("chunks", []),
            },
        )
        results.append(insights)

        angles = await AngleAgent().execute(
            context,
            {
                "topic": project.topic,
                "goal": project.goal,
                "target_audience": project.target_audience,
                "count": count,
                "insights": insights.output.get("insights", []),
                "additional_context": additional_context,
            },
        )
        results.append(angles)

        return angles.output.get("angles", []), results

    async def generate_draft(self, workflow_input: WorkflowInput) -> WorkflowOutput:
        project = await self.session.get(ContentProject, workflow_input.project_id)
        if not project or project.user_id != workflow_input.user_id:
            raise NotFoundError("Project not found")

        context = AgentContext(
            session=self.session,
            user_id=workflow_input.user_id,
            project_id=project.id,
            llm=self.llm,
        )
        agent_results: list[AgentResult] = []

        research = await ResearchAgent().execute(context, {"topic": project.topic})
        agent_results.append(research)

        retrieval = await RetrievalAgent().execute(context, {"topic": project.topic})
        agent_results.append(retrieval)

        insights = await InsightAgent().execute(
            context,
            {
                "topic": project.topic,
                "research": research.output.get("results", []),
                "rag_chunks": retrieval.output.get("chunks", []),
            },
        )
        agent_results.append(insights)

        if workflow_input.angle is None:
            angles_result = await AngleAgent().execute(
                context,
                {
                    "topic": project.topic,
                    "goal": project.goal,
                    "target_audience": project.target_audience,
                    "count": 4,
                    "insights": insights.output.get("insights", []),
                    "additional_context": workflow_input.additional_instructions,
                },
            )
            agent_results.append(angles_result)
            angles_list = angles_result.output.get("angles", [])
            angle = angles_list[0] if angles_list else {
                "title": project.title,
                "thesis": project.topic,
                "hook": project.topic[:100],
                "rationale": "Default fallback angle",
            }
        else:
            angle = workflow_input.angle

        outline = await OutlineAgent().execute(
            context,
            {
                "type": workflow_input.content_type,
                "angle": angle,
                "rag_chunks": retrieval.output.get("chunks", []),
            },
        )
        agent_results.append(outline)

        style_service = StyleService(self.session, llm=self.llm)
        style_context = await style_service.gather_style_context(
            workflow_input.user_id, workflow_input.style_sample_ids
        )

        draft = Draft(
            project_id=project.id,
            user_id=project.user_id,
            type=workflow_input.content_type,
            status="generating",
        )
        self.session.add(draft)
        await self.session.flush()
        context.draft_id = draft.id

        writer = await DraftWriterAgent().execute(
            context,
            {
                "type": workflow_input.content_type,
                "angle": angle,
                "outline": outline.output.get("outline", []),
                "style_context": style_context,
                "rag_chunks": retrieval.output.get("chunks", []),
                "additional_instructions": workflow_input.additional_instructions,
            },
        )
        agent_results.append(writer)

        if workflow_input.content_type == "thread":
            draft.thread_items = writer.output.get("thread_items", [])
            draft.title = angle.get("title")
        elif workflow_input.content_type == "research_article":
            draft.text = writer.output.get("text", "")
            draft.title = writer.output.get("title") or angle.get("title")
        else:
            draft.text = writer.output.get("text", "")
            draft.title = angle.get("title")

        draft.status = "ready_for_review"
        await self.session.flush()

        fact_check = await FactCheckerAgent().execute(context, {"draft_id": draft.id})
        agent_results.append(fact_check)

        style = await StyleReviewerAgent().execute(
            context, {"draft_id": draft.id, "style_context": style_context}
        )
        agent_results.append(style)

        editor = await EditorAgent().execute(
            context,
            {
                "draft_id": draft.id,
                "fact_check": fact_check.output,
                "style": style.output,
                "instructions": workflow_input.additional_instructions or "",
            },
        )
        agent_results.append(editor)

        media_assets: list[Any] = []
        if workflow_input.include_media:
            media_plan = await MediaDirectorAgent().execute(
                context,
                {
                    "include_media": True,
                    "type": workflow_input.content_type,
                    "angle": angle,
                    "text": draft.text or "",
                    "media_preferences": workflow_input.media_preferences,
                },
            )
            agent_results.append(media_plan)
            media_assets = await self._materialize_media(
                context, draft, media_plan.output.get("media_plan", [])
            )

        draft.quality_score = _quality_score(fact_check.output, style.output)
        await self.session.flush()

        return WorkflowOutput(draft=draft, agent_results=agent_results, media_assets=media_assets)

    async def _materialize_media(
        self,
        context: AgentContext,
        draft: Draft,
        plan: list[dict[str, Any]],
    ) -> list[Any]:
        if not plan:
            return []
        service = MediaService(self.session)
        assets: list[Any] = []
        for item in plan:
            kind = item.get("type", "image")
            prompt = item.get("prompt", "")
            if kind == "carousel_image":
                prompts = [p for p in (item.get("prompts") or [prompt]) if p]
                if len(prompts) < 2:
                    prompts = [prompt, prompt]
                assets.extend(
                    await service.generate_carousel(
                        user_id=draft.user_id,
                        draft_id=draft.id,
                        prompts=prompts[:4],
                    )
                )
            elif kind == "voice_video":
                assets.append(
                    await service.generate_voice_video(
                        user_id=draft.user_id,
                        draft_id=draft.id,
                        script=prompt or draft.text or "",
                    )
                )
            elif kind == "video":
                assets.append(
                    await service.generate_video(
                        user_id=draft.user_id,
                        draft_id=draft.id,
                        prompt=prompt,
                    )
                )
            else:
                assets.append(
                    await service.generate_image(
                        user_id=draft.user_id,
                        draft_id=draft.id,
                        prompt=prompt,
                        aspect_ratio=item.get("aspect_ratio", "1:1"),
                    )
                )
        return assets


def _quality_score(fact_output: dict[str, Any], style_output: dict[str, Any]) -> float:
    fact_score = float(fact_output.get("overall_score", 0.7))
    style_score = float(style_output.get("score", 0.7))
    return round((0.55 * fact_score) + (0.45 * style_score), 3)
