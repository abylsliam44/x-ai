"""Real image provider stub. Wire your provider here when ENABLE_REAL_MEDIA_GENERATION is true."""
from typing import Optional

from app.core.exceptions import ProviderError
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
        raise ProviderError(
            "OpenAI image generation is not wired in this MVP build. "
            "Enable it by implementing this provider with the official OpenAI SDK."
        )
