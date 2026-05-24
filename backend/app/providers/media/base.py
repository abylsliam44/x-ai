from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageGenerationResult:
    binary: bytes
    mime_type: str
    width: int
    height: int


@dataclass
class AudioGenerationResult:
    binary: bytes
    mime_type: str
    duration_seconds: float


@dataclass
class VideoGenerationResult:
    binary: bytes
    mime_type: str
    duration_seconds: float
    width: int
    height: int


class ImageProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        *,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
    ) -> ImageGenerationResult:
        raise NotImplementedError


class AudioProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def text_to_speech(
        self,
        text: str,
        *,
        voice: str = "default",
    ) -> AudioGenerationResult:
        raise NotImplementedError

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, *, mime_type: str) -> str:
        raise NotImplementedError


class VideoProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        *,
        duration_seconds: int = 10,
    ) -> VideoGenerationResult:
        raise NotImplementedError

    @abstractmethod
    async def compose_voice_video(
        self,
        audio_bytes: bytes,
        *,
        captions: list[str],
        background_style: str = "minimal",
    ) -> VideoGenerationResult:
        raise NotImplementedError
