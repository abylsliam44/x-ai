import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, NotFoundError, ProviderError
from app.core.logging import get_logger
from app.core.redis import get_redis
from app.core.security import (
    decrypt_secret,
    encrypt_secret,
    generate_pkce_pair,
    generate_state_token,
)
from app.models.x_account import XAccount
from app.models.draft import Draft
from app.models.media_asset import MediaAsset

logger = get_logger(__name__)

OAUTH_STATE_PREFIX = "x_oauth_state:"
OAUTH_STATE_TTL_SECONDS = 600


class XService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def begin_connect(self, user_id: uuid.UUID) -> tuple[str, str]:
        state = generate_state_token()
        verifier, challenge = generate_pkce_pair()
        redis = get_redis()
        await redis.setex(
            OAUTH_STATE_PREFIX + state,
            OAUTH_STATE_TTL_SECONDS,
            f"{user_id}:{verifier}",
        )

        if settings.MOCK_MODE or not settings.ENABLE_REAL_X_API:
            url = (
                f"{settings.X_REDIRECT_URI}?state={state}&code=mock_authorization_code&mock=1"
            )
            return url, state

        scopes = "%20".join(settings.X_SCOPES)
        url = (
            f"{settings.X_OAUTH_BASE_URL}"
            f"?response_type=code"
            f"&client_id={settings.X_CLIENT_ID}"
            f"&redirect_uri={settings.X_REDIRECT_URI}"
            f"&scope={scopes}"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )
        return url, state

    async def complete_callback(self, code: str, state: str) -> XAccount:
        redis = get_redis()
        stored = await redis.get(OAUTH_STATE_PREFIX + state)
        if not stored:
            raise ConflictError("Invalid or expired OAuth state")
        await redis.delete(OAUTH_STATE_PREFIX + state)
        user_id_str, verifier = stored.split(":", 1)
        user_id = uuid.UUID(user_id_str)

        if settings.MOCK_MODE or not settings.ENABLE_REAL_X_API:
            payload = {
                "access_token": "mock_access_token_" + uuid.uuid4().hex,
                "refresh_token": "mock_refresh_token_" + uuid.uuid4().hex,
                "expires_in": 7200,
                "x_user_id": "mock_x_user_" + uuid.uuid4().hex[:10],
                "username": "mock_user_" + uuid.uuid4().hex[:6],
            }
        else:
            payload = await self._exchange_code(code, verifier)
            me = await self._fetch_me(payload["access_token"])
            payload["x_user_id"] = me.get("id", "unknown")
            payload["username"] = me.get("username", "unknown")

        expires_at = datetime.now(timezone.utc).replace(microsecond=0)
        expires_in = int(payload.get("expires_in", 7200))
        from datetime import timedelta

        expires_at = expires_at + timedelta(seconds=expires_in)

        existing = await self._get_account(user_id)
        if existing:
            existing.x_user_id = payload["x_user_id"]
            existing.username = payload["username"]
            existing.encrypted_access_token = encrypt_secret(payload["access_token"])
            if payload.get("refresh_token"):
                existing.encrypted_refresh_token = encrypt_secret(payload["refresh_token"])
            existing.token_expires_at = expires_at
            existing.scopes = settings.X_SCOPES
            await self.session.flush()
            return existing

        account = XAccount(
            user_id=user_id,
            x_user_id=payload["x_user_id"],
            username=payload["username"],
            encrypted_access_token=encrypt_secret(payload["access_token"]),
            encrypted_refresh_token=(
                encrypt_secret(payload["refresh_token"]) if payload.get("refresh_token") else None
            ),
            token_expires_at=expires_at,
            scopes=settings.X_SCOPES,
        )
        self.session.add(account)
        await self.session.flush()
        return account

    async def get_status(self, user_id: uuid.UUID) -> Optional[XAccount]:
        return await self._get_account(user_id)

    async def disconnect(self, user_id: uuid.UUID) -> None:
        account = await self._get_account(user_id)
        if not account:
            raise NotFoundError("No connected X account")
        await self.session.delete(account)

    async def publish_draft(self, draft: Draft, media: list[MediaAsset]) -> dict[str, Any]:
        account = await self._get_account(draft.user_id)
        if not account:
            raise ConflictError("X account is not connected for this user")

        if settings.MOCK_MODE or not settings.ENABLE_REAL_X_API:
            return {
                "mock": True,
                "x_post_id": f"mock_post_{uuid.uuid4().hex[:18]}",
                "type": draft.type,
                "thread_count": len(draft.thread_items or []) if draft.type == "thread" else None,
                "media_count": len(media),
                "uploaded_media_ids": [f"mock_media_{i}" for i in range(len(media))],
            }

        access_token = decrypt_secret(account.encrypted_access_token)
        uploaded_media_ids = await self._upload_media(access_token, media)
        if draft.type == "thread" and draft.thread_items:
            return await self._publish_thread(access_token, draft.thread_items, uploaded_media_ids)
        return await self._publish_text(access_token, draft.text or "", uploaded_media_ids)

    async def _get_account(self, user_id: uuid.UUID) -> Optional[XAccount]:
        stmt = select(XAccount).where(XAccount.user_id == user_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def _exchange_code(self, code: str, verifier: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                settings.X_TOKEN_URL,
                data={
                    "code": code,
                    "grant_type": "authorization_code",
                    "client_id": settings.X_CLIENT_ID,
                    "redirect_uri": settings.X_REDIRECT_URI,
                    "code_verifier": verifier,
                },
                auth=(settings.X_CLIENT_ID or "", settings.X_CLIENT_SECRET or ""),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
        if response.status_code >= 400:
            raise ProviderError(f"X token exchange failed: {response.text}")
        return response.json()

    async def _fetch_me(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{settings.X_API_BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        if response.status_code >= 400:
            raise ProviderError(f"X /users/me failed: {response.text}")
        return response.json().get("data", {})

    async def _upload_media(self, access_token: str, media: list[MediaAsset]) -> list[str]:
        if not media:
            return []
        raise ProviderError(
            "Real X media upload is not wired in this MVP build. "
            "Implement the multi-part upload flow against the X media endpoints."
        )

    async def _publish_text(
        self, access_token: str, text: str, media_ids: list[str]
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"text": text}
        if media_ids:
            payload["media"] = {"media_ids": media_ids}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{settings.X_API_BASE_URL}/tweets",
                headers={"Authorization": f"Bearer {access_token}"},
                json=payload,
            )
        if response.status_code >= 400:
            raise ProviderError(f"X tweet failed: {response.text}")
        data = response.json().get("data", {})
        return {"x_post_id": data.get("id"), "type": "text"}

    async def _publish_thread(
        self, access_token: str, thread_items: list[dict[str, Any]], media_ids: list[str]
    ) -> dict[str, Any]:
        last_id: Optional[str] = None
        all_ids: list[str] = []
        for idx, item in enumerate(thread_items):
            text = item.get("text") or ""
            payload: dict[str, Any] = {"text": text}
            if idx == 0 and media_ids:
                payload["media"] = {"media_ids": media_ids}
            if last_id:
                payload["reply"] = {"in_reply_to_tweet_id": last_id}
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{settings.X_API_BASE_URL}/tweets",
                    headers={"Authorization": f"Bearer {access_token}"},
                    json=payload,
                )
            if response.status_code >= 400:
                raise ProviderError(f"X thread item {idx} failed: {response.text}")
            data = response.json().get("data", {})
            last_id = data.get("id")
            if last_id:
                all_ids.append(last_id)
        return {"x_post_id": all_ids[0] if all_ids else None, "thread_ids": all_ids, "type": "thread"}
