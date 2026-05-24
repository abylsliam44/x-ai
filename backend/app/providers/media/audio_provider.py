import io
import logging
from typing import Any

from app.core.exceptions import ProviderError
from app.providers.media.base import AudioGenerationResult, AudioProvider

logger = logging.getLogger(__name__)

_VOICE_MAP = {
    "default": "alloy",
    "coral": "coral",
    "alloy": "alloy",
    "echo": "echo",
    "fable": "fable",
    "onyx": "onyx",
    "nova": "nova",
    "shimmer": "shimmer",
}


class OpenAIAudioProvider(AudioProvider):
    name = "openai"

    def __init__(self) -> None:
        from app.core.config import settings

        if not settings.OPENAI_API_KEY:
            raise ProviderError("OPENAI_API_KEY is required for audio generation.")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderError("openai package is not installed") from exc

        client_kwargs: dict[str, Any] = {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            "max_retries": settings.OPENAI_MAX_RETRIES,
            "timeout": float(settings.OPENAI_TIMEOUT_SECONDS),
        }
        self._client: Any = AsyncOpenAI(**client_kwargs)

    async def text_to_speech(self, text: str, *, voice: str = "default") -> AudioGenerationResult:
        openai_voice = _VOICE_MAP.get(voice, "alloy")
        try:
            response = await self._client.audio.speech.create(
                model="tts-1",
                voice=openai_voice,
                input=text,
            )
            audio_bytes = response.content
        except Exception as exc:
            raise ProviderError(f"OpenAI TTS failed: {exc}") from exc

        duration = max(1.0, len(text) / 18.0)
        return AudioGenerationResult(
            binary=audio_bytes,
            mime_type="audio/mpeg",
            duration_seconds=duration,
        )

    async def transcribe(self, audio_bytes: bytes, *, mime_type: str) -> str:
        if "wav" in mime_type:
            ext = "wav"
        elif "mp3" in mime_type or "mpeg" in mime_type:
            ext = "mp3"
        elif "webm" in mime_type:
            ext = "webm"
        elif "ogg" in mime_type:
            ext = "ogg"
        else:
            ext = "wav"

        buf = io.BytesIO(audio_bytes)
        buf.name = f"audio.{ext}"
        try:
            response = await self._client.audio.transcriptions.create(
                model="whisper-1",
                file=buf,
                response_format="text",
            )
        except Exception as exc:
            raise ProviderError(f"OpenAI STT failed: {exc}") from exc

        return response if isinstance(response, str) else str(response)
