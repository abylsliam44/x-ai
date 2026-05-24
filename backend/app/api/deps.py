import uuid
from typing import Annotated

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.models.user import User


async def get_db() -> AsyncSession:
    async for session in get_session():
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    session: SessionDep,
    authorization: str | None = Header(default=None),
) -> User:
    if not authorization:
        raise UnauthorizedError("Missing Authorization header")
    if not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Authorization must use Bearer scheme")
    token = authorization.split(" ", 1)[1].strip()
    try:
        claims = decode_token(token)
    except ValueError as exc:
        raise UnauthorizedError(str(exc)) from exc
    user_id = claims.get("sub")
    if not user_id:
        raise UnauthorizedError("Token missing subject")
    try:
        user = await session.get(User, uuid.UUID(user_id))
    except Exception as exc:
        raise UnauthorizedError("Invalid user identifier") from exc
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]
