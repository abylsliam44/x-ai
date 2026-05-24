from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.providers.llm import Message


class OutlineAgent(BaseAgent):
    name = "outline_agent"
    step_name = "outline"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        angle = payload.get("angle") or {}
        content_type = payload.get("type", "text_post")
        rag_chunks = payload.get("rag_chunks") or []

        messages = [
            Message(
                role="system",
                content=(
                    "You are an Outline Agent. Produce a tight outline tailored to the content type. "
                    "Return JSON {\"outline\": [{\"section\": str, \"beats\": [str]}]}. "
                    "Threads use 3-6 sections; text posts use 2-3; research articles use 4-7."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Content type: {content_type}\n"
                    f"Angle: {angle}\n"
                    f"Available evidence: {rag_chunks[:6]}"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(messages, max_tokens=600)
        return AgentResult(
            name=self.name,
            output={"outline": payload_json.get("outline", []), "type": content_type},
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
