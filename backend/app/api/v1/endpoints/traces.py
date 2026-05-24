import uuid

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundError
from app.models.agent_trace import AgentTrace
from app.models.draft import Draft
from app.schemas.agents import AgentTraceRead
from app.schemas.common import Page

router = APIRouter(prefix="/traces", tags=["traces"])


@router.get("/draft/{draft_id}", response_model=Page[AgentTraceRead])
async def list_for_draft(
    draft_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[AgentTraceRead]:
    draft = await session.get(Draft, draft_id)
    if not draft or draft.user_id != user.id:
        raise NotFoundError("Draft not found")
    total = (
        await session.execute(
            select(func.count()).select_from(AgentTrace).where(AgentTrace.draft_id == draft_id)
        )
    ).scalar_one()
    rows = (
        await session.execute(
            select(AgentTrace)
            .where(AgentTrace.draft_id == draft_id)
            .order_by(AgentTrace.created_at.asc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return Page(
        items=[AgentTraceRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )
