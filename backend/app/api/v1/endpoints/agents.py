import uuid

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundError
from app.models.agent_trace import AgentTrace
from app.models.project import ContentProject
from app.schemas.agents import AgentTraceRead
from app.schemas.common import Page

router = APIRouter(prefix="/projects", tags=["agents"])


@router.get("/{project_id}/traces", response_model=Page[AgentTraceRead])
async def list_traces(
    project_id: uuid.UUID,
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> Page[AgentTraceRead]:
    project = await session.get(ContentProject, project_id)
    if not project or project.user_id != user.id:
        raise NotFoundError("Project not found")

    total = (
        await session.execute(
            select(func.count()).select_from(AgentTrace).where(AgentTrace.project_id == project_id)
        )
    ).scalar_one()
    rows = (
        await session.execute(
            select(AgentTrace)
            .where(AgentTrace.project_id == project_id)
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
