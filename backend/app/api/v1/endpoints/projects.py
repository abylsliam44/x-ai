import uuid

from fastapi import APIRouter, Query, status
from sqlalchemy import func, select

from app.agents import ContentWorkflow, WorkflowInput
from app.api.deps import CurrentUserDep, SessionDep
from app.core.exceptions import NotFoundError
from app.models.project import ContentProject
from app.schemas.common import Page
from app.schemas.draft import (
    AngleOption,
    DraftRead,
    GenerateAnglesRequest,
    GenerateAnglesResponse,
    GenerateDraftRequest,
)
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate, user: CurrentUserDep, session: SessionDep
) -> ProjectRead:
    project = ContentProject(
        user_id=user.id,
        title=payload.title,
        topic=payload.topic,
        goal=payload.goal,
        target_audience=payload.target_audience,
    )
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return ProjectRead.model_validate(project)


@router.get("", response_model=Page[ProjectRead])
async def list_projects(
    user: CurrentUserDep,
    session: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Page[ProjectRead]:
    total = (
        await session.execute(
            select(func.count()).select_from(ContentProject).where(ContentProject.user_id == user.id)
        )
    ).scalar_one()
    rows = (
        await session.execute(
            select(ContentProject)
            .where(ContentProject.user_id == user.id)
            .order_by(ContentProject.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return Page(
        items=[ProjectRead.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: uuid.UUID, user: CurrentUserDep, session: SessionDep
) -> ProjectRead:
    project = await session.get(ContentProject, project_id)
    if not project or project.user_id != user.id:
        raise NotFoundError("Project not found")
    return ProjectRead.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    user: CurrentUserDep,
    session: SessionDep,
) -> ProjectRead:
    project = await session.get(ContentProject, project_id)
    if not project or project.user_id != user.id:
        raise NotFoundError("Project not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(project, key, value)
    await session.commit()
    await session.refresh(project)
    return ProjectRead.model_validate(project)


@router.post("/{project_id}/generate-angles", response_model=GenerateAnglesResponse)
async def generate_angles(
    project_id: uuid.UUID,
    payload: GenerateAnglesRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> GenerateAnglesResponse:
    project = await session.get(ContentProject, project_id)
    if not project or project.user_id != user.id:
        raise NotFoundError("Project not found")

    workflow = ContentWorkflow(session)
    angles_raw, _ = await workflow.generate_angles(
        project,
        count=payload.count,
        additional_context=payload.additional_context,
    )
    await session.commit()

    angles = [_normalize_angle(a) for a in angles_raw][: payload.count]
    return GenerateAnglesResponse(angles=angles)


@router.post("/{project_id}/generate-draft", response_model=DraftRead)
async def generate_draft(
    project_id: uuid.UUID,
    payload: GenerateDraftRequest,
    user: CurrentUserDep,
    session: SessionDep,
) -> DraftRead:
    project = await session.get(ContentProject, project_id)
    if not project or project.user_id != user.id:
        raise NotFoundError("Project not found")

    workflow_input = WorkflowInput(
        project_id=project.id,
        user_id=user.id,
        content_type=payload.type,
        angle=payload.angle.model_dump() if payload.angle else None,
        additional_instructions=payload.additional_instructions,
        style_sample_ids=payload.style_sample_ids,
        source_ids=payload.source_ids,
        include_media=payload.include_media,
        media_preferences=payload.media_preferences,
    )
    workflow = ContentWorkflow(session)
    result = await workflow.generate_draft(workflow_input)
    await session.commit()
    await session.refresh(result.draft)
    return DraftRead.model_validate(result.draft)


def _normalize_angle(raw: dict) -> AngleOption:
    return AngleOption(
        title=str(raw.get("title", "Untitled angle"))[:255],
        thesis=str(raw.get("thesis", "")),
        hook=str(raw.get("hook", "")),
        rationale=str(raw.get("rationale", "")),
    )
