import uuid

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundError
from app.models.draft import Draft
from app.models.fact_check import FactCheck
from app.schemas.agents import FactCheckReportItem, FactCheckResponse

router = APIRouter(prefix="/fact-check", tags=["fact_check"])


@router.get("/draft/{draft_id}", response_model=FactCheckResponse)
async def list_fact_check_for_draft(
    draft_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(100, ge=1, le=500),
) -> FactCheckResponse:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")

    rows = (
        await session.execute(
            select(FactCheck)
            .where(FactCheck.draft_id == draft_id)
            .order_by(FactCheck.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()

    items = [
        FactCheckReportItem(
            claim=r.claim,
            verdict=r.verdict,
            confidence=r.confidence,
            evidence=r.evidence or [],
            suggested_fix=r.suggested_fix,
        )
        for r in rows
    ]
    return FactCheckResponse(
        draft_id=draft.id,
        overall_score=draft.fact_check_score or 0.0,
        items=items,
    )
