from functools import lru_cache

from app.core.config import settings
from app.providers.storage.base import StorageProvider
from app.providers.storage.local_storage import LocalStorageProvider


@lru_cache
def get_storage_provider() -> StorageProvider:
    if settings.STORAGE_PROVIDER == "s3":
        from app.providers.storage.s3_storage import S3StorageProvider

        return S3StorageProvider()
    return LocalStorageProvider()
