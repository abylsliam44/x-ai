import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from app.agents import ContentWorkflow, WorkflowInput
from app.core.database import AsyncSessionLocal
from app.core.logging import configure_logging, get_logger
from app.models.draft import Draft
from app.models.publish_job import PublishJob
from app.services.fact_check_service import FactCheckService
from app.services.media_service import MediaService
from app.services.publish_service import PublishService
from app.workers.celery_app import celery_app

configure_logging()
logger = get_logger(__name__)


def _run(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        return asyncio.run_coroutine_threadsafe(coro, loop).result()
    return loop.run_until_complete(coro)


@celery_app.task(name="app.workers.tasks.generate_draft_task")
def generate_draft_task(
    project_id: str,
    user_id: str,
    content_type: str = "text_post",
    angle: dict[str, Any] | None = None,
    additional_instructions: str | None = None,
    include_media: bool = False,
) -> dict[str, Any]:
    async def _inner() -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            workflow = ContentWorkflow(session)
            result = await workflow.generate_draft(
                WorkflowInput(
                    project_id=uuid.UUID(project_id),
                    user_id=uuid.UUID(user_id),
                    content_type=content_type,
                    angle=angle,
                    additional_instructions=additional_instructions,
                    include_media=include_media,
                )
            )
            await session.commit()
            return {"draft_id": str(result.draft.id), "status": result.draft.status}

    return _run(_inner())


@celery_app.task(name="app.workers.tasks.fact_check_task")
def fact_check_task(draft_id: str) -> dict[str, Any]:
    async def _inner() -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            draft = await session.get(Draft, uuid.UUID(draft_id))
            if not draft:
                return {"error": "draft not found"}
            service = FactCheckService(session)
            report = await service.run(draft)
            await session.commit()
            return report.model_dump(mode="json")

    return _run(_inner())


@celery_app.task(name="app.workers.tasks.publish_draft_task")
def publish_draft_task(publish_job_id: str) -> dict[str, Any]:
    async def _inner() -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            service = PublishService(session)
            job = await service.execute(uuid.UUID(publish_job_id))
            await session.commit()
            return {"status": job.status, "result": job.result}

    return _run(_inner())


@celery_app.task(name="app.workers.tasks.process_scheduled_publishes")
def process_scheduled_publishes() -> dict[str, Any]:
    async def _inner() -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)
            rows = (
                await session.execute(
                    select(PublishJob).where(
                        PublishJob.status == "scheduled",
                        PublishJob.scheduled_at.is_not(None),
                        PublishJob.scheduled_at <= now,
                    )
                )
            ).scalars().all()
            executed: list[str] = []
            for job in rows:
                service = PublishService(session)
                await service.execute(job.id)
                executed.append(str(job.id))
            await session.commit()
            return {"executed": executed, "count": len(executed)}

    return _run(_inner())


@celery_app.task(name="app.workers.tasks.generate_media_task")
def generate_media_task(
    user_id: str,
    draft_id: str | None,
    kind: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    async def _inner() -> dict[str, Any]:
        async with AsyncSessionLocal() as session:
            service = MediaService(session)
            uid = uuid.UUID(user_id)
            did = uuid.UUID(draft_id) if draft_id else None
            if kind == "image":
                asset = await service.generate_image(
                    user_id=uid,
                    draft_id=did,
                    prompt=payload["prompt"],
                    style=payload.get("style"),
                    aspect_ratio=payload.get("aspect_ratio", "1:1"),
                )
            elif kind == "carousel":
                assets = await service.generate_carousel(
                    user_id=uid,
                    draft_id=did,
                    prompts=payload["prompts"],
                    style=payload.get("style"),
                )
                await session.commit()
                return {"asset_ids": [str(a.id) for a in assets]}
            elif kind == "voice_video":
                asset = await service.generate_voice_video(
                    user_id=uid,
                    draft_id=did,
                    script=payload["script"],
                    voice=payload.get("voice", "default"),
                    background_style=payload.get("background_style", "minimal"),
                )
            elif kind == "video":
                asset = await service.generate_video(
                    user_id=uid,
                    draft_id=did,
                    prompt=payload["prompt"],
                    duration_seconds=payload.get("duration_seconds", 10),
                )
            else:
                return {"error": f"unknown kind: {kind}"}
            await session.commit()
            return {"asset_id": str(asset.id)}

    return _run(_inner())
