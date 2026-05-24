import os
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import NotFoundError
from app.providers.storage.base import StorageProvider, StoredObject


class LocalStorageProvider(StorageProvider):
    name = "local"

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.LOCAL_STORAGE_PATH).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _full(self, key: str) -> Path:
        safe = key.lstrip("/").replace("..", "_")
        return self.base_path / safe

    async def put(self, key: str, data: bytes, *, mime_type: str) -> StoredObject:
        path = self._full(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return StoredObject(
            key=key,
            url=self.url_for(key),
            size_bytes=len(data),
            mime_type=mime_type,
        )

    async def get(self, key: str) -> bytes:
        path = self._full(key)
        if not path.exists():
            raise NotFoundError(f"Storage object not found: {key}")
        return path.read_bytes()

    async def delete(self, key: str) -> None:
        path = self._full(key)
        if path.exists():
            os.remove(path)

    def url_for(self, key: str) -> str:
        return f"/static/{key.lstrip('/')}"
