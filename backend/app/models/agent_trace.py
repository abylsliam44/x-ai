import uuid
from typing import Any

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models._mixins import CreatedAt, UUIDPrimaryKey
from app.models._types import JsonField

TRACE_STATUSES = ("success", "error", "skipped")


class AgentTrace(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "agent_traces"

    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_projects.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    draft_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drafts.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    agent_name: Mapped[str] = mapped_column(String(64), nullable=False)
    step_name: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input: Mapped[dict[str, Any] | None] = mapped_column(JsonField(), nullable=True)
    output: Mapped[dict[str, Any] | None] = mapped_column(JsonField(), nullable=True)
    model: Mapped[str | None] = mapped_column(String(64), nullable=True)
    tokens_input: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_output: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="success", nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
