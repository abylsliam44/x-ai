import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.media_asset import MediaAsset
from app.providers.media import (
    AudioProvider,
    ImageProvider,
    VideoProvider,
    get_audio_provider,
    get_image_provider,
    get_video_provider,
)
from app.services.storage_service import StorageService
from app.utils.media import assert_max_images_per_post


class MediaService:
    def __init__(
        self,
        session: AsyncSession,
        *,
        image_provider: Optional[ImageProvider] = None,
        audio_provider: Optional[AudioProvider] = None,
        video_provider: Optional[VideoProvider] = None,
        storage: Optional[StorageService] = None,
    ) -> None:
        self.session = session
        self.image = image_provider or get_image_provider()
        self.audio = audio_provider or get_audio_provider()
        self.video = video_provider or get_video_provider()
        self.storage = storage or StorageService()

    async def generate_image(
        self,
        *,
        user_id: uuid.UUID,
        draft_id: Optional[uuid.UUID],
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
    ) -> MediaAsset:
        result = await self.image.generate_image(prompt, style=style, aspect_ratio=aspect_ratio)
        stored = await self.storage.save_bytes(result.binary, mime_type=result.mime_type, prefix="images")
        asset = MediaAsset(
            user_id=user_id,
            draft_id=draft_id,
            type="image",
            file_url=stored.url,
            storage_key=stored.key,
            mime_type=result.mime_type,
            size_bytes=stored.size_bytes,
            status="ready",
            meta={
                "prompt": prompt,
                "style": style,
                "aspect_ratio": aspect_ratio,
                "width": result.width,
                "height": result.height,
                "provider": self.image.name,
            },
        )
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def generate_carousel(
        self,
        *,
        user_id: uuid.UUID,
        draft_id: Optional[uuid.UUID],
        prompts: list[str],
        style: Optional[str] = None,
    ) -> list[MediaAsset]:
        assert_max_images_per_post(len(prompts))
        assets: list[MediaAsset] = []
        for idx, prompt in enumerate(prompts):
            result = await self.image.generate_image(prompt, style=style, aspect_ratio="4:5")
            stored = await self.storage.save_bytes(
                result.binary, mime_type=result.mime_type, prefix="carousel"
            )
            asset = MediaAsset(
                user_id=user_id,
                draft_id=draft_id,
                type="carousel_image",
                file_url=stored.url,
                storage_key=stored.key,
                mime_type=result.mime_type,
                size_bytes=stored.size_bytes,
                status="ready",
                meta={
                    "prompt": prompt,
                    "style": style,
                    "index": idx,
                    "total": len(prompts),
                    "provider": self.image.name,
                },
            )
            self.session.add(asset)
            assets.append(asset)
        await self.session.flush()
        return assets

    async def generate_voice_video(
        self,
        *,
        user_id: uuid.UUID,
        draft_id: Optional[uuid.UUID],
        script: str,
        voice: str = "default",
        background_style: str = "minimal",
    ) -> MediaAsset:
        audio = await self.audio.text_to_speech(script, voice=voice)
        captions = [s.strip() for s in script.split(".") if s.strip()]
        video = await self.video.compose_voice_video(
            audio.binary, captions=captions, background_style=background_style
        )
        stored = await self.storage.save_bytes(
            video.binary, mime_type=video.mime_type, prefix="voice_videos"
        )
        asset = MediaAsset(
            user_id=user_id,
            draft_id=draft_id,
            type="video",
            file_url=stored.url,
            storage_key=stored.key,
            mime_type=video.mime_type,
            size_bytes=stored.size_bytes,
            duration_seconds=video.duration_seconds,
            status="ready",
            meta={
                "script": script,
                "voice": voice,
                "background_style": background_style,
                "captions": captions,
                "audio_provider": self.audio.name,
                "video_provider": self.video.name,
                "width": video.width,
                "height": video.height,
                "kind": "voice_video",
            },
        )
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def generate_video(
        self,
        *,
        user_id: uuid.UUID,
        draft_id: Optional[uuid.UUID],
        prompt: str,
        duration_seconds: int = 10,
    ) -> MediaAsset:
        result = await self.video.generate_video(prompt, duration_seconds=duration_seconds)
        stored = await self.storage.save_bytes(
            result.binary, mime_type=result.mime_type, prefix="videos"
        )
        asset = MediaAsset(
            user_id=user_id,
            draft_id=draft_id,
            type="video",
            file_url=stored.url,
            storage_key=stored.key,
            mime_type=result.mime_type,
            size_bytes=stored.size_bytes,
            duration_seconds=result.duration_seconds,
            status="ready",
            meta={
                "prompt": prompt,
                "duration_seconds": duration_seconds,
                "provider": self.video.name,
                "width": result.width,
                "height": result.height,
            },
        )
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def get(self, asset_id: uuid.UUID, user_id: uuid.UUID) -> MediaAsset:
        asset = await self.session.get(MediaAsset, asset_id)
        if not asset or asset.user_id != user_id:
            raise NotFoundError("Media asset not found")
        return asset
