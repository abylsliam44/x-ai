"""
Tests for the model router.

Runs in mock mode (conftest sets MOCK_MODE=true), so no real API calls.
Only the routing logic is tested using direct patching of the module-level
settings object — no importlib.reload needed.
"""
import pytest
from unittest.mock import patch

import app.providers.llm.model_router as _router_module
from app.providers.llm.model_router import model_for_agent


def _fake_settings(*, routing=True, strong="gpt-4o", cheap="gpt-4o-mini", default="gpt-4o-mini"):
    return type("S", (), {
        "ENABLE_MODEL_ROUTING": routing,
        "OPENAI_MODEL_STRONG": strong,
        "OPENAI_MODEL_CHEAP": cheap,
        "OPENAI_MODEL_DEFAULT": default,
    })()


class TestModelRouter:
    def test_strong_agents_get_strong_model(self):
        """High-reasoning agents must be routed to the strong tier."""
        s = _fake_settings(strong="gpt-4o", cheap="gpt-4o-mini")
        with patch.object(_router_module, "settings", s):
            for agent in ("insight_agent", "angle_agent", "draft_writer_agent", "editor_agent"):
                result = model_for_agent(agent)
                assert result == "gpt-4o", f"{agent} should use strong model, got {result}"

    def test_cheap_agents_get_cheap_model(self):
        """Light-weight agents must be routed to the cheap tier."""
        s = _fake_settings(strong="gpt-4o", cheap="gpt-4o-mini")
        with patch.object(_router_module, "settings", s):
            for agent in (
                "research_agent",
                "retrieval_agent",
                "outline_agent",
                "style_reviewer_agent",
                "fact_checker_agent",
                "media_director_agent",
            ):
                result = model_for_agent(agent)
                assert result == "gpt-4o-mini", f"{agent} should use cheap model, got {result}"

    def test_fact_checker_escalates_to_strong(self):
        """fact_checker_agent with escalate=True must use the strong model."""
        s = _fake_settings(strong="gpt-4o", cheap="gpt-4o-mini")
        with patch.object(_router_module, "settings", s):
            assert model_for_agent("fact_checker_agent", escalate=True) == "gpt-4o"

    def test_routing_disabled_returns_default(self):
        """When ENABLE_MODEL_ROUTING=false, all agents use OPENAI_MODEL_DEFAULT."""
        s = _fake_settings(routing=False, default="gpt-4o-mini")
        with patch.object(_router_module, "settings", s):
            for agent in ("insight_agent", "research_agent", "editor_agent"):
                result = model_for_agent(agent)
                assert result == "gpt-4o-mini", f"{agent} expected default, got {result}"

    def test_unknown_agent_gets_cheap_model(self):
        """An unrecognised agent name should fall back to the cheap tier."""
        s = _fake_settings(cheap="gpt-4o-mini")
        with patch.object(_router_module, "settings", s):
            assert model_for_agent("some_future_agent") == "gpt-4o-mini"


class TestXOAuthHelpers:
    """Verify PKCE and state-token helpers used by the OAuth flow."""

    def test_pkce_code_verifier_is_43_chars_minimum(self):
        """PKCE code verifier must be at least 43 characters (RFC 7636)."""
        from app.core.security import generate_pkce_pair

        verifier, challenge = generate_pkce_pair()
        assert len(verifier) >= 43
        assert len(challenge) > 0

    def test_state_token_is_unique(self):
        """Each call to generate_state_token must return a different value."""
        from app.core.security import generate_state_token

        states = {generate_state_token() for _ in range(100)}
        assert len(states) == 100

    def test_pkce_challenge_is_base64url(self):
        """Challenge must be URL-safe base64 (no +, /, = padding)."""
        from app.core.security import generate_pkce_pair

        _, challenge = generate_pkce_pair()
        assert "+" not in challenge
        assert "/" not in challenge
        assert "=" not in challenge
