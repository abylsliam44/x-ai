from typing import Any, Optional

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider, LLMResponse, Message


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ProviderError("OPENAI_API_KEY is not configured")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderError("openai package is not installed") from exc
        self._client: Any = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        kwargs: dict[str, Any] = {
            "model": model or settings.OPENAI_MODEL,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
        except Exception as exc:
            raise ProviderError(f"OpenAI completion failed: {exc}") from exc

        choice = response.choices[0]
        usage = getattr(response, "usage", None)
        return LLMResponse(
            text=choice.message.content or "",
            model=response.model,
            tokens_input=getattr(usage, "prompt_tokens", 0) or 0,
            tokens_output=getattr(usage, "completion_tokens", 0) or 0,
            raw=None,
        )

    async def embed(self, texts: list[str], *, model: Optional[str] = None) -> list[list[float]]:
        try:
            response = await self._client.embeddings.create(
                model=model or settings.OPENAI_EMBEDDING_MODEL,
                input=texts,
            )
        except Exception as exc:
            raise ProviderError(f"OpenAI embeddings failed: {exc}") from exc
        return [item.embedding for item in response.data]
