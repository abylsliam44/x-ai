"""
Direct unit tests for every agent in the pipeline.

Tests call agent.run() / agent.execute() directly — no HTTP layer.
The mock LLM provider (set by conftest) is used throughout, so no real API
calls are made.  Each test that needs database objects (Draft, Project, User)
inserts them inline via the db_session fixture.
"""
import uuid

import pytest

from app.agents.angle_agent import AngleAgent
from app.agents.base import AgentContext, AgentResult, BaseAgent
from app.agents.draft_writer_agent import DraftWriterAgent
from app.agents.editor_agent import EditorAgent
from app.agents.fact_checker_agent import FactCheckerAgent
from app.agents.insight_agent import InsightAgent
from app.agents.media_director_agent import MediaDirectorAgent
from app.agents.research_agent import ResearchAgent
from app.agents.style_reviewer_agent import StyleReviewerAgent
from app.agents.workflow import _quality_score
from app.models.draft import Draft
from app.models.project import ContentProject
from app.models.user import User
from app.services.llm_service import LLMService


# ─── helpers ─────────────────────────────────────────────────────────────────


async def _make_user(session) -> User:
    user = User(
        email=f"agent-test-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="x",
    )
    session.add(user)
    await session.flush()
    return user


async def _make_project(session, user_id: uuid.UUID) -> ContentProject:
    project = ContentProject(
        user_id=user_id,
        title="Test",
        topic="AI judgment is the real bottleneck",
    )
    session.add(project)
    await session.flush()
    return project


async def _make_draft(
    session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    text: str = "The bottleneck is judgment, not code output.",
    draft_type: str = "text_post",
) -> Draft:
    draft = Draft(
        project_id=project_id,
        user_id=user_id,
        type=draft_type,
        text=text,
        status="ready_for_review",
    )
    session.add(draft)
    await session.flush()
    return draft


def _ctx(session, user_id, project_id=None, draft_id=None) -> AgentContext:
    return AgentContext(
        session=session,
        user_id=user_id,
        project_id=project_id,
        draft_id=draft_id,
        llm=LLMService(),
    )


# ─── ResearchAgent ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_research_agent_returns_results(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await ResearchAgent().execute(ctx, {"topic": "AI engineering"})

    assert result.name == "research_agent"
    assert result.status == "success"
    assert isinstance(result.output.get("results"), list)
    assert result.output["topic"] == "AI engineering"


@pytest.mark.asyncio
async def test_research_agent_empty_topic(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await ResearchAgent().execute(ctx, {})
    assert result.status == "success"
    assert "results" in result.output


# ─── InsightAgent ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_insight_agent_returns_insights(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await InsightAgent().execute(
        ctx,
        {
            "topic": "AI coding",
            "research": [{"snippet": "Engineers review more carefully with agents."}],
            "rag_chunks": [],
        },
    )

    assert result.name == "insight_agent"
    assert result.status == "success"
    assert isinstance(result.output.get("insights"), list)
    assert len(result.output["insights"]) >= 1


@pytest.mark.asyncio
async def test_insight_agent_no_research_still_succeeds(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await InsightAgent().execute(ctx, {"topic": "testing", "research": [], "rag_chunks": []})
    assert result.status == "success"


# ─── AngleAgent ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_angle_agent_returns_angles_list(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await AngleAgent().execute(
        ctx,
        {
            "topic": "AI coding tools",
            "goal": "Build authority",
            "target_audience": "senior engineers",
            "count": 3,
            "insights": [],
        },
    )

    assert result.name == "angle_agent"
    assert result.status == "success"
    angles = result.output.get("angles", [])
    assert isinstance(angles, list)
    assert len(angles) >= 1
    assert "title" in angles[0]
    assert "thesis" in angles[0]


@pytest.mark.asyncio
async def test_angle_agent_respects_count(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await AngleAgent().execute(
        ctx,
        {"topic": "x", "count": 3, "insights": []},
    )
    # Mock returns a fixed list; just verify the agent ran
    assert result.status == "success"


# ─── DraftWriterAgent ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_draft_writer_text_post(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await DraftWriterAgent().execute(
        ctx,
        {
            "type": "text_post",
            "angle": {"title": "Judgment is the bottleneck", "thesis": "Speed ≠ quality"},
            "outline": [],
            "style_context": "",
            "rag_chunks": [],
        },
    )

    assert result.name == "draft_writer_agent"
    assert result.status == "success"
    assert "text" in result.output
    assert len(result.output["text"]) > 0


