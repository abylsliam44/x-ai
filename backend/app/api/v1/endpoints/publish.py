import uuid

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.publish_job import PublishJob
from app.schemas.common import Page
from app.schemas.publish import PublishJobRead

router = APIRouter(prefix="/publish", tags=["publish"])


@router.get("/jobs", response_model=Page[PublishJobRead])
async def list_jobs(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[PublishJobRead]:
    total = (
        await session.execute(
            select(func.count()).select_from(PublishJob).where(PublishJob.user_id == user.id)
        )
    ).scalar_one()
    rows = (
        await session.execute(
            select(PublishJob)
            .where(PublishJob.user_id == user.id)
            .order_by(PublishJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return Page(
        items=[PublishJobRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/jobs/{job_id}", response_model=PublishJobRead)
async def get_job(
    job_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> PublishJobRead:
    job = await session.get(PublishJob, job_id)
    if not job or job.user_id != user.id:
        from app.core.exceptions import NotFoundError

        raise NotFoundError("Publish job not found")
    return PublishJobRead.model_validate(job)
