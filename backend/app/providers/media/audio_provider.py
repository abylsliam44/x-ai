from app.core.exceptions import ProviderError
from app.providers.media.base import AudioGenerationResult, AudioProvider


class OpenAIAudioProvider(AudioProvider):
    name = "openai"

    async def text_to_speech(self, text: str, *, voice: str = "default") -> AudioGenerationResult:
        raise ProviderError(
            "Real TTS is not wired in this MVP build. Implement using OpenAI or ElevenLabs SDK."
        )

    async def transcribe(self, audio_bytes: bytes, *, mime_type: str) -> str:
        raise ProviderError(
            "Real transcription is not wired in this MVP build. Implement using whisper or OpenAI audio API."
        )
