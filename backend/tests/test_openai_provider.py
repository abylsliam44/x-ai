from app.providers.llm.openai_provider import _uses_max_completion_tokens


def test_gpt5_models_use_max_completion_tokens() -> None:
    assert _uses_max_completion_tokens("gpt-5.4-mini")
    assert _uses_max_completion_tokens("gpt-5.5")


def test_legacy_chat_models_use_max_tokens() -> None:
    assert not _uses_max_completion_tokens("gpt-4o-mini")
