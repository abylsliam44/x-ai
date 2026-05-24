import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import Timestamps, UUIDPrimaryKey
from app.models._types import JsonField

PUBLISH_STATUSES = (
    "queued",
    "scheduled",
    "running",
    "succeeded",
    "failed",
    "cancelled",
)


class PublishJob(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "publish_jobs"

    draft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drafts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    platform: Mapped[str] = mapped_column(String(32), default="x", nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="queued", nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JsonField(), nullable=True)

    draft: Mapped["Draft"] = relationship(back_populates="publish_jobs")  # noqa: F821
