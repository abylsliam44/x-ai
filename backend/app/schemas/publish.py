import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel


class PublishRequest(BaseModel):
    scheduled_at: datetime | None = None


class PublishJobRead(ORMModel):
    id: uuid.UUID
    draft_id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    status: str
    scheduled_at: datetime | None
    attempts: int
    error_message: str | None
    result: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
