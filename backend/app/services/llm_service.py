import json
import time
from typing import Any, Optional

from app.core.logging import get_logger
from app.providers.llm import LLMProvider, LLMResponse, Message, get_llm_provider

logger = get_logger(__name__)


class LLMService:
    def __init__(self, provider: Optional[LLMProvider] = None) -> None:
        self.provider = provider or get_llm_provider()

    async def chat(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> tuple[LLMResponse, int]:
        started = time.perf_counter()
        response = await self.provider.complete(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "llm.complete",
            extra={
                "provider": self.provider.name,
                "model": response.model,
                "latency_ms": latency_ms,
                "tokens_in": response.tokens_input,
                "tokens_out": response.tokens_output,
            },
        )
        return response, latency_ms

    async def chat_json(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 1024,
    ) -> tuple[dict[str, Any], LLMResponse, int]:
        response, latency_ms = await self.chat(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=True,
        )
        payload = _safe_parse_json(response.text)
        return payload, response, latency_ms


def _safe_parse_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1 and last > first:
            try:
                return json.loads(text[first : last + 1])
            except json.JSONDecodeError:
                pass
    return {"raw_text": text}
