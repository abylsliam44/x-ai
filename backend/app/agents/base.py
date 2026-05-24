import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.agent_trace import AgentTrace
from app.services.llm_service import LLMService

logger = get_logger(__name__)


@dataclass
class AgentContext:
    session: AsyncSession
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    draft_id: Optional[uuid.UUID] = None
    llm: LLMService = field(default_factory=LLMService)
    shared: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResult:
    name: str
    output: dict[str, Any]
    model: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: int = 0
    status: str = "success"
    error_message: Optional[str] = None
    step_name: Optional[str] = None


class BaseAgent(ABC):
    name: str = "base"
    step_name: Optional[str] = None

    @abstractmethod
    async def run(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        raise NotImplementedError

    async def execute(self, context: AgentContext, payload: dict[str, Any]) -> AgentResult:
        started = time.perf_counter()
        try:
            result = await self.run(context, payload)
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            logger.exception("agent.failed", extra={"agent": self.name})
            result = AgentResult(
                name=self.name,
                output={},
                latency_ms=latency_ms,
                status="error",
                error_message=str(exc),
                step_name=self.step_name,
            )
        finally:
            if "result" not in locals() or result.latency_ms == 0:
                latency_ms = int((time.perf_counter() - started) * 1000)
                if "result" in locals():
                    result.latency_ms = result.latency_ms or latency_ms

        await self._save_trace(context, payload, result)
        return result

    async def _save_trace(
        self,
        context: AgentContext,
        payload: dict[str, Any],
        result: AgentResult,
    ) -> None:
        trace = AgentTrace(
            project_id=context.project_id,
            draft_id=context.draft_id,
            agent_name=self.name,
            step_name=result.step_name or self.step_name,
            input=_jsonify(payload),
            output=_jsonify(result.output),
            model=result.model,
            tokens_input=result.tokens_input,
            tokens_output=result.tokens_output,
            latency_ms=result.latency_ms,
            status=result.status,
            error_message=result.error_message,
        )
        context.session.add(trace)
        await context.session.flush()


def _jsonify(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _jsonify(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_jsonify(v) for v in value]
    if isinstance(value, uuid.UUID):
        return str(value)
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
