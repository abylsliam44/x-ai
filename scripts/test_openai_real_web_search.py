#!/usr/bin/env python3
"""
Manual script: test real OpenAI web search.

Requires:
  - backend/.env: OPENAI_API_KEY set, MOCK_MODE=false
  - ENABLE_REAL_WEB_SEARCH=true
  - DEFAULT_SEARCH_PROVIDER=openai

Run from the backend/ directory:
    cd backend && python ../scripts/test_openai_real_web_search.py
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
    print("OpenAI Real Web Search Test")
    print("=" * 60)

    if settings.MOCK_MODE:
        print("ERROR: MOCK_MODE=true — switch to false in backend/.env")
        sys.exit(1)
    if not settings.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set in backend/.env")
        sys.exit(1)
    if not settings.ENABLE_REAL_WEB_SEARCH:
        print("ERROR: ENABLE_REAL_WEB_SEARCH=false — set to true in backend/.env")
        sys.exit(1)
    if settings.DEFAULT_SEARCH_PROVIDER != "openai":
        print("ERROR: DEFAULT_SEARCH_PROVIDER must be openai")
        sys.exit(1)

    from app.providers.search.web_search_provider import OpenAIWebSearchProvider

    provider = OpenAIWebSearchProvider()
    results = await provider.search(
        "latest practical lessons from deploying AI coding agents in software teams",
        limit=5,
    )

    if not results:
        print("ERROR: No search results returned.")
        sys.exit(1)

    for idx, result in enumerate(results, start=1):
        print(f"{idx}. {result.title}")
        print(f"   {result.url}")
        print(f"   {result.snippet[:240]}")
        print()

    print("Test PASSED.")


if __name__ == "__main__":
    asyncio.run(main())
