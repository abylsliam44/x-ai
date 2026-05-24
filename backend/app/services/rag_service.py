import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.rag_chunk import RagChunk
from app.models.source import Source
from app.models.writing_sample import WritingSample
from app.schemas.rag import RagSearchResult
from app.services.embedding_service import EmbeddingService
from app.utils.text import bm25_like_score, chunk_text, tokenize


class RagService:
    def __init__(self, session: AsyncSession, embedding: Optional[EmbeddingService] = None) -> None:
        self.session = session
        self.embedding = embedding or EmbeddingService()

    async def ingest_writing_sample(self, sample: WritingSample) -> int:
        chunks = chunk_text(
            sample.text,
            chunk_size=settings.RAG_CHUNK_SIZE,
            overlap=settings.RAG_CHUNK_OVERLAP,
        )
        if not chunks:
            return 0

        embeddings = await self._maybe_embed(chunks)
        for idx, text in enumerate(chunks):
            chunk = RagChunk(
                user_id=sample.user_id,
                writing_sample_id=sample.id,
                chunk_text=text,
                embedding=embeddings[idx] if embeddings else None,
                meta={"title": sample.title, "source_type": "writing_sample", "chunk_index": idx},
            )
            self.session.add(chunk)
        await self.session.flush()
        return len(chunks)

    async def ingest_source(self, source: Source, user_id: uuid.UUID) -> int:
        body = (source.raw_text or "").strip()
        if not body:
            return 0
        chunks = chunk_text(
            body,
            chunk_size=settings.RAG_CHUNK_SIZE,
            overlap=settings.RAG_CHUNK_OVERLAP,
        )
        if not chunks:
            return 0

        embeddings = await self._maybe_embed(chunks)
        for idx, text in enumerate(chunks):
            chunk = RagChunk(
                user_id=user_id,
                source_id=source.id,
                chunk_text=text,
                embedding=embeddings[idx] if embeddings else None,
                meta={
                    "title": source.title,
                    "url": source.url,
                    "trust_level": source.trust_level,
                    "source_type": source.source_type,
                    "chunk_index": idx,
                },
            )
            self.session.add(chunk)
        await self.session.flush()
        return len(chunks)

    async def search(
        self,
        user_id: uuid.UUID,
        query: str,
        *,
        top_k: int = 6,
        include_writing_samples: bool = True,
        include_sources: bool = True,
    ) -> list[RagSearchResult]:
        stmt = select(RagChunk).where(RagChunk.user_id == user_id)
        rows = (await self.session.execute(stmt)).scalars().all()
        if not rows:
            return []

        candidates: list[RagChunk] = []
        for c in rows:
            if c.writing_sample_id and not include_writing_samples:
                continue
            if c.source_id and not include_sources:
                continue
            candidates.append(c)
        if not candidates:
            return []

        if settings.ENABLE_PGVECTOR:
            try:
                query_vec = await self.embedding.embed_one(query)
            except Exception:
                query_vec = []
            if query_vec:
                scored = [
                    (chunk, _cosine_sim(query_vec, chunk.embedding or []))
                    for chunk in candidates
                ]
            else:
                scored = self._keyword_score(query, candidates)
        else:
            scored = self._keyword_score(query, candidates)

        scored.sort(key=lambda x: x[1], reverse=True)
        results: list[RagSearchResult] = []
        for chunk, score in scored[:top_k]:
            results.append(
                RagSearchResult(
                    chunk_id=chunk.id,
                    score=float(round(score, 4)),
                    text=chunk.chunk_text,
                    source_id=chunk.source_id,
                    writing_sample_id=chunk.writing_sample_id,
                    meta=chunk.meta,
                )
            )
        return results

    async def _maybe_embed(self, texts: list[str]) -> list[list[float]] | None:
        if not settings.ENABLE_PGVECTOR:
            return None
        try:
            return await self.embedding.embed(texts)
        except Exception:
            return None

    @staticmethod
    def _keyword_score(query: str, chunks: list[RagChunk]) -> list[tuple[RagChunk, float]]:
        q_tokens = tokenize(query)
        return [
            (chunk, bm25_like_score(q_tokens, tokenize(chunk.chunk_text)))
            for chunk in chunks
        ]


def _cosine_sim(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)
