import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.writing_sample import WritingSample
from app.providers.llm import Message
from app.services.llm_service import LLMService


class StyleService:
    def __init__(self, session: AsyncSession, llm: Optional[LLMService] = None) -> None:
        self.session = session
        self.llm = llm or LLMService()

    async def gather_style_context(
        self,
        user_id: uuid.UUID,
        sample_ids: Optional[list[uuid.UUID]] = None,
    ) -> str:
        stmt = select(WritingSample).where(WritingSample.user_id == user_id)
        if sample_ids:
            stmt = stmt.where(WritingSample.id.in_(sample_ids))
        rows = (await self.session.execute(stmt)).scalars().all()
        if not rows:
            return ""
        snippets = []
        for sample in rows[:5]:
            snippet = (sample.text or "")[:600]
            snippets.append(f"--- Sample ({sample.title or 'untitled'}) ---\n{snippet}")
        return "\n\n".join(snippets)

    async def score_style(
        self,
        text: str,
        *,
        style_context: str,
    ) -> tuple[float, str, str | None, int, int, int]:
        """Returns (score, notes, model, tokens_in, tokens_out, latency_ms)."""
        if not text.strip():
            return 0.0, "Empty draft", None, 0, 0, 0

        if not style_context:
            return 0.7, "No writing samples provided; using default tone heuristics.", None, 0, 0, 0

        messages = [
            Message(
                role="system",
                content=(
                    "You score how closely a draft matches a user's writing samples. "
                    "Return JSON {\"score\": 0-1 float, \"notes\": string with concrete suggestions}. "
                    "Be strict; reward voice, rhythm, vocabulary, sentence shape."
                ),
            ),
            Message(
                role="user",
                content=(
                    f"User samples:\n{style_context[:3000]}\n\n"
                    f"Draft:\n{text[:3000]}\n\n"
                    "Score now."
                ),
            ),
        ]
        payload, llm_resp, latency = await self.llm.chat_json(
            messages, agent_name="style_reviewer_agent", max_tokens=400
        )
        score = float(payload.get("score", 0.7))
        notes = str(payload.get("notes", "")).strip() or "Style is acceptable."
        return (
            max(0.0, min(1.0, score)),
            notes,
            llm_resp.model,
            llm_resp.tokens_input,
            llm_resp.tokens_output,
            latency,
        )
