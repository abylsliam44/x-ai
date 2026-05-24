import pytest


async def _register(client):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "draft@example.com", "password": "supersecret1"},
    )
    assert response.status_code == 201
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_full_draft_flow(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    project = await client.post(
        "/api/v1/projects",
        json={"title": "AI coding judgment", "topic": "AI coding agents and judgment"},
        headers=headers,
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    angles = await client.post(
        f"/api/v1/projects/{project_id}/generate-angles",
        json={"count": 3},
        headers=headers,
    )
    assert angles.status_code == 200, angles.text
    body = angles.json()
    assert "angles" in body
    assert len(body["angles"]) >= 1

    draft = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "text_post", "include_media": False},
        headers=headers,
    )
    assert draft.status_code == 200, draft.text
    draft_id = draft.json()["id"]
    assert draft.json()["status"] == "ready_for_review"

    fact = await client.post(f"/api/v1/drafts/{draft_id}/fact-check", headers=headers)
    assert fact.status_code == 200, fact.text
    assert "overall_score" in fact.json()

    traces = await client.get(f"/api/v1/projects/{project_id}/traces", headers=headers)
    assert traces.status_code == 200
    assert traces.json()["total"] >= 4


@pytest.mark.asyncio
async def test_publish_requires_approval(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    project = await client.post(
        "/api/v1/projects",
        json={"title": "Test project", "topic": "Bottleneck shift"},
        headers=headers,
    )
    project_id = project.json()["id"]

    draft = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "text_post"},
        headers=headers,
    )
    draft_id = draft.json()["id"]

    publish_too_early = await client.post(
        f"/api/v1/drafts/{draft_id}/publish",
        json={},
        headers=headers,
    )
    assert publish_too_early.status_code == 409

    approved = await client.post(
        f"/api/v1/drafts/{draft_id}/approve",
        json={},
        headers=headers,
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    await _connect_mock_x(client, headers)

    published = await client.post(
        f"/api/v1/drafts/{draft_id}/publish",
        json={},
        headers=headers,
    )
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "succeeded"


async def _connect_mock_x(client, headers):
    connect = await client.get("/api/v1/x/connect", headers=headers)
    assert connect.status_code == 200, connect.text
    body = connect.json()
    callback = await client.get(
        "/api/v1/x/callback",
        params={"code": "mock_authorization_code", "state": body["state"]},
    )
    assert callback.status_code == 200, callback.text


@pytest.mark.asyncio
async def test_x_connect_mock(client):
    token = await _register(client)
    headers = {"Authorization": f"Bearer {token}"}

    connect = await client.get("/api/v1/x/connect", headers=headers)
    assert connect.status_code == 200, connect.text
    body = connect.json()
    assert body["mock"] is True

    callback = await client.get(
        "/api/v1/x/callback",
        params={"code": "mock_authorization_code", "state": body["state"]},
    )
    assert callback.status_code == 200, callback.text
    assert callback.json()["connected"] is True

    status = await client.get("/api/v1/x/status", headers=headers)
    assert status.status_code == 200
    assert status.json()["connected"] is True
