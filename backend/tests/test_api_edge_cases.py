"""
Edge-case tests for API endpoints.

Covers error paths, authorization guards, 404 / 409 / 401 responses,
and additional workflows not exercised by the main integration tests.
"""
import pytest


# ─── helpers ─────────────────────────────────────────────────────────────────


async def _register(client, email: str = "edge@example.com", password: str = "pass1234") -> str:
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert r.status_code == 201, r.text
    return r.json()["access_token"]


async def _auth(client, email: str = "edge@example.com") -> dict:
    token = await _register(client, email)
    return {"Authorization": f"Bearer {token}"}


async def _create_project(client, headers: dict, *, topic: str = "AI") -> dict:
    r = await client.post(
        "/api/v1/projects",
        json={"title": "Test", "topic": topic},
        headers=headers,
    )
    assert r.status_code == 201, r.text
    return r.json()


async def _generate_draft(client, headers: dict, project_id: str, *, draft_type: str = "text_post") -> dict:
    r = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": draft_type},
        headers=headers,
    )
    assert r.status_code == 200, r.text
    return r.json()


async def _connect_x(client, headers: dict) -> None:
    r = await client.get("/api/v1/x/connect", headers=headers)
    assert r.status_code == 200, r.text
    state = r.json()["state"]
    cb = await client.get(
        "/api/v1/x/callback",
        params={"code": "mock_authorization_code", "state": state},
    )
    assert cb.status_code == 200, cb.text


# ─── Auth edge cases ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dup@example.com", "password": "pass1234"}
    r1 = await client.post("/api/v1/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = await client.post("/api/v1/auth/register", json=payload)
    assert r2.status_code == 409


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client):
    await _register(client, "wrongpw@example.com", "correct_password")

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "wrong_password"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_email_returns_401(client):
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "whatever"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token_returns_401(client):
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_garbage_token_returns_401(client):
    r = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not.a.valid.token"},
    )
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_register_response_has_required_fields(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "fields@example.com", "password": "pass1234"},
    )
    body = r.json()
    assert "access_token" in body
    assert "expires_in" in body


