import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class WritingSampleCreate(BaseModel):
    title: str | None = None
    text: str = Field(min_length=1)
    source_type: str = "paste"
    meta: dict[str, Any] | None = None


class WritingSampleRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    source_type: str
    text: str
    meta: dict[str, Any] | None
    created_at: datetime


class SourceCreate(BaseModel):
    project_id: uuid.UUID | None = None
    source_type: Literal["url", "file", "x_post", "manual"] = "manual"
    title: str | None = None
    url: str | None = None
    author: str | None = None
    raw_text: str | None = None
    trust_level: float = Field(default=0.5, ge=0.0, le=1.0)
    meta: dict[str, Any] | None = None


class SourceRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    source_type: str
    title: str | None
    url: str | None
    author: str | None
    raw_text: str | None
    trust_level: float
    meta: dict[str, Any] | None
    created_at: datetime


class RagSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=6, ge=1, le=20)
    include_writing_samples: bool = True
    include_sources: bool = True


class RagSearchResult(BaseModel):
    chunk_id: uuid.UUID
    score: float
    text: str
    source_id: uuid.UUID | None = None
    writing_sample_id: uuid.UUID | None = None
    meta: dict[str, Any] | None = None


class RagSearchResponse(BaseModel):
    query: str
    results: list[RagSearchResult]
