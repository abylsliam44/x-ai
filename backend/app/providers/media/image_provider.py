"""OpenAI-backed image generation provider."""
import base64
from typing import Optional

import httpx

from app.core.config import settings
from app.core.exceptions import ProviderError, ValidationError
from app.providers.media.base import ImageGenerationResult, ImageProvider


class OpenAIImageProvider(ImageProvider):
    name = "openai"

    async def generate_image(
        self,
        prompt: str,
        *,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1",
    ) -> ImageGenerationResult:
        if not settings.OPENAI_API_KEY:
            raise ProviderError("OPENAI_API_KEY is required for OpenAI image generation")

        size, width, height = _openai_size_for_aspect(aspect_ratio)
        final_prompt = prompt.strip()
        if style:
            final_prompt = f"{final_prompt}\n\nVisual style: {style.strip()}"

        payload = {
            "model": settings.OPENAI_IMAGE_MODEL,
            "prompt": final_prompt,
            "size": size,
            "n": 1,
        }
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.OPENAI_ORG_ID:
            headers["OpenAI-Organization"] = settings.OPENAI_ORG_ID
        if settings.OPENAI_PROJECT_ID:
            headers["OpenAI-Project"] = settings.OPENAI_PROJECT_ID

        try:
            async with httpx.AsyncClient(timeout=settings.OPENAI_TIMEOUT_SECONDS) as client:
                response = await client.post(_openai_url("/images/generations"), json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ProviderError(f"OpenAI image generation network error: {exc}") from exc

        if response.status_code >= 400:
            raise ProviderError(
                f"OpenAI image generation failed ({response.status_code}): {response.text}"
            )

        item = (response.json().get("data") or [{}])[0]
        b64_json = item.get("b64_json")
        if b64_json:
            try:
                binary = base64.b64decode(b64_json)
            except Exception as exc:
                raise ProviderError("OpenAI image generation returned invalid base64") from exc
        elif item.get("url"):
            binary = await _download_image(item["url"])
        else:
            raise ProviderError("OpenAI image generation returned no image data")

        return ImageGenerationResult(
            binary=binary,
            mime_type="image/png",
            width=width,
            height=height,
        )


def _openai_url(path: str) -> str:
    base = (settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    return f"{base}{path}" if base.endswith("/v1") else f"{base}/v1{path}"


def _openai_size_for_aspect(aspect_ratio: str) -> tuple[str, int, int]:
    mapping = {
        "1:1": ("1024x1024", 1024, 1024),
        "4:5": ("1024x1536", 1024, 1536),
        "9:16": ("1024x1536", 1024, 1536),
        "16:9": ("1536x1024", 1536, 1024),
    }
    try:
        return mapping[aspect_ratio]
    except KeyError as exc:
        allowed = ", ".join(mapping)
        raise ValidationError(f"Unsupported aspect_ratio '{aspect_ratio}'. Use one of: {allowed}") from exc


async def _download_image(url: str) -> bytes:
    try:
        async with httpx.AsyncClient(timeout=settings.OPENAI_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        raise ProviderError(f"Failed to download generated image: {exc}") from exc
    if response.status_code >= 400:
        raise ProviderError(
            f"Failed to download generated image ({response.status_code}): {response.text}"
        )
    return response.content
