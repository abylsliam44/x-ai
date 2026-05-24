import pytest


@pytest.mark.asyncio
async def test_full_e2e_mock_flow(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "e2e@example.com", "password": "supersecret1", "full_name": "E2E User"},
    )
    assert register.status_code == 201, register.text
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "e2e@example.com", "password": "supersecret1"},
    )
    assert login.status_code == 200

    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "e2e@example.com"

    project = await client.post(
        "/api/v1/projects",
        json={
            "title": "Engineering judgment",
            "topic": "Why judgment is the new bottleneck in AI engineering",
            "goal": "Build authority",
            "target_audience": "Senior engineers on X",
        },
        headers=headers,
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    sample = await client.post(
        "/api/v1/rag/writing-samples",
        json={"title": "Sample voice", "text": "Short, sharp sentences. No filler. Pointed claims."},
        headers=headers,
    )
    assert sample.status_code == 201, sample.text

    source = await client.post(
        "/api/v1/rag/sources",
        json={
            "project_id": project_id,
            "source_type": "manual",
            "title": "Background note",
            "raw_text": (
                "Across teams, AI coding agents reduced implementation time "
                "but increased the importance of clear specification and review."
            ),
            "trust_level": 0.7,
        },
        headers=headers,
    )
    assert source.status_code == 201, source.text

    rag_search = await client.post(
        "/api/v1/rag/search",
        json={"query": "specification and review", "top_k": 3},
        headers=headers,
    )
    assert rag_search.status_code == 200
    assert isinstance(rag_search.json()["results"], list)

    angles = await client.post(
        f"/api/v1/projects/{project_id}/generate-angles",
        json={"count": 3},
        headers=headers,
    )
    assert angles.status_code == 200
    assert len(angles.json()["angles"]) >= 1

    draft = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "text_post", "include_media": False},
        headers=headers,
    )
    assert draft.status_code == 200, draft.text
    draft_id = draft.json()["id"]
    assert draft.json()["status"] == "ready_for_review"

    fact = await client.post(f"/api/v1/drafts/{draft_id}/fact-check", headers=headers)
    assert fact.status_code == 200
    assert "overall_score" in fact.json()

    publish_before = await client.post(
        f"/api/v1/drafts/{draft_id}/publish", json={}, headers=headers
    )
    assert publish_before.status_code == 409

    approved = await client.post(
        f"/api/v1/drafts/{draft_id}/approve", json={}, headers=headers
    )
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    connect = await client.get("/api/v1/x/connect", headers=headers)
    assert connect.status_code == 200
    state = connect.json()["state"]

    callback = await client.get(
        "/api/v1/x/callback",
        params={"code": "mock_authorization_code", "state": state},
    )
    assert callback.status_code == 200

    published = await client.post(
        f"/api/v1/drafts/{draft_id}/publish", json={}, headers=headers
    )
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "succeeded"
    assert published.json()["result"]["mock"] is True

    traces = await client.get(f"/api/v1/projects/{project_id}/traces", headers=headers)
    assert traces.status_code == 200
    trace_body = traces.json()
    assert trace_body["total"] >= 6
    names = {t["agent_name"] for t in trace_body["items"]}
    assert {"research_agent", "angle_agent", "draft_writer_agent", "fact_checker_agent"} <= names

    draft_traces = await client.get(f"/api/v1/traces/draft/{draft_id}", headers=headers)
    assert draft_traces.status_code == 200
    assert draft_traces.json()["total"] >= 1


@pytest.mark.asyncio
async def test_thread_workflow(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "thread@example.com", "password": "supersecret1"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project = await client.post(
        "/api/v1/projects",
        json={"title": "Thread topic", "topic": "Why AI demos die before becoming products"},
        headers=headers,
    )
    project_id = project.json()["id"]

    draft = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "thread", "include_media": False},
        headers=headers,
    )
    assert draft.status_code == 200, draft.text
    body = draft.json()
    assert body["type"] == "thread"
    assert isinstance(body["thread_items"], list)
    assert len(body["thread_items"]) >= 2


@pytest.mark.asyncio
async def test_image_media_generation(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "media@example.com", "password": "supersecret1"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    image = await client.post(
        "/api/v1/media/generate-image",
        json={"prompt": "Concept card: judgment > generation", "aspect_ratio": "1:1"},
        headers=headers,
    )
    assert image.status_code == 201, image.text
    asset = image.json()
    assert asset["status"] == "ready"
    assert asset["type"] == "image"
    assert asset["file_url"]

    listed = await client.get(
        "/api/v1/media",
        params={"draft_id": asset["draft_id"]} if asset["draft_id"] else {},
        headers=headers,
    )
    assert listed.status_code == 200, listed.text
    assert any(item["id"] == asset["id"] for item in listed.json())


@pytest.mark.asyncio
async def test_draft_workflow_with_media(client):
    register = await client.post(
        "/api/v1/auth/register",
        json={"email": "workflow-media@example.com", "password": "supersecret1"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    project = await client.post(
        "/api/v1/projects",
        json={"title": "Image post", "topic": "Why judgment beats generation"},
        headers=headers,
    )
    project_id = project.json()["id"]

    draft = await client.post(
        f"/api/v1/projects/{project_id}/generate-draft",
        json={"type": "image_post", "include_media": True},
        headers=headers,
    )
    assert draft.status_code == 200, draft.text
    draft_id = draft.json()["id"]

    media = await client.get("/api/v1/media", params={"draft_id": draft_id}, headers=headers)
    assert media.status_code == 200, media.text
    body = media.json()
    assert len(body) >= 1
    assert body[0]["type"] == "image"
