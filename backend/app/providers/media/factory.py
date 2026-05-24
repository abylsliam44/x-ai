from functools import lru_cache

from app.core.config import settings
from app.providers.media.base import AudioProvider, ImageProvider, VideoProvider
from app.providers.media.mock_provider import MockAudioProvider, MockImageProvider, MockVideoProvider


@lru_cache
def get_image_provider() -> ImageProvider:
    if (
        settings.MOCK_MODE
        or not settings.real_image_generation_enabled
        or settings.DEFAULT_IMAGE_PROVIDER == "mock"
    ):
        return MockImageProvider()
    from app.providers.media.image_provider import OpenAIImageProvider

    return OpenAIImageProvider()


@lru_cache
def get_audio_provider() -> AudioProvider:
    real_requested = (
        settings.ENABLE_REAL_TTS
        or settings.ENABLE_REAL_STT
        or settings.ENABLE_REAL_MEDIA_GENERATION
    )
    if settings.MOCK_MODE or not real_requested or not settings.OPENAI_API_KEY:
        return MockAudioProvider()
    from app.providers.media.audio_provider import OpenAIAudioProvider

    return OpenAIAudioProvider()


@lru_cache
def get_video_provider() -> VideoProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_MEDIA_GENERATION or settings.DEFAULT_VIDEO_PROVIDER == "mock":
        return MockVideoProvider()
    from app.providers.media.video_provider import ExternalVideoProvider

    return ExternalVideoProvider()
