import uuid
from datetime import datetime, timedelta, timezone
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
from app.models.draft import Draft
from app.models.media_asset import MediaAsset
from app.services.storage_service import StorageService
from app.models.x_account import XAccount

logger = get_logger(__name__)

OAUTH_STATE_PREFIX = "x_oauth_state:"
OAUTH_STATE_TTL_SECONDS = 600

# Minimum seconds remaining before we proactively refresh the token.
_TOKEN_REFRESH_BUFFER_SECONDS = 300


class XService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # OAuth connect
    # ------------------------------------------------------------------

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
            # Return a mock callback URL so the frontend can complete the flow
            # without hitting the real X OAuth endpoint.
            url = (
                f"{settings.X_REDIRECT_URI}"
                f"?state={state}&code=mock_authorization_code&mock=1"
            )
            return url, state

        scopes = " ".join(settings.X_SCOPES)
        import urllib.parse

        encoded_scopes = urllib.parse.quote(scopes)
        url = (
            f"{settings.X_OAUTH_AUTHORIZE_URL}"
            f"?response_type=code"
            f"&client_id={settings.X_CLIENT_ID}"
            f"&redirect_uri={urllib.parse.quote(settings.X_REDIRECT_URI, safe='')}"
            f"&scope={encoded_scopes}"
            f"&state={state}"
            f"&code_challenge={challenge}"
            f"&code_challenge_method=S256"
        )
        return url, state

    async def complete_callback(self, code: str, state: str) -> XAccount:
        redis = get_redis()
        stored = await redis.get(OAUTH_STATE_PREFIX + state)
        if not stored:
            raise ConflictError("Invalid or expired OAuth state. Please reconnect your X account.")
        await redis.delete(OAUTH_STATE_PREFIX + state)

        user_id_str, verifier = stored.split(":", 1)
        user_id = uuid.UUID(user_id_str)

        if settings.MOCK_MODE or not settings.ENABLE_REAL_X_API:
            payload: dict[str, Any] = {
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

        return await self._upsert_account(user_id, payload)

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    async def get_status(self, user_id: uuid.UUID) -> Optional[XAccount]:
        return await self._get_account(user_id)

    async def disconnect(self, user_id: uuid.UUID) -> None:
        account = await self._get_account(user_id)
        if not account:
            raise NotFoundError("No connected X account")
        await self.session.delete(account)

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------

    async def publish_draft(self, draft: Draft, media: list[MediaAsset]) -> dict[str, Any]:
        account = await self._get_account(draft.user_id)
        if not account:
            raise ConflictError(
                "X account is not connected. Go to Settings → Connected Accounts."
            )

        if settings.MOCK_MODE or not settings.ENABLE_REAL_X_API:
            return {
                "mock": True,
                "x_post_id": f"mock_post_{uuid.uuid4().hex[:18]}",
                "type": draft.type,
                "thread_count": len(draft.thread_items or []) if draft.type == "thread" else None,
                "media_count": len(media),
                "uploaded_media_ids": [f"mock_media_{i}" for i in range(len(media))],
            }

        access_token = await self._get_valid_token(account)

        if media:
            if not settings.X_ENABLE_REAL_MEDIA_UPLOAD:
                raise ProviderError(
                    "Real X media upload is not enabled. "
                    "Set X_ENABLE_REAL_MEDIA_UPLOAD=true in .env to publish posts with media. "
                    "Text-only publishing is available."
                )
            uploaded_media_ids = await self._upload_media(access_token, media)
        else:
            uploaded_media_ids = []

        if draft.type == "thread" and draft.thread_items:
            return await self._publish_thread(access_token, draft.thread_items, uploaded_media_ids)
        return await self._publish_text(access_token, draft.text or "", uploaded_media_ids)

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    async def _get_valid_token(self, account: XAccount) -> str:
        """Return a valid access token, refreshing if needed."""
        if account.token_expires_at:
            expires_at = account.token_expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
            if remaining < _TOKEN_REFRESH_BUFFER_SECONDS:
                await self._refresh_token(account)

        return decrypt_secret(account.encrypted_access_token)

    async def _refresh_token(self, account: XAccount) -> None:
        if not account.encrypted_refresh_token:
            logger.warning("x.token_refresh.no_refresh_token", extra={"account_id": str(account.id)})
            return

        refresh_token = decrypt_secret(account.encrypted_refresh_token)
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    settings.X_OAUTH_TOKEN_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token,
                        "client_id": settings.X_CLIENT_ID,
                    },
                    auth=(settings.X_CLIENT_ID or "", settings.X_CLIENT_SECRET or ""),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
        except Exception as exc:
            raise ProviderError(f"X token refresh network error: {exc}") from exc

        if response.status_code >= 400:
            raise ProviderError(
                f"X token refresh failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        account.encrypted_access_token = encrypt_secret(data["access_token"])
        if data.get("refresh_token"):
            account.encrypted_refresh_token = encrypt_secret(data["refresh_token"])
        expires_in = int(data.get("expires_in", 7200))
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        await self.session.flush()
        logger.info("x.token_refresh.success", extra={"account_id": str(account.id)})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get_account(self, user_id: uuid.UUID) -> Optional[XAccount]:
        stmt = select(XAccount).where(XAccount.user_id == user_id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def _upsert_account(
        self, user_id: uuid.UUID, payload: dict[str, Any]
    ) -> XAccount:
        expires_in = int(payload.get("expires_in", 7200))
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

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

    async def _exchange_code(self, code: str, verifier: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                settings.X_OAUTH_TOKEN_URL,
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
            raise ProviderError(
                f"X token exchange failed ({response.status_code}): {response.text}"
            )
        return response.json()

    async def _fetch_me(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(
                f"{settings.X_API_BASE_URL}/users/me",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"user.fields": "id,username"},
            )
        if response.status_code >= 400:
            raise ProviderError(
                f"X /users/me failed ({response.status_code}): {response.text}"
            )
        return response.json().get("data", {})

    async def _upload_media(self, access_token: str, media: list[MediaAsset]) -> list[str]:
        """Upload media assets and return list of X media_ids."""
        uploaded: list[str] = []
        for asset in media:
            if not asset.file_url:
                logger.warning("x.media_upload.missing_file_url", extra={"asset_id": str(asset.id)})
                continue

            if asset.type in ("image", "carousel_image"):
                if not settings.X_ENABLE_REAL_IMAGE_UPLOAD:
                    raise ProviderError(
                        "Real X image upload is not enabled "
                        "(X_ENABLE_REAL_IMAGE_UPLOAD=false). "
                        "Text-only publishing is available."
                    )
                # Image upload — simple form-data upload to legacy v1.1 endpoint.
                media_id = await self._upload_image_asset(access_token, asset)
            elif asset.type in ("video", "audio", "gif"):
                if not settings.X_ENABLE_REAL_VIDEO_UPLOAD:
                    raise ProviderError(
                        "Real X video/GIF upload is not enabled "
                        "(X_ENABLE_REAL_VIDEO_UPLOAD=false). "
                        "Text-only publishing is available."
                    )
                if asset.type == "gif":
                    raise ProviderError("Real X GIF upload is not implemented in this MVP build.")
                media_id = await self._upload_video_asset_chunked(access_token, asset)
            else:
                logger.warning(
                    "x.media_upload.unsupported_type",
                    extra={"type": asset.type, "asset_id": str(asset.id)},
                )
                continue

            uploaded.append(media_id)

        return uploaded

    async def _upload_image_asset(self, access_token: str, asset: MediaAsset) -> str:
        """Upload a single image to X media upload endpoint (simple upload)."""
        if not asset.storage_key:
            raise ProviderError(f"Cannot upload image asset {asset.id}: storage_key is missing")
        data = await StorageService().get_bytes(asset.storage_key)

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://upload.twitter.com/1.1/media/upload.json",
                headers={"Authorization": f"Bearer {access_token}"},
                files={"media": (asset.storage_key or "image", data, asset.mime_type or "image/jpeg")},
            )
        if response.status_code >= 400:
            raise ProviderError(
                f"X image upload failed ({response.status_code}): {response.text}"
            )
        media_id = str(response.json()["media_id"])
        asset.x_media_id = media_id
        await self.session.flush()
        return media_id

    async def _upload_video_asset_chunked(self, access_token: str, asset: MediaAsset) -> str:
        """Chunked INIT/APPEND/FINALIZE upload for video."""
        import os

        file_path = asset.file_url.lstrip("/")
        file_size = os.path.getsize(file_path)
        mime_type = asset.mime_type or "video/mp4"
        chunk_size = 4 * 1024 * 1024  # 4 MB chunks

        headers = {"Authorization": f"Bearer {access_token}"}
        upload_url = "https://upload.twitter.com/1.1/media/upload.json"

        # INIT
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                upload_url,
                headers=headers,
                data={
                    "command": "INIT",
                    "total_bytes": str(file_size),
                    "media_type": mime_type,
                    "media_category": "tweet_video",
                },
            )
        if resp.status_code >= 400:
            raise ProviderError(f"X video upload INIT failed ({resp.status_code}): {resp.text}")
        media_id = str(resp.json()["media_id"])

        # APPEND
        import aiofiles

        segment = 0
        async with aiofiles.open(file_path, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.post(
                        upload_url,
                        headers=headers,
                        data={"command": "APPEND", "media_id": media_id, "segment_index": str(segment)},
                        files={"media": chunk},
                    )
                if resp.status_code not in (200, 204):
                    raise ProviderError(
                        f"X video upload APPEND segment {segment} failed: {resp.text}"
                    )
                segment += 1

        # FINALIZE
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                upload_url,
                headers=headers,
                data={"command": "FINALIZE", "media_id": media_id},
            )
        if resp.status_code >= 400:
            raise ProviderError(f"X video upload FINALIZE failed ({resp.status_code}): {resp.text}")

        # Wait for processing
        await self._wait_for_media_processing(access_token, media_id)

        asset.x_media_id = media_id
        await self.session.flush()
        return media_id

    async def _wait_for_media_processing(
        self, access_token: str, media_id: str, max_polls: int = 20
    ) -> None:
        """Poll X media/upload STATUS until processing_info is complete."""
        import asyncio

        headers = {"Authorization": f"Bearer {access_token}"}
        for _ in range(max_polls):
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(
                    "https://upload.twitter.com/1.1/media/upload.json",
                    headers=headers,
                    params={"command": "STATUS", "media_id": media_id},
                )
            if resp.status_code >= 400:
                raise ProviderError(f"X media STATUS failed ({resp.status_code}): {resp.text}")
            info = resp.json().get("processing_info")
            if not info:
                return
            state = info.get("state")
            if state == "succeeded":
                return
            if state == "failed":
                error = info.get("error", {})
                raise ProviderError(
                    f"X media processing failed: {error.get('message', 'unknown')}"
                )
            wait = info.get("check_after_secs", 5)
            await asyncio.sleep(wait)

        raise ProviderError("X media processing timed out after polling.")

    async def _publish_text(
        self,
        access_token: str,
        text: str,
        media_ids: list[str],
    ) -> dict[str, Any]:
        if not text.strip():
            raise ConflictError("Cannot publish empty text to X.")

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
            self._raise_x_api_error("tweet", response)

        data = response.json().get("data", {})
        logger.info("x.publish.text", extra={"x_post_id": data.get("id")})
        return {"x_post_id": data.get("id"), "type": "text"}

    async def _publish_thread(
        self,
        access_token: str,
        thread_items: list[dict[str, Any]],
        media_ids: list[str],
    ) -> dict[str, Any]:
        last_id: Optional[str] = None
        all_ids: list[str] = []
        partial_failure = False

        for idx, item in enumerate(thread_items):
            text = (item.get("text") or "").strip()
            if not text:
                logger.warning("x.thread.skip_empty_item", extra={"index": idx})
                continue

            payload: dict[str, Any] = {"text": text}
            if idx == 0 and media_ids:
                payload["media"] = {"media_ids": media_ids}
            if last_id:
                payload["reply"] = {"in_reply_to_tweet_id": last_id}

            try:
                async with httpx.AsyncClient(timeout=20) as client:
                    response = await client.post(
                        f"{settings.X_API_BASE_URL}/tweets",
                        headers={"Authorization": f"Bearer {access_token}"},
                        json=payload,
                    )
                if response.status_code >= 400:
                    self._raise_x_api_error(f"thread item {idx}", response)
                data = response.json().get("data", {})
                last_id = data.get("id")
                if last_id:
                    all_ids.append(last_id)
            except ProviderError:
                partial_failure = True
                logger.error(
                    "x.thread.item_failed",
                    extra={"index": idx, "published_so_far": len(all_ids)},
                )
                break

        result: dict[str, Any] = {
            "x_post_id": all_ids[0] if all_ids else None,
            "thread_ids": all_ids,
            "type": "thread",
            "partial": partial_failure,
        }
        if partial_failure:
            result["warning"] = (
                f"Thread partially published: {len(all_ids)}/{len(thread_items)} items sent."
            )
        return result

    @staticmethod
    def _raise_x_api_error(context: str, response: httpx.Response) -> None:
        try:
            body = response.json()
            detail = body.get("detail") or body.get("title") or str(body)
        except Exception:
            detail = response.text
        raise ProviderError(
            f"X API error while publishing {context} "
            f"({response.status_code}): {detail}"
        )
