import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models._mixins import CreatedAt, UUIDPrimaryKey
from app.models._types import JsonField

VERDICTS = ("supported", "weakly_supported", "contradicted", "unverifiable")


class FactCheck(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "fact_checks"

    draft_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("drafts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    claim: Mapped[str] = mapped_column(Text, nullable=False)
    verdict: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence: Mapped[list[Any] | None] = mapped_column(JsonField(), nullable=True)
    suggested_fix: Mapped[str | None] = mapped_column(Text, nullable=True)

    draft: Mapped["Draft"] = relationship(back_populates="fact_checks")  # noqa: F821
