from typing import Optional

from app.core.logging import get_logger
from app.providers.search import SearchResult, get_web_search_provider, get_x_search_provider
from app.providers.search.base import SearchProvider

logger = get_logger(__name__)


class ResearchService:
    def __init__(
        self,
        web_provider: Optional[SearchProvider] = None,
        x_provider: Optional[SearchProvider] = None,
    ) -> None:
        self.web = web_provider or get_web_search_provider()
        self.x = x_provider or get_x_search_provider()

    async def research(self, query: str, *, web_limit: int = 5, x_limit: int = 5) -> list[SearchResult]:
        web_results = await self._safe_search(self.web, query, limit=web_limit)
        x_results = await self._safe_search(self.x, query, limit=x_limit)
        merged = web_results + x_results
        merged.sort(key=lambda r: r.score, reverse=True)
        return merged

    async def _safe_search(
        self,
        provider: SearchProvider,
        query: str,
        *,
        limit: int,
    ) -> list[SearchResult]:
        try:
            return await provider.search(query, limit=limit)
        except Exception as exc:
            logger.warning(
                "research.provider_failed",
                extra={"provider": provider.name, "error": str(exc)},
            )
            return []
