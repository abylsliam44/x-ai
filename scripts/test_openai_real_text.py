#!/usr/bin/env python3
"""
Manual script: test real OpenAI text generation.

Requires backend/.env to be populated with a valid OPENAI_API_KEY
and MOCK_MODE=false.

Run from the backend/ directory:
    cd backend && python ../scripts/test_openai_real_text.py
"""
import asyncio
import os
import sys
import time
from pathlib import Path

# Allow running from repo root or backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Load .env manually so we don't need to set env vars
from dotenv import load_dotenv  # pip install python-dotenv
load_dotenv(BACKEND_DIR / ".env")

# Reload settings after env is populated
from app.core.config import get_settings
get_settings.cache_clear()
settings = get_settings()


async def main() -> None:
    print("=" * 60)
    print("OpenAI Real Text Generation Test")
    print("=" * 60)

    if settings.MOCK_MODE:
        print("ERROR: MOCK_MODE=true — switch to false in backend/.env")
        sys.exit(1)
    if not settings.OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY is not set in backend/.env")
        sys.exit(1)

    print(f"Provider  : {settings.DEFAULT_LLM_PROVIDER}")
    print(f"Model (cheap): {settings.OPENAI_MODEL_CHEAP}")
    print(f"Model (strong): {settings.OPENAI_MODEL_STRONG}")
    print()

    from app.providers.llm.openai_provider import OpenAIProvider
    from app.providers.llm.base import Message

    provider = OpenAIProvider()

    messages = [
        Message(role="system", content="You are a concise assistant."),
        Message(
            role="user",
            content=(
                "Write a single sharp insight about AI coding agents "
                "and engineering judgment. One paragraph, no more than 3 sentences."
            ),
        ),
    ]

    print(f"Calling model: {settings.OPENAI_MODEL_CHEAP}")
    started = time.perf_counter()
    response = await provider.complete(messages, model=settings.OPENAI_MODEL_CHEAP, max_tokens=200)
    latency_ms = int((time.perf_counter() - started) * 1000)

    print()
    print("--- Response ---")
    print(response.text)
    print()
    print(f"Model     : {response.model}")
    print(f"Tokens in : {response.tokens_input}")
    print(f"Tokens out: {response.tokens_output}")
    print(f"Latency   : {latency_ms} ms")
    print()
    print("Test PASSED.")


if __name__ == "__main__":
    asyncio.run(main())
