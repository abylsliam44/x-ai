import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class XConnectResponse(BaseModel):
    authorization_url: str
    state: str
    mock: bool = False


class XStatusResponse(BaseModel):
    connected: bool
    account_id: Optional[uuid.UUID] = None
    username: Optional[str] = None
    x_user_id: Optional[str] = None
    connected_at: Optional[datetime] = None
    scopes: list[str] = []
    token_expires_at: Optional[datetime] = None
    # True when ENABLE_REAL_X_API=true (not mock mode)
    real_mode: bool = False
    # True when connected, token is valid, and real X API is enabled
    can_publish: bool = False


class XCallbackResponse(BaseModel):
    connected: bool
    username: str
    x_user_id: str
