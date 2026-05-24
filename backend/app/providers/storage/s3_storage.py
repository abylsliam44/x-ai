from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.storage.base import StorageProvider, StoredObject


class S3StorageProvider(StorageProvider):
    name = "s3"

    def __init__(self) -> None:
        if not settings.S3_BUCKET:
            raise ProviderError("S3_BUCKET is not configured")
        try:
            import aioboto3
        except ImportError as exc:
            raise ProviderError("aioboto3 package is not installed") from exc
        self._session = aioboto3.Session()

    async def put(self, key: str, data: bytes, *, mime_type: str) -> StoredObject:
        async with self._session.client(
            "s3",
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            await client.put_object(
                Bucket=settings.S3_BUCKET,
                Key=key,
                Body=data,
                ContentType=mime_type,
            )
        return StoredObject(
            key=key,
            url=self.url_for(key),
            size_bytes=len(data),
            mime_type=mime_type,
        )

    async def get(self, key: str) -> bytes:
        async with self._session.client(
            "s3",
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            response = await client.get_object(Bucket=settings.S3_BUCKET, Key=key)
            return await response["Body"].read()

    async def delete(self, key: str) -> None:
        async with self._session.client(
            "s3",
            region_name=settings.S3_REGION,
            endpoint_url=settings.S3_ENDPOINT_URL,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        ) as client:
            await client.delete_object(Bucket=settings.S3_BUCKET, Key=key)

    def url_for(self, key: str) -> str:
        if settings.S3_ENDPOINT_URL:
            return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET}/{key}"
        return f"https://{settings.S3_BUCKET}.s3.{settings.S3_REGION}.amazonaws.com/{key}"
