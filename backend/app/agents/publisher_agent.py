from datetime import datetime
from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.draft import Draft
from app.services.publish_service import PublishService


class PublisherAgent(BaseAgent):
    name = "publisher_agent"
    step_name = "publish"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        draft_id = payload.get("draft_id") or context.draft_id
        scheduled_at_raw = payload.get("scheduled_at")
        scheduled_at: datetime | None = None
        if isinstance(scheduled_at_raw, datetime):
            scheduled_at = scheduled_at_raw
        elif isinstance(scheduled_at_raw, str):
            try:
                scheduled_at = datetime.fromisoformat(scheduled_at_raw)
            except ValueError:
                scheduled_at = None

        if not draft_id:
            return AgentResult(
                name=self.name,
                output={"error": "no draft_id"},
                status="error",
                error_message="no draft_id",
            )
        draft = await context.session.get(Draft, draft_id)
        if not draft:
            return AgentResult(
                name=self.name,
                output={"error": "draft missing"},
                status="error",
                error_message="draft missing",
            )

        publish = PublishService(context.session)
        job = await publish.queue(draft, scheduled_at=scheduled_at)

        executed: dict[str, Any] | None = None
        if scheduled_at is None:
            job = await publish.execute(job.id)
            executed = {
                "job_id": str(job.id),
                "status": job.status,
                "result": job.result,
            }

        return AgentResult(
            name=self.name,
            output={
                "queued": True,
                "scheduled_at": scheduled_at.isoformat() if scheduled_at else None,
                "executed": executed,
            },
            model="publisher",
        )
