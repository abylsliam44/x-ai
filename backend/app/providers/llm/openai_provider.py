import logging
import time
from typing import Any, Optional

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.llm.base import LLMProvider, LLMResponse, Message

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ProviderError(
                "OPENAI_API_KEY is required when MOCK_MODE=false and "
                "DEFAULT_LLM_PROVIDER=openai."
            )
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ProviderError("openai package is not installed") from exc

        client_kwargs: dict[str, Any] = {
            "api_key": settings.OPENAI_API_KEY,
            "base_url": settings.OPENAI_BASE_URL or "https://api.openai.com/v1",
            "max_retries": settings.OPENAI_MAX_RETRIES,
            "timeout": float(settings.OPENAI_TIMEOUT_SECONDS),
        }
        if settings.OPENAI_ORG_ID:
            client_kwargs["organization"] = settings.OPENAI_ORG_ID
        if settings.OPENAI_PROJECT_ID:
            client_kwargs["project"] = settings.OPENAI_PROJECT_ID

        self._client: Any = AsyncOpenAI(**client_kwargs)

    async def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        from openai import APIConnectionError, APIStatusError, RateLimitError

        # Caller may pass a specific model; fall back to the cheap default.
        resolved_model = model or settings.OPENAI_MODEL_DEFAULT
        capped_tokens = min(max_tokens, settings.OPENAI_MAX_OUTPUT_TOKENS)

        kwargs: dict[str, Any] = {
            "model": resolved_model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
            "max_tokens": capped_tokens,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        started = time.perf_counter()
        try:
            response = await self._client.chat.completions.create(**kwargs)
        except RateLimitError as exc:
            raise ProviderError(f"OpenAI rate limit exceeded after retries: {exc}") from exc
        except APIConnectionError as exc:
            raise ProviderError(f"OpenAI connection error: {exc}") from exc
        except APIStatusError as exc:
            if exc.status_code == 401:
                raise ProviderError("OpenAI API key is invalid or unauthorised") from exc
            if exc.status_code == 404:
                raise ProviderError(
                    f"OpenAI model not found: {resolved_model}. "
                    "Check OPENAI_MODEL_STRONG / OPENAI_MODEL_CHEAP in .env."
                ) from exc
            raise ProviderError(f"OpenAI API error {exc.status_code}: {exc.message}") from exc
        except Exception as exc:
            raise ProviderError(f"OpenAI completion failed: {exc}") from exc

        latency_ms = int((time.perf_counter() - started) * 1000)
        choice = response.choices[0]
        usage = response.usage
        actual_model = response.model or resolved_model

        logger.debug(
            "openai.complete",
            extra={
                "model": actual_model,
                "latency_ms": latency_ms,
                "tokens_in": getattr(usage, "prompt_tokens", 0),
                "tokens_out": getattr(usage, "completion_tokens", 0),
            },
        )

        return LLMResponse(
            text=choice.message.content or "",
            model=actual_model,
            tokens_input=getattr(usage, "prompt_tokens", 0) or 0,
            tokens_output=getattr(usage, "completion_tokens", 0) or 0,
            raw=None,
        )

    async def embed(self, texts: list[str], *, model: Optional[str] = None) -> list[list[float]]:
        from openai import APIConnectionError, APIStatusError, RateLimitError

        resolved_model = model or settings.OPENAI_EMBEDDING_MODEL
        try:
            response = await self._client.embeddings.create(
                model=resolved_model,
                input=texts,
            )
        except RateLimitError as exc:
            raise ProviderError(f"OpenAI rate limit exceeded after retries: {exc}") from exc
        except APIConnectionError as exc:
            raise ProviderError(f"OpenAI connection error: {exc}") from exc
        except APIStatusError as exc:
            raise ProviderError(f"OpenAI API error {exc.status_code}: {exc.message}") from exc
        except Exception as exc:
            raise ProviderError(f"OpenAI embeddings failed: {exc}") from exc

        return [item.embedding for item in response.data]

    async def generate_image(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
    ) -> list[str]:
        """Return a list of image URLs."""
        from openai import APIStatusError

        resolved_model = model or settings.OPENAI_IMAGE_MODEL
        try:
            response = await self._client.images.generate(
                model=resolved_model,
                prompt=prompt,
                size=size,  # type: ignore[arg-type]
                quality=quality,  # type: ignore[arg-type]
                n=n,
                response_format="url",
            )
        except APIStatusError as exc:
            raise ProviderError(
                f"OpenAI image generation failed ({exc.status_code}): {exc.message}"
            ) from exc
        except Exception as exc:
            raise ProviderError(f"OpenAI image generation failed: {exc}") from exc

        return [item.url for item in response.data if item.url]

    async def transcribe_audio(
        self,
        audio_path: str,
        *,
        model: Optional[str] = None,
        language: Optional[str] = None,
    ) -> str:
        """Transcribe an audio file and return the text."""
        from openai import APIStatusError

        resolved_model = model or settings.OPENAI_STT_MODEL
        try:
            with open(audio_path, "rb") as audio_file:
                response = await self._client.audio.transcriptions.create(
                    model=resolved_model,
                    file=audio_file,
                    language=language,
                )
        except APIStatusError as exc:
            raise ProviderError(
                f"OpenAI STT failed ({exc.status_code}): {exc.message}"
            ) from exc
        except Exception as exc:
            raise ProviderError(f"OpenAI STT failed: {exc}") from exc

        return response.text

    async def generate_speech(
        self,
        text: str,
        output_path: str,
        *,
        model: Optional[str] = None,
        voice: Optional[str] = None,
    ) -> None:
        """Generate speech from text and write MP3 to *output_path*."""
        from openai import APIStatusError

        resolved_model = model or settings.OPENAI_TTS_MODEL
        resolved_voice = voice or settings.OPENAI_TTS_VOICE
        try:
            response = await self._client.audio.speech.create(
                model=resolved_model,
                voice=resolved_voice,  # type: ignore[arg-type]
                input=text,
            )
            response.stream_to_file(output_path)
        except APIStatusError as exc:
            raise ProviderError(
                f"OpenAI TTS failed ({exc.status_code}): {exc.message}"
            ) from exc
        except Exception as exc:
            raise ProviderError(f"OpenAI TTS failed: {exc}") from exc
