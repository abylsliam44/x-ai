import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel

DraftType = Literal[
    "text_post",
    "thread",
    "quote_post",
    "image_post",
    "carousel_post",
    "gif_post",
    "voice_video_post",
    "video_post",
    "research_article",
]


class DraftCreate(BaseModel):
    project_id: uuid.UUID
    type: DraftType
    title: str | None = None
    text: str | None = None
    thread_items: list[dict[str, Any]] | None = None


class DraftRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str | None
    text: str | None
    thread_items: list[Any] | None
    status: str
    quality_score: float | None
    style_score: float | None
    fact_check_score: float | None
    scheduled_at: datetime | None
    published_at: datetime | None
    x_post_id: str | None
    created_at: datetime
    updated_at: datetime


class GenerateAnglesRequest(BaseModel):
    count: int = Field(5, ge=1, le=12)
    additional_context: str | None = None


class AngleOption(BaseModel):
    title: str
    thesis: str
    hook: str
    rationale: str


class GenerateAnglesResponse(BaseModel):
    angles: list[AngleOption]


class GenerateDraftRequest(BaseModel):
    type: DraftType
    angle: AngleOption | None = None
    additional_instructions: str | None = None
    style_sample_ids: list[uuid.UUID] | None = None
    source_ids: list[uuid.UUID] | None = None
    include_media: bool = False
    media_preferences: dict[str, Any] | None = None


class ReviseRequest(BaseModel):
    instructions: str
    keep_structure: bool = True


class ApproveRequest(BaseModel):
    note: str | None = None
