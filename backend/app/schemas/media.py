import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

MediaType = Literal["image", "carousel_image", "gif", "audio", "video"]


class MediaRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    draft_id: uuid.UUID | None
    type: str
    file_url: str | None
    storage_key: str | None
    mime_type: str | None
    size_bytes: int | None
    duration_seconds: float | None
    x_media_id: str | None
    status: str
    meta: dict[str, Any] | None
    created_at: datetime


class GenerateImageRequest(BaseModel):
    draft_id: uuid.UUID | None = None
    prompt: str
    style: str | None = None
    aspect_ratio: str = Field(default="1:1")


class GenerateCarouselRequest(BaseModel):
    draft_id: uuid.UUID | None = None
    prompts: list[str] = Field(min_length=2, max_length=10)
    style: str | None = None


class GenerateVoiceVideoRequest(BaseModel):
    draft_id: uuid.UUID | None = None
    script: str
    voice: str = "default"
    background_style: str = "minimal"


class GenerateVideoRequest(BaseModel):
    draft_id: uuid.UUID | None = None
    prompt: str
    duration_seconds: int = Field(default=10, ge=2, le=140)


class TextToSpeechRequest(BaseModel):
    draft_id: uuid.UUID | None = None
    text: str = Field(min_length=1, max_length=4096)
    voice: str = "alloy"


class SpeechToTextResponse(BaseModel):
    text: str
