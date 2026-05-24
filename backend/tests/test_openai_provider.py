from app.providers.llm.openai_provider import (
    _supports_custom_temperature,
    _uses_max_completion_tokens,
)


def test_gpt5_models_use_max_completion_tokens() -> None:
    assert _uses_max_completion_tokens("gpt-5.4-mini")
    assert _uses_max_completion_tokens("gpt-5.5")


def test_legacy_chat_models_use_max_tokens() -> None:
    assert not _uses_max_completion_tokens("gpt-4o-mini")


def test_gpt5_models_do_not_send_custom_temperature() -> None:
    assert not _supports_custom_temperature("gpt-5.4-mini")
    assert not _supports_custom_temperature("o3-mini")


def test_legacy_chat_models_allow_custom_temperature() -> None:
    assert _supports_custom_temperature("gpt-4o-mini")
