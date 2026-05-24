from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.providers.llm import Message


class InsightAgent(BaseAgent):
    name = "insight_agent"
    step_name = "insights"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        topic = payload.get("topic") or ""
        research = payload.get("research") or []
        rag_chunks = payload.get("rag_chunks") or []

        messages = [
            Message(
                role="system",
                content=(
                    "You are an Insight Agent. Pull out non-obvious, defensible insights from the "
                    "supplied research and retrieval evidence. Avoid generic statements. "
                    "Return JSON {\"insights\": [{\"insight\": str, \"why_it_matters\": str, "
                    "\"evidence_refs\": [str]}]}"
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Topic: {topic}\n\n"
                    f"Research summaries: {research[:8]}\n\n"
                    f"Retrieved internal chunks: {rag_chunks[:8]}\n"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(messages, max_tokens=900)
        return AgentResult(
            name=self.name,
            output={"insights": payload_json.get("insights", []), "topic": topic},
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
