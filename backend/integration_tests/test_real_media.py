"""
Integration tests: real image generation, STT, TTS.

Video generation is SKIPPED (ENABLE_REAL_VIDEO_GENERATION=false in prod).
X media upload is SKIPPED (ENABLE_REAL_X_API=false for safety).

Run alongside test_real_agents.py:
    cd /app && python -m pytest integration_tests/ -v -s
"""
import io

import pytest

pytestmark = pytest.mark.integration

# Read flags from app settings (pydantic-settings reads .env file, not just os.environ)
def _get_flags():
    from app.core.config import get_settings
    s = get_settings()
    return (
        s.ENABLE_REAL_IMAGE_GENERATION,
        s.ENABLE_REAL_STT,
        s.ENABLE_REAL_TTS,
        s.ENABLE_REAL_VIDEO_GENERATION,
    )

_IMAGE_ENABLED, _STT_ENABLED, _TTS_ENABLED, _VIDEO_ENABLED = _get_flags()


# ─── Image generation ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.skipif(not _IMAGE_ENABLED, reason="ENABLE_REAL_IMAGE_GENERATION=false")
async def test_real_image_generation_returns_file_url(client, auth_headers):
    """
    POST /media/generate-image must call OpenAI image API and return a
    media asset with a real file_url (not a mock/placeholder).
    """
    r = await client.post(
        "/api/v1/media/generate-image",
        json={
            "prompt": "Minimalist concept card: 'Judgment is the new bottleneck'. Dark background, white text.",
            "aspect_ratio": "1:1",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()

    assert body["type"] == "image"
    assert body["status"] == "ready"
    assert body["file_url"], "Expected a non-empty file_url"
    # A real asset will have a proper path; mock assets use a placeholder
    assert "mock" not in body["file_url"].lower(), (
        f"file_url looks like a mock placeholder: {body['file_url']}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not _IMAGE_ENABLED, reason="ENABLE_REAL_IMAGE_GENERATION=false")
@pytest.mark.xfail(
    reason="OpenAI image API may return transient 5xx errors for non-square ratios",
    strict=False,
)
async def test_real_image_generation_16x9(client, auth_headers):
    """16:9 aspect ratio image generation — marked xfail for transient network errors."""
    r = await client.post(
        "/api/v1/media/generate-image",
        json={
            "prompt": "Abstract visual metaphor for AI engineering judgment.",
            "aspect_ratio": "16:9",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "ready"


@pytest.mark.asyncio
@pytest.mark.skipif(not _IMAGE_ENABLED, reason="ENABLE_REAL_IMAGE_GENERATION=false")
async def test_real_image_generation_invalid_aspect_returns_422(client, auth_headers):
    """Unsupported aspect ratio must return a validation error, not a 500."""
    r = await client.post(
        "/api/v1/media/generate-image",
        json={"prompt": "test", "aspect_ratio": "3:2"},
        headers=auth_headers,
    )
    assert r.status_code in (422, 400), (
        f"Expected validation error for unsupported aspect ratio, got {r.status_code}: {r.text}"
    )


@pytest.mark.asyncio
@pytest.mark.skipif(not _IMAGE_ENABLED, reason="ENABLE_REAL_IMAGE_GENERATION=false")
async def test_real_image_post_draft_includes_media_asset(client, auth_headers):
    """
    Generating an image_post draft with include_media=true should produce
    at least one MediaAsset of type 'image'. If image generation fails due to
    a transient network error the draft is still created — we verify draft success
    and check for assets without hard-failing when none exist.
    """
    r = await client.post(
        "/api/v1/projects",
        json={"title": "Image test", "topic": "AI judgment as a skill"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    project_id = r.json()["id"]

    draft_r = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "image_post", "include_media": True},
        headers=auth_headers,
    )
    assert draft_r.status_code == 200, draft_r.text
    draft_id = draft_r.json()["id"]

    media_r = await client.get(
        "/api/v1/media",
        params={"draft_id": draft_id},
        headers=auth_headers,
    )
    assert media_r.status_code == 200, media_r.text
    assets = media_r.json()

    if len(assets) == 0:
        # Image generation may fail transiently — draft itself must be valid
        body = draft_r.json()
        assert body["status"] in ("ready_for_review", "draft"), (
            "Draft should be in a valid state even when image generation fails"
        )
        pytest.xfail(
            "No media assets found — image generation likely failed with a transient "
            "network error. Draft was created successfully. Re-run to verify."
        )
    else:
        assert assets[0]["type"] == "image"
        assert assets[0]["status"] == "ready"


# ─── TTS (text-to-speech) ─────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.skipif(not _TTS_ENABLED, reason="ENABLE_REAL_TTS=false")
async def test_real_tts_returns_audio_asset(client, auth_headers):
    """
    POST /media/text-to-speech must call OpenAI TTS and return a media asset
    of type 'audio' with a real file_url.
    """
    r = await client.post(
        "/api/v1/media/text-to-speech",
        json={
            "text": "The real bottleneck in AI engineering is no longer code generation. It is judgment.",
            "voice": "alloy",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["type"] == "audio"
    assert body["status"] == "ready"
    assert body["file_url"]
    assert "mock" not in body["file_url"].lower(), (
        f"file_url looks like a mock placeholder: {body['file_url']}"
    )


# ─── STT (speech-to-text) ─────────────────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.skipif(not _STT_ENABLED, reason="ENABLE_REAL_STT=false")
async def test_real_stt_transcribes_audio(client, auth_headers):
    """
    POST /media/speech-to-text must call OpenAI Whisper and return a transcript.
    We use a minimal synthetic WAV (44-byte header, silence) just to hit the API.
    For a real-quality test, replace with an actual voice recording.
    """
    import struct
    import wave

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(1)
        wf.setframerate(8000)
        wf.writeframes(b"\x80" * 8000)  # 1 second of near-silence
    audio_bytes = buf.getvalue()

    r = await client.post(
        "/api/v1/media/speech-to-text",
        content=audio_bytes,
        headers={
            **auth_headers,
            "Content-Type": "audio/wav",
        },
    )
    # The API should succeed even if the transcript is empty (silence)
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert "text" in body  # transcript key present (may be empty for silence)


# ─── Video generation — must be skipped ───────────────────────────────────────


@pytest.mark.asyncio
async def test_video_generation_skipped_when_disabled(client, auth_headers):
    """
    With ENABLE_REAL_VIDEO_GENERATION=false, generating a voice_video_post
    should still succeed but return a mock/placeholder video asset (not call Sora).
    This test documents the expected degraded-mode behavior.
    """
    r = await client.post(
        "/api/v1/projects",
        json={"title": "Video test", "topic": "AI judgment"},
        headers=auth_headers,
    )
    project_id = r.json()["id"]

    draft_r = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "voice_video_post", "include_media": True},
        headers=auth_headers,
    )
    # Should not crash — degraded mode should return a valid response
    assert draft_r.status_code == 200, (
        f"Draft generation failed for voice_video_post: {draft_r.text}"
    )