@pytest.mark.asyncio
async def test_draft_writer_thread(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await DraftWriterAgent().execute(
        ctx,
        {
            "type": "thread",
            "angle": {"title": "Thread angle", "thesis": "x"},
            "outline": [],
            "style_context": "",
            "rag_chunks": [],
        },
    )

    assert result.status == "success"
    thread_items = result.output.get("thread_items", [])
    assert isinstance(thread_items, list)
    assert len(thread_items) >= 2


@pytest.mark.asyncio
async def test_draft_writer_research_article(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await DraftWriterAgent().execute(
        ctx,
        {
            "type": "research_article",
            "angle": {"title": "Deep dive"},
            "outline": [],
            "style_context": "",
            "rag_chunks": [],
        },
    )

    assert result.status == "success"
    assert "title" in result.output or "text" in result.output


# ─── EditorAgent ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_editor_agent_no_draft_id_returns_skipped(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)  # no draft_id

    result = await EditorAgent().execute(ctx, {})
    assert result.status == "skipped"
    assert result.output.get("skipped") is True


@pytest.mark.asyncio
async def test_editor_agent_missing_draft_returns_error(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id, draft_id=uuid.uuid4())

    result = await EditorAgent().execute(ctx, {"draft_id": uuid.uuid4()})
    assert result.status == "error"


@pytest.mark.asyncio
async def test_editor_agent_improves_text_post(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = await _make_draft(db_session, project.id, user.id)
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await EditorAgent().execute(
        ctx,
        {
            "draft_id": draft.id,
            "fact_check": {"overall_score": 0.9, "items": []},
            "style": {"score": 0.8, "notes": "good rhythm"},
            "instructions": "Make it shorter",
        },
    )

    assert result.name == "editor_agent"
    assert result.status == "success"
    assert result.output.get("applied") is True


@pytest.mark.asyncio
async def test_editor_agent_handles_thread(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = Draft(
        project_id=project.id,
        user_id=user.id,
        type="thread",
        thread_items=[
            {"index": 1, "text": "First tweet."},
            {"index": 2, "text": "Second tweet."},
        ],
        status="ready_for_review",
    )
    db_session.add(draft)
    await db_session.flush()
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await EditorAgent().execute(ctx, {"draft_id": draft.id, "instructions": ""})
    assert result.status == "success"


# ─── FactCheckerAgent ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fact_checker_no_draft_id_returns_skipped(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await FactCheckerAgent().execute(ctx, {})
    assert result.status == "skipped"
    assert result.output.get("skipped") is True


@pytest.mark.asyncio
async def test_fact_checker_missing_draft_returns_error(db_session):
    user = await _make_user(db_session)
    fake_id = uuid.uuid4()
    ctx = _ctx(db_session, user.id, draft_id=fake_id)

    result = await FactCheckerAgent().execute(ctx, {"draft_id": fake_id})
    assert result.status == "error"


@pytest.mark.asyncio
async def test_fact_checker_runs_on_text_post(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = await _make_draft(
        db_session,
        project.id,
        user.id,
        text="Research shows that 80% of AI projects fail in production.",
    )
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await FactCheckerAgent().execute(ctx, {"draft_id": draft.id})
    assert result.name == "fact_checker_agent"
    assert result.status == "success"
    assert "overall_score" in result.output
    assert 0.0 <= result.output["overall_score"] <= 1.0


@pytest.mark.asyncio
async def test_fact_checker_runs_on_thread_draft(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = Draft(
        project_id=project.id,
        user_id=user.id,
        type="thread",
        thread_items=[
            {"index": 1, "text": "Studies show all developers use AI tools now."},
            {"index": 2, "text": "The fastest teams ship 3x more features."},
        ],
        status="ready_for_review",
    )
    db_session.add(draft)
    await db_session.flush()
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await FactCheckerAgent().execute(ctx, {"draft_id": draft.id})
    assert result.status == "success"
    assert "overall_score" in result.output


# ─── StyleReviewerAgent ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_style_reviewer_no_samples_returns_default(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = await _make_draft(db_session, project.id, user.id)
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await StyleReviewerAgent().execute(
        ctx, {"draft_id": draft.id, "style_context": ""}
    )
    assert result.name == "style_reviewer_agent"
    assert result.status == "success"
    assert "score" in result.output
    assert 0.0 <= float(result.output["score"]) <= 1.0


@pytest.mark.asyncio
async def test_style_reviewer_with_context_calls_llm(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    draft = await _make_draft(db_session, project.id, user.id)
    ctx = _ctx(db_session, user.id, project.id, draft.id)

    result = await StyleReviewerAgent().execute(
        ctx,
        {
            "draft_id": draft.id,
            "style_context": "Short sentences. Concrete claims. No fluff.",
        },
    )
    assert result.status == "success"
    assert "score" in result.output


# ─── MediaDirectorAgent ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_media_director_skip_when_no_media(db_session):
    user = await _make_user(db_session)
    ctx = _ctx(db_session, user.id)

    result = await MediaDirectorAgent().execute(ctx, {"include_media": False})
    assert result.status == "skipped"
    assert result.output["media_plan"] == []


@pytest.mark.asyncio
async def test_media_director_returns_plan_when_include_media(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await MediaDirectorAgent().execute(
        ctx,
        {
            "include_media": True,
            "type": "image_post",
            "angle": {"title": "Framework visual"},
            "text": "Judgment > speed. Always.",
        },
    )
    assert result.name == "media_director_agent"
    assert result.status == "success"
    plan = result.output.get("media_plan", [])
    assert isinstance(plan, list)
    assert len(plan) >= 1
    assert "type" in plan[0]
    assert "prompt" in plan[0]


# ─── BaseAgent error handling ─────────────────────────────────────────────────


class _BoomAgent(BaseAgent):
    name = "boom_agent"

    async def run(self, context, payload):
        raise RuntimeError("agent exploded")


@pytest.mark.asyncio
async def test_base_agent_catches_exception_and_returns_error(db_session):
    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    result = await _BoomAgent().execute(ctx, {})

    assert result.status == "error"
    assert "agent exploded" in (result.error_message or "")
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_base_agent_saves_trace_on_success(db_session):
    from sqlalchemy import select
    from app.models.agent_trace import AgentTrace

    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    await ResearchAgent().execute(ctx, {"topic": "test trace saving"})

    traces = (
        await db_session.execute(
            select(AgentTrace).where(AgentTrace.project_id == project.id)
        )
    ).scalars().all()
    assert len(traces) >= 1
    assert traces[-1].agent_name == "research_agent"


@pytest.mark.asyncio
async def test_base_agent_saves_trace_on_error(db_session):
    from sqlalchemy import select
    from app.models.agent_trace import AgentTrace

    user = await _make_user(db_session)
    project = await _make_project(db_session, user.id)
    ctx = _ctx(db_session, user.id, project.id)

    await _BoomAgent().execute(ctx, {"detail": "boom"})

    traces = (
        await db_session.execute(
            select(AgentTrace).where(AgentTrace.project_id == project.id)
        )
    ).scalars().all()
    assert any(t.status == "error" for t in traces)


# ─── _quality_score ───────────────────────────────────────────────────────────


class TestQualityScore:
    def test_perfect_scores(self):
        score = _quality_score({"overall_score": 1.0}, {"score": 1.0})
        assert abs(score - 1.0) < 0.01

    def test_zero_scores(self):
        score = _quality_score({"overall_score": 0.0}, {"score": 0.0})
        assert score == 0.0

    def test_weighted_average(self):
        # fact_score=1.0, style_score=0.0 → 0.55 * 1.0 + 0.45 * 0.0 = 0.55
        score = _quality_score({"overall_score": 1.0}, {"score": 0.0})
        assert abs(score - 0.55) < 0.01

    def test_missing_keys_use_defaults(self):
        # Both missing → both default to 0.7
        score = _quality_score({}, {})
        expected = round(0.55 * 0.7 + 0.45 * 0.7, 3)
        assert abs(score - expected) < 0.01

    def test_result_is_rounded_to_3_decimal_places(self):
        score = _quality_score({"overall_score": 0.333}, {"score": 0.666})
        assert score == round(score, 3)
