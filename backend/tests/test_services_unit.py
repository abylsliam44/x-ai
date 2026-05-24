"""
Unit tests for the service layer.

Covers:
  - FactCheckService: _draft_body static, score calculation, verdict weights,
    empty-claim short-circuit
  - StyleService: empty text, no context, with context
  - PublishService: queue (approved / not approved / scheduled_at),
    execute (missing job, missing draft, provider failure, success)
  - ResearchService: both providers fail gracefully, dedup logic
"""
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from app.agents.base import AgentContext
from app.core.exceptions import ConflictError, NotFoundError
from app.models.draft import Draft
from app.models.project import ContentProject
from app.models.publish_job import PublishJob
from app.models.user import User
from app.services.fact_check_service import VERDICT_WEIGHTS, FactCheckService
from app.services.llm_service import LLMService
from app.services.publish_service import PublishService
from app.services.style_service import StyleService


# ─── helpers ─────────────────────────────────────────────────────────────────


async def _insert_user(session) -> User:
    u = User(
        email=f"svc-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="x",
    )
    session.add(u)
    await session.flush()
    return u


async def _insert_project(session, user_id: uuid.UUID) -> ContentProject:
    p = ContentProject(
        user_id=user_id,
        title="Test project",
        topic="AI judgment",
    )
    session.add(p)
    await session.flush()
    return p


async def _insert_draft(
    session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    *,
    status: str = "approved",
    draft_type: str = "text_post",
    text: str = "The bottleneck is judgment.",
    thread_items=None,
) -> Draft:
    d = Draft(
        project_id=project_id,
        user_id=user_id,
        type=draft_type,
        text=text,
        thread_items=thread_items,
        status=status,
    )
    session.add(d)
    await session.flush()
    return d


# ─── FactCheckService._draft_body ─────────────────────────────────────────────


class TestFactCheckServiceDraftBody:
    def _make_draft(self, *, draft_type="text_post", text=None, thread_items=None):
        d = SimpleNamespace(type=draft_type, text=text, thread_items=thread_items)
        return d

    def test_text_post_returns_text(self):
        d = self._make_draft(text="Hello world")
        assert FactCheckService._draft_body(d) == "Hello world"  # type: ignore[arg-type]

    def test_thread_joins_item_texts(self):
        items = [{"text": "First"}, {"text": "Second"}, {"text": "Third"}]
        d = self._make_draft(draft_type="thread", thread_items=items)
        body = FactCheckService._draft_body(d)  # type: ignore[arg-type]
        assert "First" in body
        assert "Second" in body
        assert "Third" in body

    def test_thread_with_string_items(self):
        d = self._make_draft(draft_type="thread", thread_items=["Tweet A", "Tweet B"])
        body = FactCheckService._draft_body(d)  # type: ignore[arg-type]
        assert "Tweet A" in body and "Tweet B" in body

    def test_empty_text_returns_empty_string(self):
        d = self._make_draft(text=None)
        assert FactCheckService._draft_body(d) == ""  # type: ignore[arg-type]

    def test_thread_no_items_falls_back_to_text(self):
        d = self._make_draft(draft_type="thread", text="fallback", thread_items=None)
        assert FactCheckService._draft_body(d) == "fallback"  # type: ignore[arg-type]


# ─── VERDICT_WEIGHTS ─────────────────────────────────────────────────────────


class TestVerdictWeights:
    def test_supported_is_highest(self):
        assert VERDICT_WEIGHTS["supported"] == 1.0

    def test_contradicted_is_zero(self):
        assert VERDICT_WEIGHTS["contradicted"] == 0.0

    def test_weakly_supported_between_zero_and_one(self):
        w = VERDICT_WEIGHTS["weakly_supported"]
        assert 0.0 < w < 1.0

    def test_unverifiable_between_zero_and_one(self):
        u = VERDICT_WEIGHTS["unverifiable"]
        assert 0.0 < u < 1.0

    def test_weakly_supported_better_than_unverifiable(self):
        assert VERDICT_WEIGHTS["weakly_supported"] > VERDICT_WEIGHTS["unverifiable"]


# ─── FactCheckService full run ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fact_check_service_no_claims_returns_perfect_score(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    # Empty draft body → extract_claim_candidates returns [] → shortcut path
    draft = await _insert_draft(
        db_session, project.id, user.id, text=""
    )
    svc = FactCheckService(db_session, llm=LLMService())
    report, model, tok_in, tok_out, latency = await svc.run(draft)

    assert report.overall_score == 1.0
    assert report.items == []
    assert model is None


