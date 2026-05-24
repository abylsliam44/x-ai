from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.draft import Draft
from app.services.fact_check_service import FactCheckService


class FactCheckerAgent(BaseAgent):
    name = "fact_checker_agent"
    step_name = "fact_check"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        draft_id = payload.get("draft_id") or context.draft_id
        if not draft_id:
            return AgentResult(
                name=self.name,
                output={"items": [], "overall_score": 1.0, "skipped": True},
                status="skipped",
                step_name=self.step_name,
            )
        draft = await context.session.get(Draft, draft_id)
        if not draft:
            return AgentResult(
                name=self.name,
                output={"items": [], "overall_score": 0.0, "missing": True},
                status="error",
                error_message="Draft missing",
            )
        service = FactCheckService(context.session)
        report = await service.run(draft)
        return AgentResult(
            name=self.name,
            output=report.model_dump(mode="json"),
            model="fact-check",
        )
