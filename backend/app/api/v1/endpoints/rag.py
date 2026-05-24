from fastapi import APIRouter, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentUserDep, SessionDep
from app.models.source import Source
from app.models.writing_sample import WritingSample
from app.schemas.common import Page
from app.schemas.rag import (
    RagSearchRequest,
    RagSearchResponse,
    SourceCreate,
    SourceRead,
    WritingSampleCreate,
    WritingSampleRead,
)
from app.services.rag_service import RagService

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/writing-samples",
    response_model=WritingSampleRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_writing_sample(
    payload: WritingSampleCreate,
    user: CurrentUserDep,
    session: SessionDep,
) -> WritingSampleRead:
    sample = WritingSample(
        user_id=user.id,
        title=payload.title,
        source_type=payload.source_type,
        text=payload.text,
        meta=payload.meta,
    )
    session.add(sample)
    await session.flush()

    rag = RagService(session)
    await rag.ingest_writing_sample(sample)

    await session.commit()
    await session.refresh(sample)
    return WritingSampleRead.model_validate(sample)


@router.get("/writing-samples", response_model=Page[WritingSampleRead])
async def list_writing_samples(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[WritingSampleRead]:
    total = (
        await session.execute(
            select(func.count()).select_from(WritingSample).where(WritingSample.user_id == user.id)
        )
    ).scalar_one()
    rows = (
        await session.execute(
            select(WritingSample)
            .where(WritingSample.user_id == user.id)
            .order_by(WritingSample.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return Page(
        items=[WritingSampleRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/sources", response_model=SourceRead, status_code=status.HTTP_201_CREATED)
async def create_source(
    payload: SourceCreate,
    user: CurrentUserDep,
    session: SessionDep,
) -> SourceRead:
    source = Source(
        project_id=payload.project_id,
        source_type=payload.source_type,
        title=payload.title,
        url=payload.url,
        author=payload.author,
        raw_text=payload.raw_text,
        trust_level=payload.trust_level,
        meta=payload.meta,
    )
    session.add(source)
    await session.flush()

    rag = RagService(session)
    await rag.ingest_source(source, user.id)

    await session.commit()
    await session.refresh(source)
    return SourceRead.model_validate(source)


@router.get("/sources", response_model=Page[SourceRead])
async def list_sources(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[SourceRead]:
    from app.models.project import ContentProject

    base = (
        select(Source)
        .outerjoin(ContentProject, ContentProject.id == Source.project_id)
        .where((ContentProject.user_id == user.id) | (Source.project_id.is_(None)))
    )
    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = (
        await session.execute(
            base.order_by(Source.created_at.desc()).limit(limit).offset(offset)
        )
    ).scalars().all()
    return Page(
        items=[SourceRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("/search", response_model=RagSearchResponse)
async def search(
    payload: RagSearchRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> RagSearchResponse:
    rag = RagService(session)
    results = await rag.search(
        user.id,
        payload.query,
        top_k=payload.top_k,
        include_writing_samples=payload.include_writing_samples,
        include_sources=payload.include_sources,
    )
    return RagSearchResponse(query=payload.query, results=results)


@router.get("/search", response_model=RagSearchResponse)
async def search_get(
    user: CurrentUserDep,
    session: SessionDep,
    q: str = Query(..., min_length=1),
    top_k: int = Query(6, ge=1, le=20),
) -> RagSearchResponse:
    rag = RagService(session)
    results = await rag.search(user.id, q, top_k=top_k)
    return RagSearchResponse(query=q, results=results)
