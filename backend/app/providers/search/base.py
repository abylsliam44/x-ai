from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    published_at: str | None = None
    author: str | None = None
    source: str = "web"
    score: float = 0.5
    raw: dict[str, Any] = field(default_factory=dict)


class SearchProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        raise NotImplementedError
