from functools import lru_cache

from app.core.config import settings
from app.providers.search.base import SearchProvider
from app.providers.search.mock_provider import MockWebSearchProvider, MockXSearchProvider


@lru_cache
def get_web_search_provider() -> SearchProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_WEB_SEARCH or settings.DEFAULT_SEARCH_PROVIDER == "mock":
        return MockWebSearchProvider()
    if settings.DEFAULT_SEARCH_PROVIDER == "openai":
        from app.providers.search.web_search_provider import OpenAIWebSearchProvider

        return OpenAIWebSearchProvider()
    from app.providers.search.web_search_provider import TavilyWebSearchProvider

    return TavilyWebSearchProvider()


@lru_cache
def get_x_search_provider() -> SearchProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_X_SEARCH:
        return MockXSearchProvider()
    from app.providers.search.x_search_provider import XSearchProvider

    return XSearchProvider()
