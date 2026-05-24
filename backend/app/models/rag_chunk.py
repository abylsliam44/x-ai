import uuid
from typing import Any

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import CreatedAt, UUIDPrimaryKey
from app.models._types import FloatArrayField, JsonField


class RagChunk(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "rag_chunks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    writing_sample_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("writing_samples.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(FloatArrayField(), nullable=True)
    meta: Mapped[dict[str, Any] | None] = mapped_column("metadata", JsonField(), nullable=True)


__all__ = ["RagChunk"]
