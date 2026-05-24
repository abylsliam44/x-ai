from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    auth,
    drafts,
    fact_check,
    health,
    media,
    projects,
    publish,
    rag,
    traces,
    users,
    x_auth,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(x_auth.router)
api_router.include_router(projects.router)
api_router.include_router(agents.router)
api_router.include_router(drafts.router)
api_router.include_router(rag.router)
api_router.include_router(media.router)
api_router.include_router(fact_check.router)
api_router.include_router(publish.router)
api_router.include_router(traces.router)
