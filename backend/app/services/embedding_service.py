from typing import Optional

from app.core.config import settings
from app.providers.llm import LLMProvider, get_llm_provider
from app.providers.llm.mock_provider import MockLLMProvider


class EmbeddingService:
    def __init__(self, provider: Optional[LLMProvider] = None) -> None:
        if provider is not None:
            self.provider = provider
        elif settings.MOCK_MODE:
            self.provider = MockLLMProvider()
        else:
            self.provider = get_llm_provider()

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        return await self.provider.embed(texts)

    async def embed_one(self, text: str) -> list[float]:
        vectors = await self.embed([text])
        return vectors[0] if vectors else []
