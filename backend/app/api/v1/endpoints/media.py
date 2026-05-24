import uuid

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.media_asset import MediaAsset
from app.schemas.media import (
    GenerateCarouselRequest,
    GenerateImageRequest,
    GenerateVideoRequest,
    GenerateVoiceVideoRequest,
    MediaRead,
)
from app.services.media_service import MediaService

router = APIRouter(prefix="/media", tags=["media"])


@router.get("", response_model=list[MediaRead])
async def list_media(
    user: CurrentUserDep,
    session: SessionDep,
    draft_id: uuid.UUID | None = Query(default=None),
    limit: int = Query(50, ge=1, le=100),
) -> list[MediaRead]:
    stmt = (
        select(MediaAsset)
        .where(MediaAsset.user_id == user.id)
        .order_by(MediaAsset.created_at.desc())
        .limit(limit)
    )
    if draft_id:
        stmt = stmt.where(MediaAsset.draft_id == draft_id)
    rows = (await session.execute(stmt)).scalars().all()
    return [MediaRead.model_validate(row) for row in rows]


@router.post("/generate-image", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def generate_image(
    payload: GenerateImageRequest, user: CurrentUserDep, session: SessionDep
) -> MediaRead:
    service = MediaService(session)
    asset = await service.generate_image(
        user_id=user.id,
        draft_id=payload.draft_id,
        prompt=payload.prompt,
        style=payload.style,
        aspect_ratio=payload.aspect_ratio,
    )
    await session.commit()
    await session.refresh(asset)
    return MediaRead.model_validate(asset)


@router.post("/generate-carousel", response_model=list[MediaRead], status_code=status.HTTP_201_CREATED)
async def generate_carousel(
    payload: GenerateCarouselRequest, user: CurrentUserDep, session: SessionDep
) -> list[MediaRead]:
    service = MediaService(session)
    assets = await service.generate_carousel(
        user_id=user.id,
        draft_id=payload.draft_id,
        prompts=payload.prompts,
        style=payload.style,
    )
    await session.commit()
    for asset in assets:
        await session.refresh(asset)
    return [MediaRead.model_validate(a) for a in assets]


@router.post("/generate-voice-video", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def generate_voice_video(
    payload: GenerateVoiceVideoRequest, user: CurrentUserDep, session: SessionDep
) -> MediaRead:
    service = MediaService(session)
    asset = await service.generate_voice_video(
        user_id=user.id,
        draft_id=payload.draft_id,
        script=payload.script,
        voice=payload.voice,
        background_style=payload.background_style,
    )
    await session.commit()
    await session.refresh(asset)
    return MediaRead.model_validate(asset)


@router.post("/generate-video", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def generate_video(
    payload: GenerateVideoRequest, user: CurrentUserDep, session: SessionDep
) -> MediaRead:
    service = MediaService(session)
    asset = await service.generate_video(
        user_id=user.id,
        draft_id=payload.draft_id,
        prompt=payload.prompt,
        duration_seconds=payload.duration_seconds,
    )
    await session.commit()
    await session.refresh(asset)
    return MediaRead.model_validate(asset)


@router.get("/{asset_id}", response_model=MediaRead)
async def get_media(
    asset_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> MediaRead:
    service = MediaService(session)
    asset = await service.get(asset_id, user.id)
    return MediaRead.model_validate(asset)
