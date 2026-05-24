from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.rag_service import RagService


class RetrievalAgent(BaseAgent):
    name = "retrieval_agent"
    step_name = "retrieval"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        topic = payload.get("topic") or payload.get("query") or ""
        rag = RagService(context.session)
        results = await rag.search(context.user_id, topic, top_k=6)
        serialized = [r.model_dump(mode="json") for r in results]
        return AgentResult(
            name=self.name,
            output={"topic": topic, "chunks": serialized},
            model="retrieval",
        )
