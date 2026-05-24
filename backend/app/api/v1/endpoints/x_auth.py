from datetime import datetime, timezone

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.schemas.x import XCallbackResponse, XConnectResponse, XStatusResponse
from app.services.x_service import XService

router = APIRouter(prefix="/x", tags=["x"])


@router.get("/connect", response_model=XConnectResponse)
async def connect(user: CurrentUserDep, session: SessionDep) -> XConnectResponse:
    service = XService(session)
    url, state = await service.begin_connect(user.id)
    await session.commit()
    return XConnectResponse(
        authorization_url=url,
        state=state,
        mock=settings.is_mock or not settings.ENABLE_REAL_X_API,
    )


@router.get("/callback", response_model=XCallbackResponse)
async def callback(
    session: SessionDep,
    code: str = Query(...),
    state: str = Query(...),
) -> XCallbackResponse:
    service = XService(session)
    account = await service.complete_callback(code=code, state=state)
    await session.commit()
    return XCallbackResponse(
        connected=True,
        username=account.username,
        x_user_id=account.x_user_id,
    )


@router.get("/status", response_model=XStatusResponse)
async def status_endpoint(user: CurrentUserDep, session: SessionDep) -> XStatusResponse:
    service = XService(session)
    account = await service.get_status(user.id)

    real_mode = settings.ENABLE_REAL_X_API and not settings.MOCK_MODE

    if not account:
        return XStatusResponse(connected=False, real_mode=real_mode, can_publish=False)

    token_valid = True
    if account.token_expires_at:
        expires_at = account.token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        token_valid = expires_at > datetime.now(timezone.utc)

    can_publish = real_mode and token_valid

    return XStatusResponse(
        connected=True,
        account_id=account.id,
        username=account.username,
        x_user_id=account.x_user_id,
        connected_at=account.connected_at,
        scopes=account.scopes or [],
        token_expires_at=account.token_expires_at,
        real_mode=real_mode,
        can_publish=can_publish,
    )


@router.delete("/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def disconnect(user: CurrentUserDep, session: SessionDep) -> None:
    service = XService(session)
    await service.disconnect(user.id)
    await session.commit()
