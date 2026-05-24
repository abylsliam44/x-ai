import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import Timestamps, UUIDPrimaryKey
from app.models._types import JsonField

DRAFT_TYPES = (
    "text_post",
    "thread",
    "quote_post",
    "image_post",
    "carousel_post",
    "gif_post",
    "voice_video_post",
    "video_post",
    "research_article",
)

DRAFT_STATUSES = (
    "draft",
    "generating",
    "ready_for_review",
    "approved",
    "scheduled",
    "publishing",
    "published",
    "failed",
)


class Draft(UUIDPrimaryKey, Timestamps, Base):
    __tablename__ = "drafts"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("content_projects.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    thread_items: Mapped[list[Any] | None] = mapped_column(JsonField(), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)

    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    style_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    fact_check_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    x_post_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    project: Mapped["ContentProject"] = relationship(back_populates="drafts")  # noqa: F821
    media: Mapped[list["MediaAsset"]] = relationship(  # noqa: F821
        back_populates="draft", cascade="all, delete-orphan"
    )
    fact_checks: Mapped[list["FactCheck"]] = relationship(  # noqa: F821
        back_populates="draft", cascade="all, delete-orphan"
    )
    publish_jobs: Mapped[list["PublishJob"]] = relationship(  # noqa: F821
        back_populates="draft", cascade="all, delete-orphan"
    )
