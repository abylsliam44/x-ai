from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.draft import Draft
from app.models.fact_check import FactCheck
from app.providers.llm import Message
from app.schemas.agents import FactCheckReportItem, FactCheckResponse
from app.services.llm_service import LLMService
from app.services.rag_service import RagService
from app.services.research_service import ResearchService
from app.utils.text import extract_claim_candidates

VERDICT_WEIGHTS = {
    "supported": 1.0,
    "weakly_supported": 0.6,
    "unverifiable": 0.4,
    "contradicted": 0.0,
}


class FactCheckService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        llm: LLMService | None = None,
        rag: RagService | None = None,
        research: ResearchService | None = None,
    ) -> None:
        self.session = session
        self.llm = llm or LLMService()
        self.rag = rag or RagService(session)
        self.research = research or ResearchService()

    async def run(self, draft: Draft) -> FactCheckResponse:
        body = self._draft_body(draft)
        claim_candidates = extract_claim_candidates(body)
        if not claim_candidates:
            return FactCheckResponse(draft_id=draft.id, overall_score=1.0, items=[])

        retrieved: list[dict[str, Any]] = []
        for claim in claim_candidates:
            chunks = await self.rag.search(draft.user_id, claim, top_k=3)
            web = await self.research.research(claim, web_limit=2, x_limit=1)
            retrieved.append(
                {
                    "claim": claim,
                    "rag_chunks": [
                        {"text": c.text, "score": c.score, "source_id": str(c.source_id) if c.source_id else None}
                        for c in chunks
                    ],
                    "web": [
                        {
                            "title": r.title,
                            "url": r.url,
                            "snippet": r.snippet,
                            "score": r.score,
                            "source": r.source,
                        }
                        for r in web
                    ],
                }
            )

        messages = [
            Message(
                role="system",
                content=(
                    "You are a rigorous fact-checking assistant. For each claim, output "
                    "a verdict from: supported, weakly_supported, contradicted, unverifiable. "
                    "Be conservative: only mark supported when evidence is direct and credible."
                ),
            ),
            Message(
                role="user",
                content=(
                    "Evaluate the following claims using the supplied evidence. "
                    "Return JSON of shape {\"claims\": [{claim, verdict, confidence, evidence, suggested_fix}]}.\n\n"
                    f"Draft excerpt:\n{body[:2000]}\n\n"
                    f"Evidence packets: {retrieved}"
                ),
            ),
        ]
        payload, _, _ = await self.llm.chat_json(messages, max_tokens=900)
        raw_items = payload.get("claims") or []

        items: list[FactCheckReportItem] = []
        for raw in raw_items:
            claim_text = (raw.get("claim") or "").strip() or claim_candidates[0]
            verdict = raw.get("verdict", "unverifiable")
            if verdict not in VERDICT_WEIGHTS:
                verdict = "unverifiable"
            confidence = float(raw.get("confidence", 0.5))
            evidence = raw.get("evidence") or []
            suggested_fix = raw.get("suggested_fix")
            self.session.add(
                FactCheck(
                    draft_id=draft.id,
                    claim=claim_text,
                    verdict=verdict,
                    confidence=max(0.0, min(1.0, confidence)),
                    evidence=evidence,
                    suggested_fix=suggested_fix,
                )
            )
            items.append(
                FactCheckReportItem(
                    claim=claim_text,
                    verdict=verdict,
                    confidence=confidence,
                    evidence=evidence,
                    suggested_fix=suggested_fix,
                )
            )

        if not items:
            for claim in claim_candidates:
                self.session.add(
                    FactCheck(
                        draft_id=draft.id,
                        claim=claim,
                        verdict="unverifiable",
                        confidence=0.3,
                        evidence=[],
                        suggested_fix=None,
                    )
                )
                items.append(
                    FactCheckReportItem(
                        claim=claim,
                        verdict="unverifiable",
                        confidence=0.3,
                        evidence=[],
                        suggested_fix=None,
                    )
                )

        overall = sum(VERDICT_WEIGHTS[i.verdict] * max(0.1, i.confidence) for i in items)
        denom = sum(max(0.1, i.confidence) for i in items) or 1.0
        score = round(overall / denom, 3)
        draft.fact_check_score = score
        await self.session.flush()
        return FactCheckResponse(draft_id=draft.id, overall_score=score, items=items)

    @staticmethod
    def _draft_body(draft: Draft) -> str:
        if draft.type == "thread" and draft.thread_items:
            return "\n".join(
                (item.get("text", "") if isinstance(item, dict) else str(item))
                for item in draft.thread_items
            )
        return draft.text or ""
