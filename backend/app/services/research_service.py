from typing import Optional

from app.providers.search import SearchResult, get_web_search_provider, get_x_search_provider
from app.providers.search.base import SearchProvider


class ResearchService:
    def __init__(
        self,
        web_provider: Optional[SearchProvider] = None,
        x_provider: Optional[SearchProvider] = None,
    ) -> None:
        self.web = web_provider or get_web_search_provider()
        self.x = x_provider or get_x_search_provider()

    async def research(self, query: str, *, web_limit: int = 5, x_limit: int = 5) -> list[SearchResult]:
        web_results = await self.web.search(query, limit=web_limit)
        x_results = await self.x.search(query, limit=x_limit)
        merged = web_results + x_results
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged
