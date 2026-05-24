from types import SimpleNamespace

import pytest

from app.providers.llm.base import Message
from app.providers.llm.openai_provider import (
    OpenAIProvider,
    _is_gpt_image_model,
    _supports_custom_temperature,
    _supports_reasoning_effort,
)


class FakeCompletions:
    def __init__(self) -> None:
        self.kwargs = {}

    async def create(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            model=kwargs["model"],
            choices=[SimpleNamespace(message=SimpleNamespace(content='{"ok": true}'))],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=4),
        )


class FakeImages:
    def __init__(self) -> None:
        self.kwargs = {}

    async def generate(self, **kwargs):
        self.kwargs = kwargs
        return SimpleNamespace(
            data=[
                SimpleNamespace(
                    b64_json="aW1hZ2U=",
                    output_format="png",
                    url=None,
                )
            ]
        )


def _provider_with_fake_client() -> tuple[OpenAIProvider, FakeCompletions]:
    completions = FakeCompletions()
    provider = OpenAIProvider.__new__(OpenAIProvider)
    provider._client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return provider, completions


def _provider_with_fake_image_client() -> tuple[OpenAIProvider, FakeImages]:
    images = FakeImages()
    provider = OpenAIProvider.__new__(OpenAIProvider)
    provider._client = SimpleNamespace(images=images)
    return provider, images


def _fake_settings(**overrides):
    defaults = {
        "OPENAI_MODEL_DEFAULT": "gpt-5.4-mini",
        "OPENAI_MAX_OUTPUT_TOKENS": 4000,
        "OPENAI_REASONING_EFFORT": "low",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_gpt5_chat_uses_current_reasoning_model_parameters(monkeypatch) -> None:
    import app.providers.llm.openai_provider as module

    monkeypatch.setattr(module, "settings", _fake_settings())
    provider, completions = _provider_with_fake_client()

    await provider.complete(
        [Message(role="user", content="Return JSON")],
        temperature=0.2,
        max_tokens=123,
        json_mode=True,
    )

    assert completions.kwargs["max_completion_tokens"] == 123
    assert "max_tokens" not in completions.kwargs
    assert "temperature" not in completions.kwargs
    assert completions.kwargs["extra_body"] == {"reasoning_effort": "low"}
    assert completions.kwargs["response_format"] == {"type": "json_object"}


@pytest.mark.asyncio
async def test_legacy_chat_uses_current_token_parameter_and_temperature(monkeypatch) -> None:
    import app.providers.llm.openai_provider as module

    monkeypatch.setattr(module, "settings", _fake_settings(OPENAI_MODEL_DEFAULT="gpt-4o-mini"))
    provider, completions = _provider_with_fake_client()

    await provider.complete([Message(role="user", content="Hello")], temperature=0.4, max_tokens=42)

    assert completions.kwargs["max_completion_tokens"] == 42
    assert "max_tokens" not in completions.kwargs
    assert completions.kwargs["temperature"] == 0.4
    assert "extra_body" not in completions.kwargs


def test_gpt5_models_do_not_send_custom_temperature() -> None:
    assert not _supports_custom_temperature("gpt-5.4-mini")
    assert not _supports_custom_temperature("o3-mini")


def test_legacy_chat_models_allow_custom_temperature() -> None:
    assert _supports_custom_temperature("gpt-4o-mini")


def test_reasoning_effort_is_only_sent_to_reasoning_models() -> None:
    assert _supports_reasoning_effort("gpt-5.5")
    assert _supports_reasoning_effort("o4-mini")
    assert not _supports_reasoning_effort("gpt-4o-mini")


def test_gpt_image_model_detection() -> None:
    assert _is_gpt_image_model("gpt-image-2")
    assert not _is_gpt_image_model("dall-e-3")


@pytest.mark.asyncio
async def test_legacy_image_helper_uses_gpt_image_base64_defaults(monkeypatch) -> None:
    import app.providers.llm.openai_provider as module

    monkeypatch.setattr(module, "settings", _fake_settings(OPENAI_IMAGE_MODEL="gpt-image-2"))
    provider, images = _provider_with_fake_image_client()

    result = await provider.generate_image("make a card")

    assert result == ["data:image/png;base64,aW1hZ2U="]
    assert images.kwargs["quality"] == "auto"
    assert images.kwargs["extra_body"] == {"output_format": "png"}
    assert "response_format" not in images.kwargs
