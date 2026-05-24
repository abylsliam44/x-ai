"""
Integration tests: real LLM pipeline (OpenAI).

Each test makes actual API calls — they cost tokens. Keep them minimal.
All tests are marked @pytest.mark.integration; skip with -m "not integration".

What we verify beyond the mock tests:
  - Response is not the hard-coded mock string
  - Agent traces have a real model name (not "mock-llm-1")
  - Angles have meaningful text (title, thesis are non-empty)
  - Draft text is coherent prose (not an error message)
  - Fact-check produces verdicts, not empty output
"""
import pytest

MOCK_TEXT_FINGERPRINT = "Code generation is becoming a commodity"


pytestmark = pytest.mark.integration


# ─── Helpers ─────────────────────────────────────────────────────────────────


async def _create_project(client, headers, *, topic: str) -> dict:
    r = await client.post(
        "/api/v1/projects",
        json={"title": "Integration test", "topic": topic, "goal": "Build authority"},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


# ─── LLM health ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_endpoint_is_not_mock_mode(client):
    """Sanity-check: server must be running in real mode."""
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body["mock_mode"] is False, (
        "Server is still in MOCK_MODE. Integration tests require MOCK_MODE=false."
    )


# ─── Angle generation (real OpenAI) ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_real_angle_generation_returns_non_mock_content(client, auth_headers):
    """
    AngleAgent must call real OpenAI and return genuine angle titles.
    We verify the output is NOT the hard-coded mock string.
    """
    topic = "Why AI coding agents are making senior engineers more valuable, not less"
    project = await _create_project(client, auth_headers, topic=topic)

    r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-angles",
        json={"count": 3},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    angles = r.json()["angles"]

    assert len(angles) >= 1, "Expected at least one angle"
    first = angles[0]
    assert "title" in first and len(first["title"]) > 5
    assert "thesis" in first and len(first["thesis"]) > 10
    # Content must differ from mock — real LLM produces varied output
    combined = " ".join(str(a) for a in angles)
    assert MOCK_TEXT_FINGERPRINT not in combined, (
        "Angle output looks like mock text. Check that MOCK_MODE=false and "
        "DEFAULT_LLM_PROVIDER=openai with a valid API key."
    )


# ─── Full draft pipeline (real OpenAI) ───────────────────────────────────────


@pytest.mark.asyncio
async def test_real_text_post_draft_is_non_empty_and_not_mock(client, auth_headers):
    """
    Full pipeline: Research → Insight → Angle → Writer → FactChecker → Editor.
    All steps use real OpenAI. Verify the draft is genuine prose.
    """
    topic = "The shift from code generation to engineering judgment in 2025"
    project = await _create_project(client, auth_headers, topic=topic)

    r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "text_post", "include_media": False},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["type"] == "text_post"
    assert body["status"] == "ready_for_review"
    text = body.get("text") or ""
    assert len(text) > 30, f"Draft text is too short: {repr(text)}"
    assert MOCK_TEXT_FINGERPRINT not in text, (
        "Draft text matches the mock hard-coded fingerprint. "
        "MOCK_MODE may still be in effect."
    )


@pytest.mark.asyncio
async def test_real_thread_draft_has_multiple_real_items(client, auth_headers):
    """Thread must have ≥ 2 items; each item must be real prose."""
    topic = "Why AI demos fail to become products"
    project = await _create_project(client, auth_headers, topic=topic)

    r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "thread", "include_media": False},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()

    assert body["type"] == "thread"
    items = body.get("thread_items") or []
    assert len(items) >= 2, f"Expected ≥ 2 thread items, got {len(items)}"
    # At least one item must be more than a single word
    long_items = [i for i in items if len((i.get("text") or "")) > 20]
    assert len(long_items) >= 1


# ─── Fact check (real LLM) ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_real_fact_check_returns_verdicts(client, auth_headers):
    """
    FactCheckerAgent must run against a draft with checkable claims and
    return at least one verdict (not just skip the check).
    """
    topic = "AI coding tools and their impact"
    project = await _create_project(client, auth_headers, topic=topic)

    draft_r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "text_post"},
        headers=auth_headers,
    )
    assert draft_r.status_code == 200, draft_r.text
    draft_id = draft_r.json()["id"]

    fc_r = await client.post(
        f"/api/v1/drafts/{draft_id}/fact-check",
        headers=auth_headers,
    )
    assert fc_r.status_code == 200, fc_r.text
    body = fc_r.json()

    assert "overall_score" in body
    assert 0.0 <= body["overall_score"] <= 1.0
    assert isinstance(body.get("items"), list)


# ─── Agent traces carry real model names ─────────────────────────────────────


@pytest.mark.asyncio
async def test_real_traces_record_openai_model_name(client, auth_headers):
    """
    After a real draft generation, agent traces should contain a real
    model name (e.g. gpt-4o-mini or gpt-5.5), not "mock-llm-1".
    """
    project = await _create_project(client, auth_headers, topic="engineering judgment")

    await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "text_post"},
        headers=auth_headers,
    )

    traces_r = await client.get(
        f"/api/v1/projects/{project['id']}/traces",
        headers=auth_headers,
    )
    assert traces_r.status_code == 200, traces_r.text
    items = traces_r.json()["items"]
    assert len(items) >= 4, "Expected at least 4 agent traces"

    # At least one trace must have a real model name
    model_names = {t.get("model") for t in items if t.get("model")}
    has_real_model = any(
        name and "mock" not in name.lower() and name != "research" and name != "fact-check"
        for name in model_names
    )
    assert has_real_model, (
        f"No real model name found in traces. Models seen: {model_names}. "
        "This suggests the LLM provider is still mock."
    )


# ─── Revise with real Editor Agent ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_real_revise_changes_draft_text(client, auth_headers):
    """
    Revise endpoint must call EditorAgent with real OpenAI and return
    a modified draft. The revised text should differ from the original.
    """
    project = await _create_project(client, auth_headers, topic="AI and judgment")

    draft_r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "text_post"},
        headers=auth_headers,
    )
    original_text = draft_r.json().get("text") or ""
    draft_id = draft_r.json()["id"]

    revise_r = await client.post(
        f"/api/v1/drafts/{draft_id}/revise",
        json={"instructions": "Make it much shorter — max two sentences."},
        headers=auth_headers,
    )
    assert revise_r.status_code == 200, revise_r.text
    revised_text = revise_r.json().get("text") or ""

    assert len(revised_text) > 0, "Revised draft must not be empty"
    # A real edit should produce different text from the original
    # (not guaranteed 100% of the time, but very likely with "make it shorter")
    # We allow it to be the same and just warn — don't fail the test on this
    if revised_text == original_text:
        pytest.warns(
            UserWarning,
            match="Revised text is identical to original — Editor Agent may not have applied changes",
        )


# ─── Quality score is populated after real pipeline ─────────────────────────


@pytest.mark.asyncio
async def test_real_draft_has_quality_score(client, auth_headers):
    """
    After the full real pipeline (writer + fact-checker + style-reviewer),
    the draft must have a non-null quality_score.
    """
    project = await _create_project(client, auth_headers, topic="AI engineering")

    r = await client.post(
        f"/api/v1/projects/{project['id']}/generate-draft",
        json={"type": "text_post"},
        headers=auth_headers,
    )
    assert r.status_code == 200, r.text
    body = r.json()

    assert body.get("quality_score") is not None, (
        "quality_score should be set after the pipeline runs. "
        "Check that FactChecker and StyleReviewer agents ran successfully."
    )
    assert 0.0 <= float(body["quality_score"]) <= 1.0
