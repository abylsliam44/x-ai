from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.providers.llm import Message


class DraftWriterAgent(BaseAgent):
    name = "draft_writer_agent"
    step_name = "draft"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        content_type = payload.get("type", "text_post")
        angle = payload.get("angle") or {}
        outline = payload.get("outline") or []
        style_context = payload.get("style_context") or ""
        rag_chunks = payload.get("rag_chunks") or []
        additional = payload.get("additional_instructions") or ""

        system_prompt = (
            "You are a Draft Writer Agent for X/Twitter. Write copy with concrete claims, "
            "sharp rhythm, no filler, no emojis, no hashtags unless asked. Match the user's voice."
        )
        if content_type == "thread":
            instruction = (
                "Return JSON {\"thread_items\": [{\"index\": int, \"text\": str}]}. "
                "Each tweet stays under 270 characters. Build tension across the thread."
            )
        elif content_type == "research_article":
            instruction = (
                "Return JSON {\"title\": str, \"text\": str}. Article uses concrete examples "
                "and references the supplied evidence inline."
            )
        else:
            instruction = (
                "Return JSON {\"text\": str}. Single post under 280 characters unless content_type "
                "implies a longer format. Open with the hook."
            )

        messages = [
            Message(role="system", content=system_prompt),
            Message(
                role="user",
                content=(
                    f"Content type: {content_type}\n"
                    f"Angle: {angle}\n"
                    f"Outline: {outline}\n"
                    f"User style samples:\n{style_context[:2000]}\n\n"
                    f"Evidence:\n{rag_chunks[:6]}\n\n"
                    f"Additional instructions: {additional}\n\n"
                    f"{instruction}"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(messages, max_tokens=1400)

        output: dict[str, Any] = {"type": content_type}
        if "thread_items" in payload_json:
            output["thread_items"] = payload_json["thread_items"]
        if "text" in payload_json:
            output["text"] = payload_json["text"]
        if "title" in payload_json:
            output["title"] = payload_json["title"]

        return AgentResult(
            name=self.name,
            output=output,
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