# ─── Project edge cases ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_project_not_found_returns_404(client):
    headers = await _auth(client, "proj404@example.com")
    import uuid
    r = await client.get(f"/api/v1/projects/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_other_user_cannot_access_project(client):
    h1 = await _auth(client, "owner@example.com")
    project = await _create_project(client, h1)

    h2 = await _auth(client, "intruder@example.com")
    r = await client.get(f"/api/v1/projects/{project['id']}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_list_projects_empty_returns_zero(client):
    headers = await _auth(client, "emptyprojects@example.com")
    r = await client.get("/api/v1/projects", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["items"] == []


@pytest.mark.asyncio
async def test_list_projects_returns_only_own(client):
    h1 = await _auth(client, "owner2@example.com")
    h2 = await _auth(client, "other2@example.com")

    await _create_project(client, h1, topic="owner topic")
    await _create_project(client, h2, topic="other topic")

    r = await client.get("/api/v1/projects", headers=h1)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["topic"] == "owner topic"


@pytest.mark.asyncio
async def test_project_pagination(client):
    headers = await _auth(client, "paginate@example.com")
    for i in range(5):
        await _create_project(client, headers, topic=f"topic {i}")

    r = await client.get("/api/v1/projects", params={"limit": 2, "offset": 0}, headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 5
    assert len(body["items"]) == 2

    r2 = await client.get("/api/v1/projects", params={"limit": 2, "offset": 4}, headers=headers)
    assert len(r2.json()["items"]) == 1


@pytest.mark.asyncio
async def test_update_project(client):
    headers = await _auth(client, "update@example.com")
    project = await _create_project(client, headers, topic="original")

    r = await client.patch(
        f"/api/v1/projects/{project['id']}",
        json={"title": "Updated title"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Updated title"



# ─── Draft edge cases ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_draft_not_found_returns_404(client):
    import uuid
    headers = await _auth(client, "draft404@example.com")
    r = await client.get(f"/api/v1/drafts/{uuid.uuid4()}", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_other_user_cannot_access_draft(client):
    h1 = await _auth(client, "downer@example.com")
    project = await _create_project(client, h1)
    draft = await _generate_draft(client, h1, project["id"])

    h2 = await _auth(client, "dintruder@example.com")
    r = await client.get(f"/api/v1/drafts/{draft['id']}", headers=h2)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_revise_draft_changes_text(client):
    headers = await _auth(client, "revise@example.com")
    project = await _create_project(client, headers)
    draft = await _generate_draft(client, headers, project["id"])

    r = await client.post(
        f"/api/v1/drafts/{draft['id']}/revise",
        json={"instructions": "Make it shorter and punchier"},
        headers=headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "ready_for_review"


@pytest.mark.asyncio
async def test_revise_nonexistent_draft_returns_404(client):
    import uuid
    headers = await _auth(client, "revise404@example.com")
    r = await client.post(
        f"/api/v1/drafts/{uuid.uuid4()}/revise",
        json={"instructions": "x"},
        headers=headers,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_fact_check_nonexistent_draft_returns_404(client):
    import uuid
    headers = await _auth(client, "fc404@example.com")
    r = await client.post(f"/api/v1/drafts/{uuid.uuid4()}/fact-check", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_approve_and_get_draft_reflects_status(client):
    headers = await _auth(client, "appvget@example.com")
    project = await _create_project(client, headers)
    draft = await _generate_draft(client, headers, project["id"])

    approve = await client.post(
        f"/api/v1/drafts/{draft['id']}/approve",
        json={},
        headers=headers,
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    get = await client.get(f"/api/v1/drafts/{draft['id']}", headers=headers)
    assert get.status_code == 200
    assert get.json()["status"] == "approved"


# ─── X OAuth edge cases ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_x_status_not_connected_before_connect(client):
    headers = await _auth(client, "xstatus@example.com")
    r = await client.get("/api/v1/x/status", headers=headers)
    assert r.status_code == 200
    assert r.json()["connected"] is False


@pytest.mark.asyncio
async def test_x_disconnect_clears_connection(client):
    headers = await _auth(client, "xdisco@example.com")
    await _connect_x(client, headers)

    status_before = await client.get("/api/v1/x/status", headers=headers)
    assert status_before.json()["connected"] is True

    disco = await client.delete("/api/v1/x/disconnect", headers=headers)
    assert disco.status_code == 204

    status_after = await client.get("/api/v1/x/status", headers=headers)
    assert status_after.json()["connected"] is False


@pytest.mark.asyncio
async def test_x_callback_invalid_state_returns_409(client):
    r = await client.get(
        "/api/v1/x/callback",
        params={"code": "some_code", "state": "totally_invalid_state_token"},
    )
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_x_connect_returns_mock_flag(client):
    headers = await _auth(client, "xmock@example.com")
    r = await client.get("/api/v1/x/connect", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["mock"] is True
    assert "state" in body
    assert "authorization_url" in body


# ─── Thread draft specific ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_thread_draft_has_thread_items(client):
    headers = await _auth(client, "threadcheck@example.com")
    project = await _create_project(client, headers, topic="AI and engineering judgment")
    draft = await _generate_draft(client, headers, project["id"], draft_type="thread")

    assert draft["type"] == "thread"
    assert isinstance(draft["thread_items"], list)
    assert len(draft["thread_items"]) >= 2


@pytest.mark.asyncio
async def test_thread_draft_can_be_published(client):
    headers = await _auth(client, "threadpub@example.com")
    project = await _create_project(client, headers)
    draft = await _generate_draft(client, headers, project["id"], draft_type="thread")
    draft_id = draft["id"]

    await client.post(f"/api/v1/drafts/{draft_id}/approve", json={}, headers=headers)
    await _connect_x(client, headers)

    r = await client.post(f"/api/v1/drafts/{draft_id}/publish", json={}, headers=headers)
    assert r.status_code == 200
    assert r.json()["status"] == "succeeded"


# ─── Agent traces ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_traces_endpoint_returns_paginated_results(client):
    headers = await _auth(client, "traces@example.com")
    project = await _create_project(client, headers)
    await _generate_draft(client, headers, project["id"])

    r = await client.get(
        f"/api/v1/projects/{project['id']}/traces",
        headers=headers,
    )
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1


@pytest.mark.asyncio
async def test_traces_project_not_found_returns_404(client):
    import uuid
    headers = await _auth(client, "tracenf@example.com")
    r = await client.get(f"/api/v1/projects/{uuid.uuid4()}/traces", headers=headers)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_traces_by_draft(client):
    headers = await _auth(client, "drafttraces@example.com")
    project = await _create_project(client, headers)
    draft = await _generate_draft(client, headers, project["id"])

    r = await client.get(f"/api/v1/traces/draft/{draft['id']}", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1


# ─── Health ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_contains_version(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert "status" in body
    assert body["status"] == "ok"


# ─── MockLLMProvider JSON branches ───────────────────────────────────────────


class TestMockLLMProviderJsonBranches:
    """Verify every JSON schema branch in MockLLMProvider._mock_json_payload."""

    @pytest.mark.asyncio
    async def test_thread_branch(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content='Return JSON {"thread_items": [...]}')],
            json_mode=True,
        )
        import json
        payload = json.loads(resp.text)
        assert "thread_items" in payload
        assert len(payload["thread_items"]) >= 2

    @pytest.mark.asyncio
    async def test_angles_branch(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content='Return JSON {"angles": [...]}')],
            json_mode=True,
        )
        import json
        payload = json.loads(resp.text)
        assert "angles" in payload
        assert len(payload["angles"]) >= 1

    @pytest.mark.asyncio
    async def test_claims_branch(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content='Return JSON {"claims": [...]}')],
            json_mode=True,
        )
        import json
        payload = json.loads(resp.text)
        assert "claims" in payload

    @pytest.mark.asyncio
    async def test_insights_branch(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content='Return JSON {"insights": [...]}')],
            json_mode=True,
        )
        import json
        payload = json.loads(resp.text)
        assert "insights" in payload

    @pytest.mark.asyncio
    async def test_media_plan_branch(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content='Return JSON {"media_plan": [...]}')],
            json_mode=True,
        )
        import json
        payload = json.loads(resp.text)
        assert "media_plan" in payload

    @pytest.mark.asyncio
    async def test_embed_returns_consistent_vectors(self):
        from app.providers.llm.mock_provider import MockLLMProvider

        provider = MockLLMProvider()
        vecs1 = await provider.embed(["hello world"])
        vecs2 = await provider.embed(["hello world"])
        assert vecs1 == vecs2  # deterministic by hash

    @pytest.mark.asyncio
    async def test_embed_different_texts_differ(self):
        from app.providers.llm.mock_provider import MockLLMProvider

        provider = MockLLMProvider()
        v1 = (await provider.embed(["alpha"]))[0]
        v2 = (await provider.embed(["beta"]))[0]
        assert v1 != v2

    @pytest.mark.asyncio
    async def test_text_mode_returns_string(self):
        from app.providers.llm.mock_provider import MockLLMProvider
        from app.providers.llm.base import Message

        provider = MockLLMProvider()
        resp = await provider.complete(
            [Message(role="user", content="What do you think?")],
            json_mode=False,
        )
        assert isinstance(resp.text, str)
        assert len(resp.text) > 0
