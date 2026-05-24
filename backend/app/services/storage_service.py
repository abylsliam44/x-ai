from typing import Optional

from app.providers.storage import StorageProvider, StoredObject, get_storage_provider
from app.utils.files import extension_for_mime, generate_storage_key


class StorageService:
    def __init__(self, provider: Optional[StorageProvider] = None) -> None:
        self.provider = provider or get_storage_provider()

    async def save_bytes(
        self,
        data: bytes,
        *,
        mime_type: str,
        prefix: str = "media",
    ) -> StoredObject:
        key = generate_storage_key(prefix, extension=extension_for_mime(mime_type))
        return await self.provider.put(key, data, mime_type=mime_type)

    async def get_bytes(self, key: str) -> bytes:
        return await self.provider.get(key)

    async def delete(self, key: str) -> None:
        await self.provider.delete(key)
