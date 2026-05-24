from app.core.exceptions import ProviderError
from app.providers.media.base import VideoGenerationResult, VideoProvider


class ExternalVideoProvider(VideoProvider):
    name = "external"

    async def generate_video(self, prompt: str, *, duration_seconds: int = 10) -> VideoGenerationResult:
        raise ProviderError(
            "External video generation is not wired in this MVP build. Implement with Runway, Luma, or similar."
        )

    async def compose_voice_video(
        self,
        audio_bytes: bytes,
        *,
        captions: list[str],
        background_style: str = "minimal",
    ) -> VideoGenerationResult:
        raise ProviderError(
            "Server-side MP4 composition is not wired in this MVP build. Implement with ffmpeg or a hosted service."
        )
