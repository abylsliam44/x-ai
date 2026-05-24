from app.core.exceptions import ProviderError
from app.providers.search.base import SearchProvider, SearchResult


class TavilyWebSearchProvider(SearchProvider):
    name = "tavily"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        raise ProviderError(
            "Real web search is not wired in this MVP build. Implement using Tavily, Serper, or similar."
        )
