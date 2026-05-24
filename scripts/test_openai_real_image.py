#!/usr/bin/env python3
"""
Manual script: test real OpenAI image generation.

Requires:
  - backend/.env: OPENAI_API_KEY set, MOCK_MODE=false
  - ENABLE_REAL_IMAGE_GENERATION=true in backend/.env

Run from the backend/ directory:
    cd backend && python ../scripts/test_openai_real_image.py

The generated image URL is printed. DALL-E URLs expire after ~1 hour.
"""
import asyncio
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / ".env")

from app.core.config import get_settings
get_settings.cache_clear()
settings = get_settings()


async def main() -> None:
    print("=" * 60)
    print("OpenAI Real Image Generation Test")
    print("=" * 60)

    if settings.MOCK_MODE:
        print("ERROR: MOCK_MODE=true — switch to false in backend/.env")
        sys.exit(1)
    if not settings.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set in backend/.env")
        sys.exit(1)
    if not settings.ENABLE_REAL_IMAGE_GENERATION:
        print("ERROR: ENABLE_REAL_IMAGE_GENERATION=false — set to true in backend/.env")
        sys.exit(1)

    print(f"Image model: {settings.OPENAI_IMAGE_MODEL}")
    print()

    from app.providers.llm.openai_provider import OpenAIProvider
    provider = OpenAIProvider()

    prompt = (
        "A clean minimal quote card with dark background. "
        "White text reads: 'The bottleneck in AI coding is no longer code generation. It is judgment.' "
        "Minimalist design, no clutter."
    )
    print(f"Prompt: {prompt}")
    print()

    urls = await provider.generate_image(
        prompt,
        model=settings.OPENAI_IMAGE_MODEL,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    if not urls:
        print("ERROR: No image URLs returned.")
        sys.exit(1)

    print("--- Generated Image URL ---")
    print(urls[0])
    print()
    print("NOTE: DALL-E URLs expire after ~1 hour.")
    print()
    print("Test PASSED.")


if __name__ == "__main__":
    asyncio.run(main())
