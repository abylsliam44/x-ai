"""
Agent → model tier routing.

Each agent is mapped to either "strong" (complex reasoning) or "cheap"
(fast, lower-cost) tier.  The router resolves the actual model string from
settings, so changing OPENAI_MODEL_STRONG / OPENAI_MODEL_CHEAP in .env is
enough to reroute all agents without touching agent code.
"""

from __future__ import annotations

from app.core.config import settings

# "strong" agents: need deep reasoning, synthesis, or creative writing.
# "cheap" agents: extraction, retrieval, classification, simple scoring.
_AGENT_TIER: dict[str, str] = {
    # strong
    "insight_agent": "strong",
    "angle_agent": "strong",
    "draft_writer_agent": "strong",
    "editor_agent": "strong",
    # cheap
    "research_agent": "cheap",
    "retrieval_agent": "cheap",
    "outline_agent": "cheap",
    "style_reviewer_agent": "cheap",
    "fact_checker_agent": "cheap",
    "media_director_agent": "cheap",
    # publisher uses no LLM by default
    "publisher_agent": "cheap",
}

# Fact-checker can escalate to strong when confidence is low.
_ESCALATION_AGENTS = {"fact_checker_agent"}


def model_for_agent(agent_name: str, *, escalate: bool = False) -> str:
    """Return the OpenAI model string for *agent_name*.

    Falls back to OPENAI_MODEL_DEFAULT if the agent is not in the routing
    table or ENABLE_MODEL_ROUTING is disabled.
    """
    if not settings.ENABLE_MODEL_ROUTING:
        return settings.OPENAI_MODEL_DEFAULT

    tier = _AGENT_TIER.get(agent_name, "cheap")
    if escalate and agent_name in _ESCALATION_AGENTS:
        tier = "strong"

    if tier == "strong":
        return settings.OPENAI_MODEL_STRONG
    return settings.OPENAI_MODEL_CHEAP
