from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.providers.llm import Message


class AngleAgent(BaseAgent):
    name = "angle_agent"
    step_name = "angles"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        topic = payload.get("topic", "")
        goal = payload.get("goal") or "build authority and earn engagement"
        audience = payload.get("target_audience") or "technical X/Twitter readers"
        count = int(payload.get("count", 5))
        insights = payload.get("insights") or []
        additional = payload.get("additional_context") or ""

        messages = [
            Message(
                role="system",
                content=(
                    "You are an Angle Agent. Produce sharp, contrarian-but-defensible angles. "
                    "Each angle has: title, thesis, hook (first line of the post), rationale. "
                    f"Return JSON {{\"angles\": [...]}}. Produce {count} angles."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Topic: {topic}\n"
                    f"Goal: {goal}\n"
                    f"Audience: {audience}\n"
                    f"Insights: {insights}\n"
                    f"Additional context: {additional}"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(messages, max_tokens=900)
        return AgentResult(
            name=self.name,
            output={"angles": payload_json.get("angles", []), "topic": topic},
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
