from typing import Any, Optional

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider, LLMResponse, Message


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self) -> None:
        if not settings.ANTHROPIC_API_KEY:
            raise ProviderError("ANTHROPIC_API_KEY is not configured")
        try:
            from anthropic import AsyncAnthropic
        except ImportError as exc:
            raise ProviderError("anthropic package is not installed") from exc
        self._client: Any = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        system_parts = [m.content for m in messages if m.role == "system"]
        chat = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role in ("user", "assistant")
        ]
        prompt_suffix = (
            "\n\nRespond with valid JSON only, no surrounding prose." if json_mode else ""
        )
        if chat and prompt_suffix and chat[-1]["role"] == "user":
            chat[-1]["content"] = chat[-1]["content"] + prompt_suffix

        kwargs: dict[str, Any] = {
            "model": model or settings.ANTHROPIC_MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": chat,
        }
        if system_parts:
            kwargs["system"] = "\n\n".join(system_parts)

        try:
            response = await self._client.messages.create(**kwargs)
        except Exception as exc:
            raise ProviderError(f"Anthropic completion failed: {exc}") from exc

        text_blocks = [getattr(block, "text", "") for block in response.content]
        text = "".join(text_blocks)
        usage = getattr(response, "usage", None)
        return LLMResponse(
            text=text,
            model=response.model,
            tokens_input=getattr(usage, "input_tokens", 0) or 0,
            tokens_output=getattr(usage, "output_tokens", 0) or 0,
            raw=None,
        )

    async def embed(self, texts: list[str], *, model: Optional[str] = None) -> list[list[float]]:
        raise ProviderError(
            "Anthropic does not provide embeddings; use OpenAI or another embedding provider"
        )
