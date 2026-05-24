"""
Tests for config.py startup validation.

All tests run with MOCK_MODE=true (set by conftest.py) so no real API is
called.  Each test that needs to inspect real-mode validation manually sets
env vars and calls Settings() directly.
"""
import os

import pytest
from pydantic import ValidationError


def _make_settings(**overrides):
    """Create a Settings instance with a known, isolated env (no .env file)."""
    # Use a subclass that does NOT read a .env file, so tests are hermetic.
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from app.core.config import Settings as _BaseSettings

    class IsolatedSettings(_BaseSettings):
        model_config = SettingsConfigDict(
            env_file=None,  # don't read .env — use os.environ only
            case_sensitive=True,
            extra="ignore",
        )

    env_defaults = {
        "MOCK_MODE": "false",
        "SECRET_KEY": "test-secret",
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/test",
        "DATABASE_SYNC_URL": "postgresql+psycopg://postgres:postgres@localhost:5432/test",
        # Clear secrets so real-mode validation can be tested independently
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "X_CLIENT_ID": "",
        "X_CLIENT_SECRET": "",
        "ENABLE_REAL_X_API": "false",
    }
    env_defaults.update(overrides)

    saved = {k: os.environ.get(k) for k in env_defaults}
    for key, value in env_defaults.items():
        os.environ[key] = value

    try:
        return IsolatedSettings()
    finally:
        for key, original in saved.items():
            if original is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original


class TestMockMode:
    def test_mock_mode_requires_no_secrets(self):
        """MOCK_MODE=true must always succeed without any API keys."""
        from app.core.config import Settings

        os.environ["MOCK_MODE"] = "true"
        try:
            s = Settings()
            assert s.is_mock
        finally:
            os.environ.pop("MOCK_MODE", None)

    def test_is_mock_property(self):
        """is_mock is true when either MOCK_MODE=true or provider=mock."""
        from app.core.config import Settings

        os.environ["MOCK_MODE"] = "true"
        os.environ["DEFAULT_LLM_PROVIDER"] = "openai"
        try:
            s = Settings()
            assert s.is_mock is True
        finally:
            os.environ.pop("MOCK_MODE", None)
            os.environ.pop("DEFAULT_LLM_PROVIDER", None)


class TestRealModeOpenAI:
    def test_openai_real_mode_requires_api_key(self):
        """MOCK_MODE=false + DEFAULT_LLM_PROVIDER=openai without key → ValidationError."""
        with pytest.raises((ValidationError, ValueError)):
            _make_settings(DEFAULT_LLM_PROVIDER="openai")

    def test_openai_real_mode_passes_with_key(self):
        """MOCK_MODE=false + DEFAULT_LLM_PROVIDER=openai + key set → valid."""
        s = _make_settings(
            DEFAULT_LLM_PROVIDER="openai",
            OPENAI_API_KEY="sk-test-fake-key-for-validation",
        )
        assert s.OPENAI_API_KEY == "sk-test-fake-key-for-validation"
        assert not s.is_mock

    def test_error_message_is_actionable(self):
        """Validation error message must mention the missing variable name."""
        try:
            _make_settings(DEFAULT_LLM_PROVIDER="openai")
            assert False, "Should have raised"
        except (ValidationError, ValueError) as exc:
            assert "OPENAI_API_KEY" in str(exc)


class TestRealModeX:
    def test_x_real_api_requires_client_id(self):
        """ENABLE_REAL_X_API=true without X_CLIENT_ID → ValidationError."""
        with pytest.raises((ValidationError, ValueError)):
            _make_settings(
                DEFAULT_LLM_PROVIDER="mock",
                MOCK_MODE="false",
                ENABLE_REAL_X_API="true",
                X_CLIENT_SECRET="some-secret",
            )

    def test_x_real_api_requires_client_secret(self):
        """ENABLE_REAL_X_API=true without X_CLIENT_SECRET → ValidationError."""
        with pytest.raises((ValidationError, ValueError)):
            _make_settings(
                DEFAULT_LLM_PROVIDER="mock",
                MOCK_MODE="false",
                ENABLE_REAL_X_API="true",
                X_CLIENT_ID="some-id",
            )

    def test_x_real_api_passes_with_both(self):
        """ENABLE_REAL_X_API=true with both credentials → valid."""
        s = _make_settings(
            DEFAULT_LLM_PROVIDER="mock",
            MOCK_MODE="false",
            ENABLE_REAL_X_API="true",
            X_CLIENT_ID="my-client-id",
            X_CLIENT_SECRET="my-client-secret",
        )
        assert s.ENABLE_REAL_X_API is True
        assert s.X_CLIENT_ID == "my-client-id"

    def test_x_real_api_disabled_needs_no_credentials(self):
        """ENABLE_REAL_X_API=false → no credential validation."""
        s = _make_settings(
            DEFAULT_LLM_PROVIDER="mock",
            MOCK_MODE="false",
            ENABLE_REAL_X_API="false",
        )
        assert s.ENABLE_REAL_X_API is False
