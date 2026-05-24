import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.models.draft import Draft
from app.models.media_asset import MediaAsset
from app.models.publish_job import PublishJob
from app.services.x_service import XService


class PublishService:
    def __init__(self, session: AsyncSession, x_service: Optional[XService] = None) -> None:
        self.session = session
        self.x_service = x_service or XService(session)

    async def queue(
        self,
        draft: Draft,
        *,
        scheduled_at: Optional[datetime] = None,
    ) -> PublishJob:
        if draft.status != "approved" and draft.status != "scheduled":
            raise ConflictError(
                f"Draft must be approved before publishing (status={draft.status})"
            )

        job = PublishJob(
            draft_id=draft.id,
            user_id=draft.user_id,
            platform="x",
            status="scheduled" if scheduled_at else "queued",
            scheduled_at=scheduled_at,
        )
        if scheduled_at:
            draft.status = "scheduled"
            draft.scheduled_at = scheduled_at
        self.session.add(job)
        await self.session.flush()
        return job

    async def execute(self, job_id: uuid.UUID) -> PublishJob:
        job = await self.session.get(PublishJob, job_id)
        if not job:
            raise NotFoundError("Publish job not found")

        draft = await self.session.get(Draft, job.draft_id)
        if not draft:
            job.status = "failed"
            job.error_message = "Draft missing"
            await self.session.flush()
            return job

        media_stmt = select(MediaAsset).where(MediaAsset.draft_id == draft.id)
        media = list((await self.session.execute(media_stmt)).scalars().all())

        job.status = "running"
        job.attempts += 1
        draft.status = "publishing"
        await self.session.flush()

        try:
            result = await self.x_service.publish_draft(draft, media)
        except Exception as exc:
            job.status = "failed"
            job.error_message = str(exc)
            draft.status = "failed"
            await self.session.flush()
            return job

        job.status = "succeeded"
        job.result = result
        draft.status = "published"
        draft.published_at = datetime.now(timezone.utc)
        draft.x_post_id = result.get("x_post_id")
        await self.session.flush()
        return job
