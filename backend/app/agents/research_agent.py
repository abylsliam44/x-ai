from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.research_service import ResearchService


class ResearchAgent(BaseAgent):
    name = "research_agent"
    step_name = "research"

    def __init__(self, service: ResearchService | None = None) -> None:
        self.service = service or ResearchService()

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        topic = payload.get("topic") or payload.get("query") or ""
        results = await self.service.research(topic, web_limit=5, x_limit=3)
        serialized = [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "published_at": r.published_at,
                "author": r.author,
                "source": r.source,
                "score": r.score,
            }
            for r in results
        ]
        return AgentResult(
            name=self.name,
            output={"topic": topic, "results": serialized},
            model="research",
        )
