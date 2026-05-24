from functools import lru_cache

from app.core.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.mock_provider import MockLLMProvider


@lru_cache
def get_llm_provider(name: str | None = None) -> LLMProvider:
    chosen = (name or settings.DEFAULT_LLM_PROVIDER).lower()
    if settings.MOCK_MODE or chosen == "mock":
        return MockLLMProvider()
    if chosen == "openai":
        from app.providers.llm.openai_provider import OpenAIProvider

        return OpenAIProvider()
    if chosen == "anthropic":
        from app.providers.llm.anthropic_provider import AnthropicProvider

        return AnthropicProvider()
    return MockLLMProvider()
