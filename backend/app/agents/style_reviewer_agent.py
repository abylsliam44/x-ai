from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.draft import Draft
from app.services.style_service import StyleService


class StyleReviewerAgent(BaseAgent):
    name = "style_reviewer_agent"
    step_name = "style"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        draft_id = payload.get("draft_id") or context.draft_id
        style_context = payload.get("style_context") or ""

        text: str
        draft: Draft | None = None
        if draft_id:
            draft = await context.session.get(Draft, draft_id)
            if draft:
                if draft.type == "thread" and draft.thread_items:
                    text = "\n".join(
                        item.get("text", "") if isinstance(item, dict) else str(item)
                        for item in draft.thread_items
                    )
                else:
                    text = draft.text or ""
            else:
                text = payload.get("text", "")
        else:
            text = payload.get("text", "")

        service = StyleService(context.session, llm=context.llm)
        score, notes, model, tok_in, tok_out, latency = await service.score_style(
            text, style_context=style_context
        )

        if draft:
            draft.style_score = score
            await context.session.flush()

        return AgentResult(
            name=self.name,
            output={"score": score, "notes": notes, "draft_id": str(draft_id) if draft_id else None},
            model=model or "style",
            tokens_input=tok_in,
            tokens_output=tok_out,
            latency_ms=latency,
        )
