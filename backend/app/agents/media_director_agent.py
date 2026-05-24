from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.providers.llm import Message


class MediaDirectorAgent(BaseAgent):
    name = "media_director_agent"
    step_name = "media_plan"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        if not payload.get("include_media"):
            return AgentResult(
                name=self.name,
                output={"media_plan": [], "skipped": True},
                status="skipped",
            )

        content_type = payload.get("type", "text_post")
        angle = payload.get("angle") or {}
        text = payload.get("text") or ""
        preferences = payload.get("media_preferences") or {}

        messages = [
            Message(
                role="system",
                content=(
                    "You are a Media Director Agent. Decide what visuals best support the post. "
                    "Return JSON {\"media_plan\": [{\"type\": \"image|carousel_image|gif|video|voice_video\", "
                    "\"prompt\": str, \"aspect_ratio\": str, \"notes\": str}]}. "
                    "Carousel = 2-6 image entries. Voice video = single voice_video entry with prompt as the script."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Content type: {content_type}\n"
                    f"Angle: {angle}\n"
                    f"Draft text: {text[:1200]}\n"
                    f"User preferences: {preferences}"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(
            messages, agent_name=self.name, max_tokens=600
        )
        return AgentResult(
            name=self.name,
            output={"media_plan": payload_json.get("media_plan", [])},
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
