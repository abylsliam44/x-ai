import uuid
from datetime import datetime

from pydantic import BaseModel


class XConnectResponse(BaseModel):
    authorization_url: str
    state: str
    mock: bool = False


class XStatusResponse(BaseModel):
    connected: bool
    account_id: uuid.UUID | None = None
    username: str | None = None
    x_user_id: str | None = None
    connected_at: datetime | None = None
    scopes: list[str] = []


class XCallbackResponse(BaseModel):
    connected: bool
    username: str
    x_user_id: str
