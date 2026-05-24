import uuid

from fastapi import APIRouter, status

from app.agents.base import AgentContext
from app.agents.editor_agent import EditorAgent
from app.agents.fact_checker_agent import FactCheckerAgent
from app.agents.publisher_agent import PublisherAgent
from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import ConflictError, NotFoundError
from app.models.draft import Draft
from app.schemas.agents import FactCheckResponse
from app.schemas.draft import ApproveRequest, DraftRead, ReviseRequest
from app.schemas.publish import PublishJobRead, PublishRequest
from app.services.fact_check_service import FactCheckService
from app.services.publish_service import PublishService

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.get("/{draft_id}", response_model=DraftRead)
async def get_draft(
    draft_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> DraftRead:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    return DraftRead.model_validate(draft)


@router.post("/{draft_id}/revise", response_model=DraftRead)
async def revise_draft(
    draft_id: uuid.UUID,
    payload: ReviseRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> DraftRead:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    if draft.status not in ("draft", "ready_for_review", "approved"):
        raise ConflictError(f"Draft cannot be revised in status {draft.status}")

    context = AgentContext(
        session=session,
        user_id=user.id,
        project_id=draft.project_id,
        draft_id=draft.id,
    )
    await EditorAgent().execute(
        context,
        {
            "draft_id": draft.id,
            "fact_check": {},
            "style": {},
            "instructions": payload.instructions,
        },
    )
    draft.status = "ready_for_review"
    await session.commit()
    await session.refresh(draft)
    return DraftRead.model_validate(draft)


@router.post("/{draft_id}/fact-check", response_model=FactCheckResponse)
async def fact_check_draft(
    draft_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> FactCheckResponse:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    context = AgentContext(session=session, user_id=user.id, draft_id=draft.id, project_id=draft.project_id)
    result = await FactCheckerAgent().execute(context, {"draft_id": draft.id})
    await session.commit()
    if result.status == "error":
        raise ConflictError(result.error_message or "Fact check failed")
    return FactCheckResponse(**result.output)


@router.post("/{draft_id}/approve", response_model=DraftRead)
async def approve_draft(
    draft_id: uuid.UUID,
    payload: ApproveRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> DraftRead:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    if draft.status not in ("ready_for_review", "draft"):
        raise ConflictError(f"Draft cannot be approved in status {draft.status}")
    draft.status = "approved"
    await session.commit()
    await session.refresh(draft)
    _ = payload
    return DraftRead.model_validate(draft)


@router.post("/{draft_id}/publish", response_model=PublishJobRead)
async def publish_draft(
    draft_id: uuid.UUID,
    payload: PublishRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> PublishJobRead:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    if draft.status != "approved" and draft.status != "scheduled":
        raise ConflictError(
            f"Draft must be approved before publishing (current status: {draft.status})"
        )

    publish_service = PublishService(session)
    job = await publish_service.queue(draft, scheduled_at=payload.scheduled_at)
    if not payload.scheduled_at:
        job = await publish_service.execute(job.id)
        if job.status == "failed":
            await session.commit()
            raise ConflictError(job.error_message or "Publish failed")
    await session.commit()
    await session.refresh(job)
    return PublishJobRead.model_validate(job)


@router.post("/{draft_id}/schedule-publish", response_model=PublishJobRead, status_code=status.HTTP_202_ACCEPTED)
async def schedule_publish(
    draft_id: uuid.UUID,
    payload: PublishRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> PublishJobRead:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    if not payload.scheduled_at:
        raise ConflictError("scheduled_at is required for scheduled publishing")

    context = AgentContext(session=session, user_id=user.id, draft_id=draft.id, project_id=draft.project_id)
    result = await PublisherAgent().execute(
        context,
        {"draft_id": draft.id, "scheduled_at": payload.scheduled_at.isoformat()},
    )
    await session.commit()
    if result.status == "error":
        raise ConflictError(result.error_message or "Failed to schedule publish")

    job_id_str = result.output.get("executed", {}).get("job_id")
    if job_id_str is None:
        from sqlalchemy import select

        from app.models.publish_job import PublishJob

        stmt = (
            select(PublishJob)
            .where(PublishJob.draft_id == draft.id)
            .order_by(PublishJob.created_at.desc())
            .limit(1)
        )
        job = (await session.execute(stmt)).scalar_one()
    else:
        from app.models.publish_job import PublishJob

        job = await session.get(PublishJob, uuid.UUID(job_id_str))

    return PublishJobRead.model_validate(job)
