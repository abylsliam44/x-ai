import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.schemas.common import ORMModel


class AgentTraceRead(ORMModel):
    id: uuid.UUID
    project_id: uuid.UUID | None
    draft_id: uuid.UUID | None
    agent_name: str
    step_name: str | None
    input: dict[str, Any] | None
    output: dict[str, Any] | None
    model: str | None
    tokens_input: int | None
    tokens_output: int | None
    latency_ms: int | None
    status: str
    error_message: str | None
    created_at: datetime


class FactCheckReportItem(BaseModel):
    claim: str
    verdict: str
    confidence: float
    evidence: list[dict[str, Any]] | None = None
    suggested_fix: str | None = None


class FactCheckResponse(BaseModel):
    draft_id: uuid.UUID
    overall_score: float
    items: list[FactCheckReportItem]
