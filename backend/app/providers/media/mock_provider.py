import struct
from typing import Optional

from app.providers.media.base import (
    AudioGenerationResult,
    AudioProvider,
    ImageGenerationResult,
    ImageProvider,
    VideoGenerationResult,
    VideoProvider,
)

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _build_minimal_png(width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        import zlib

        length = struct.pack(">I", len(data))
        crc = struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return length + tag + data + crc

    import zlib

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + b"\x80\x80\x80" * width for _ in range(height))
    idat = zlib.compress(raw)
    return _PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


class MockImageProvider(ImageProvider):
    name = "mock"

    async def generate_image(
        self,
        prompt: str,
        *,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
    ) -> ImageGenerationResult:
        width, height = _aspect_to_dims(aspect_ratio)
        return ImageGenerationResult(
            binary=_build_minimal_png(width, height),
            mime_type="image/png",
            width=width,
            height=height,
        )


class MockAudioProvider(AudioProvider):
    name = "mock"

    async def text_to_speech(self, text: str, *, voice: str = "default") -> AudioGenerationResult:
        duration = max(2.0, min(60.0, len(text) / 18.0))
        payload = b"MOCK-WAV-" + text.encode("utf-8")[:512]
        return AudioGenerationResult(
            binary=payload,
            mime_type="audio/wav",
            duration_seconds=duration,
        )

    async def transcribe(self, audio_bytes: bytes, *, mime_type: str) -> str:
        return "Mock transcription: this is what the user said in the recording."


class MockVideoProvider(VideoProvider):
    name = "mock"

    async def generate_video(
        self,
        prompt: str,
        *,
        duration_seconds: int = 10,
    ) -> VideoGenerationResult:
        payload = b"MOCK-MP4-VIDEO-" + prompt.encode("utf-8")[:512]
        return VideoGenerationResult(
            binary=payload,
            mime_type="video/mp4",
            duration_seconds=float(duration_seconds),
            width=1080,
            height=1920,
        )

    async def compose_voice_video(
        self,
        audio_bytes: bytes,
        *,
        captions: list[str],
        background_style: str = "minimal",
    ) -> VideoGenerationResult:
        payload = b"MOCK-VOICE-MP4-" + b"|".join(c.encode("utf-8")[:120] for c in captions)
        duration = max(4.0, min(140.0, len(audio_bytes) / 16000.0))
        return VideoGenerationResult(
            binary=payload,
            mime_type="video/mp4",
            duration_seconds=duration,
            width=1080,
            height=1920,
        )


def _aspect_to_dims(aspect_ratio: str) -> tuple[int, int]:
    mapping = {
        "1:1": (8, 8),
        "16:9": (16, 9),
        "9:16": (9, 16),
        "4:5": (8, 10),
    }
    return mapping.get(aspect_ratio, (8, 8))
