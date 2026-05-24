import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    topic: str = Field(min_length=1)
    goal: str | None = None
    target_audience: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    topic: str | None = None
    goal: str | None = None
    target_audience: str | None = None
    status: str | None = None


class ProjectRead(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    topic: str
    goal: str | None
    target_audience: str | None
    status: str
    created_at: datetime
    updated_at: datetime
