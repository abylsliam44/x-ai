import uuid
from typing import Any

from sqlalchemy import BigInteger, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import CreatedAt, UUIDPrimaryKey
from app.models._types import JsonField

MEDIA_TYPES = ("image", "carousel_image", "gif", "audio", "video")
MEDIA_STATUSES = ("pending", "generating", "ready", "uploaded_to_x", "failed")


class MediaAsset(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "media_assets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drafts.id", ondelete="SET NULL"), index=True, nullable=True
    )
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    storage_key: Mapped[str | None] = mapped_column(String, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(128), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    x_media_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    meta: Mapped[dict[str, Any] | None] = mapped_column("metadata", JsonField(), nullable=True)

    draft: Mapped["Draft | None"] = relationship(back_populates="media")  # noqa: F821
