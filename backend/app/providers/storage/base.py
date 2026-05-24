from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class StoredObject:
    key: str
    url: str
    size_bytes: int
    mime_type: str


class StorageProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def put(self, key: str, data: bytes, *, mime_type: str) -> StoredObject:
        raise NotImplementedError

    @abstractmethod
    async def get(self, key: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def url_for(self, key: str) -> str:
        raise NotImplementedError
