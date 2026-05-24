from app.core.exceptions import ProviderError
from app.providers.search.base import SearchProvider, SearchResult


class XSearchProvider(SearchProvider):
    name = "x"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        raise ProviderError(
            "Real X search is not wired in this MVP build. "
            "Implement against the X Recent/Full-archive Search endpoint."
        )
