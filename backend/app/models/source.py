import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import CreatedAt, UUIDPrimaryKey
from app.models._types import JsonField


class Source(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "sources"

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_projects.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    title: Mapped[str | None] = mapped_column(String(512), nullable=True)
    url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    trust_level: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column("metadata", JsonField(), nullable=True)

    project: Mapped["ContentProject | None"] = relationship(back_populates="sources")  # noqa: F821
