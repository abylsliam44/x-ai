from functools import lru_cache

from app.core.config import settings
from app.providers.media.base import AudioProvider, ImageProvider, VideoProvider
from app.providers.media.mock_provider import MockAudioProvider, MockImageProvider, MockVideoProvider


@lru_cache
def get_image_provider() -> ImageProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_MEDIA_GENERATION or settings.DEFAULT_IMAGE_PROVIDER == "mock":
        return MockImageProvider()
    from app.providers.media.image_provider import OpenAIImageProvider

    return OpenAIImageProvider()


@lru_cache
def get_audio_provider() -> AudioProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_MEDIA_GENERATION or settings.DEFAULT_AUDIO_PROVIDER == "mock":
        return MockAudioProvider()
    from app.providers.media.audio_provider import OpenAIAudioProvider

    return OpenAIAudioProvider()


@lru_cache
def get_video_provider() -> VideoProvider:
    if settings.MOCK_MODE or not settings.ENABLE_REAL_MEDIA_GENERATION or settings.DEFAULT_VIDEO_PROVIDER == "mock":
        return MockVideoProvider()
    from app.providers.media.video_provider import ExternalVideoProvider

    return ExternalVideoProvider()