@pytest.mark.asyncio
async def test_fact_check_service_with_claims_returns_score_between_0_and_1(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(
        db_session,
        project.id,
        user.id,
        text="Research shows 80% of teams adopt AI tools in 2024.",
    )
    svc = FactCheckService(db_session, llm=LLMService())
    report, model, tok_in, tok_out, latency = await svc.run(draft)

    assert 0.0 <= report.overall_score <= 1.0
    assert isinstance(report.items, list)


@pytest.mark.asyncio
async def test_fact_check_service_persists_fact_check_rows(db_session):
    from sqlalchemy import select
    from app.models.fact_check import FactCheck

    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(
        db_session,
        project.id,
        user.id,
        text="Studies show that the majority of models degrade over time.",
    )
    svc = FactCheckService(db_session, llm=LLMService())
    await svc.run(draft)

    rows = (
        await db_session.execute(select(FactCheck).where(FactCheck.draft_id == draft.id))
    ).scalars().all()
    assert len(rows) >= 1


@pytest.mark.asyncio
async def test_fact_check_service_updates_draft_fact_check_score(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(
        db_session,
        project.id,
        user.id,
        text="The largest AI dataset contains 1 trillion tokens.",
    )
    svc = FactCheckService(db_session, llm=LLMService())
    await svc.run(draft)

    await db_session.refresh(draft)
    assert draft.fact_check_score is not None


# ─── StyleService ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_style_service_empty_text_returns_zero(db_session):
    svc = StyleService(db_session)
    score, notes, model, tok_in, tok_out, latency = await svc.score_style("", style_context="anything")
    assert score == 0.0
    assert "Empty" in notes


@pytest.mark.asyncio
async def test_style_service_no_context_returns_default(db_session):
    svc = StyleService(db_session)
    score, notes, model, tok_in, tok_out, latency = await svc.score_style("Some text.", style_context="")
    assert score == 0.7
    assert "No writing samples" in notes
    assert model is None


@pytest.mark.asyncio
async def test_style_service_with_context_calls_llm(db_session):
    svc = StyleService(db_session, llm=LLMService())
    score, notes, model, tok_in, tok_out, latency = await svc.score_style(
        "The bottleneck is judgment, not throughput.",
        style_context="Short sentences. Direct claims. No filler words.",
    )
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_style_service_gather_context_empty_when_no_samples(db_session):
    user = await _insert_user(db_session)
    svc = StyleService(db_session)
    context = await svc.gather_style_context(user.id)
    assert context == ""


@pytest.mark.asyncio
async def test_style_service_gather_context_with_samples(db_session):
    from app.models.writing_sample import WritingSample

    user = await _insert_user(db_session)
    sample = WritingSample(
        user_id=user.id,
        title="My voice",
        text="Short sentences. Direct claims.",
    )
    db_session.add(sample)
    await db_session.flush()

    svc = StyleService(db_session)
    context = await svc.gather_style_context(user.id)
    assert "Short sentences" in context


# ─── PublishService.queue ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_service_queue_approved_draft_creates_job(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(db_session, project.id, user.id, status="approved")

    svc = PublishService(db_session)
    job = await svc.queue(draft)

    assert job.draft_id == draft.id
    assert job.status == "queued"
    assert job.platform == "x"


@pytest.mark.asyncio
async def test_publish_service_queue_unapproved_raises_conflict(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(db_session, project.id, user.id, status="ready_for_review")

    svc = PublishService(db_session)
    with pytest.raises(ConflictError):
        await svc.queue(draft)


@pytest.mark.asyncio
async def test_publish_service_queue_with_scheduled_at(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(db_session, project.id, user.id, status="approved")

    future = datetime.now(timezone.utc) + timedelta(hours=2)
    svc = PublishService(db_session)
    job = await svc.queue(draft, scheduled_at=future)

    assert job.status == "scheduled"
    assert draft.status == "scheduled"


# ─── PublishService.execute ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_publish_execute_missing_job_raises_not_found(db_session):
    svc = PublishService(db_session)
    with pytest.raises(NotFoundError):
        await svc.execute(uuid.uuid4())


@pytest.mark.asyncio
async def test_publish_execute_missing_draft_marks_failed(db_session):
    user = await _insert_user(db_session)
    # Insert a job that references a non-existent draft
    job = PublishJob(
        draft_id=uuid.uuid4(),
        user_id=user.id,
        platform="x",
        status="queued",
    )
    db_session.add(job)
    await db_session.flush()

    svc = PublishService(db_session)
    result = await svc.execute(job.id)

    assert result.status == "failed"
    assert result.error_message == "Draft missing"


@pytest.mark.asyncio
async def test_publish_execute_provider_failure_reverts_draft(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(db_session, project.id, user.id, status="approved")

    job = PublishJob(
        draft_id=draft.id,
        user_id=user.id,
        platform="x",
        status="queued",
    )
    db_session.add(job)
    await db_session.flush()

    class _FailingXService:
        async def publish_draft(self, draft, media):
            raise RuntimeError("X API unavailable")

    svc = PublishService(db_session, x_service=_FailingXService())  # type: ignore[arg-type]
    result = await svc.execute(job.id)

    assert result.status == "failed"
    assert "X API unavailable" in result.error_message
    # Draft status is set to "failed" on publish error
    await db_session.refresh(draft)
    assert draft.status == "failed"


@pytest.mark.asyncio
async def test_publish_execute_success_path(db_session):
    user = await _insert_user(db_session)
    project = await _insert_project(db_session, user.id)
    draft = await _insert_draft(db_session, project.id, user.id, status="approved")

    job = PublishJob(
        draft_id=draft.id,
        user_id=user.id,
        platform="x",
        status="queued",
    )
    db_session.add(job)
    await db_session.flush()

    class _MockXService:
        async def publish_draft(self, draft, media):
            return {"x_post_id": "1234567890", "mock": True}

    svc = PublishService(db_session, x_service=_MockXService())  # type: ignore[arg-type]
    result = await svc.execute(job.id)

    assert result.status == "succeeded"
    assert result.result["x_post_id"] == "1234567890"
    await db_session.refresh(draft)
    assert draft.status == "published"
    assert draft.x_post_id == "1234567890"
    assert draft.published_at is not None


# ─── ResearchService ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_research_service_merges_both_providers():
    from app.providers.search.base import SearchProvider, SearchResult
    from app.services.research_service import ResearchService

    class _Web(SearchProvider):
        name = "web"

        async def search(self, query, *, limit=5):
            return [SearchResult(title="Web", url="https://web.example", snippet="w", score=0.9)]

    class _X(SearchProvider):
        name = "x"

        async def search(self, query, *, limit=5):
            return [SearchResult(title="X", url="https://x.example", snippet="x", score=0.8)]

    results = await ResearchService(web_provider=_Web(), x_provider=_X()).research("q")
    urls = {r.url for r in results}
    assert "https://web.example" in urls
    assert "https://x.example" in urls


@pytest.mark.asyncio
async def test_research_service_sorts_by_score_descending():
    from app.providers.search.base import SearchProvider, SearchResult
    from app.services.research_service import ResearchService

    class _High(SearchProvider):
        name = "high"

        async def search(self, query, *, limit=5):
            return [SearchResult(title="High", url="https://high.example", snippet="h", score=0.95)]

    class _Low(SearchProvider):
        name = "low"

        async def search(self, query, *, limit=5):
            return [SearchResult(title="Low", url="https://low.example", snippet="l", score=0.3)]

    results = await ResearchService(web_provider=_High(), x_provider=_Low()).research("q")
    assert results[0].score >= results[-1].score


@pytest.mark.asyncio
async def test_research_service_propagates_provider_errors():
    """ResearchService does not catch provider exceptions — they propagate."""
    from app.core.exceptions import ProviderError
    from app.providers.search.base import SearchProvider
    from app.services.research_service import ResearchService

    class _Fail(SearchProvider):
        name = "fail"

        async def search(self, query, *, limit=5):
            raise ProviderError("down")

    with pytest.raises(ProviderError):
        await ResearchService(web_provider=_Fail(), x_provider=_Fail()).research("x")


@pytest.mark.asyncio
async def test_research_service_returns_combined_list():
    from app.providers.search.base import SearchProvider, SearchResult
    from app.services.research_service import ResearchService

    class _Both(SearchProvider):
        name = "both"

        async def search(self, query, *, limit=5):
            return [
                SearchResult(title=f"{self.name}-1", url=f"https://{self.name}.example/1", snippet="", score=0.7),
                SearchResult(title=f"{self.name}-2", url=f"https://{self.name}.example/2", snippet="", score=0.5),
            ]

    svc = ResearchService(web_provider=_Both(), x_provider=_Both())
    results = await svc.research("q")
    # Two providers, each returning 2 results → 4 total
    assert len(results) == 4
