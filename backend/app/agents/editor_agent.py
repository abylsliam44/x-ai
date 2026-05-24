from typing import Any

from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.models.draft import Draft
from app.providers.llm import Message


class EditorAgent(BaseAgent):
    name = "editor_agent"
    step_name = "edit"

    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        draft_id = payload.get("draft_id") or context.draft_id
        fact_check = payload.get("fact_check") or {}
        style = payload.get("style") or {}
        instructions = payload.get("instructions") or ""

        if not draft_id:
            return AgentResult(
                name=self.name,
                output={"skipped": True, "reason": "no draft_id"},
                status="skipped",
            )
        draft = await context.session.get(Draft, draft_id)
        if not draft:
            return AgentResult(
                name=self.name,
                output={"error": "draft missing"},
                status="error",
                error_message="Draft missing",
            )

        is_thread = draft.type == "thread" and draft.thread_items
        body = (
            [item.get("text", "") if isinstance(item, dict) else str(item) for item in (draft.thread_items or [])]
            if is_thread
            else draft.text or ""
        )

        instruction = (
            "Return JSON {\"thread_items\": [{\"index\": int, \"text\": str}]}."
            if is_thread
            else "Return JSON {\"text\": str}."
        )

        messages = [
            Message(
                role="system",
                content=(
                    "You are an Editor Agent. Apply fact-check fixes, sharpen voice, cut filler, "
                    "preserve the author's intent. Do not add new claims that lack evidence."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"Draft content type: {draft.type}\n"
                    f"Current body: {body}\n"
                    f"Fact check report: {fact_check}\n"
                    f"Style notes: {style}\n"
                    f"User revision instructions: {instructions}\n\n"
                    f"{instruction}"
                ),
            ),
        ]
        payload_json, response, latency = await context.llm.chat_json(messages, max_tokens=1400)

        if is_thread and payload_json.get("thread_items"):
            draft.thread_items = payload_json["thread_items"]
        if not is_thread and payload_json.get("text"):
            draft.text = payload_json["text"]
        await context.session.flush()

        return AgentResult(
            name=self.name,
            output={"draft_id": str(draft_id), "applied": True, "revision": payload_json},
            model=response.model,
            tokens_input=response.tokens_input,
            tokens_output=response.tokens_output,
            latency_ms=latency,
        )
