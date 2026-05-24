import base64
from types import SimpleNamespace

import pytest

from app.core.exceptions import ProviderError, ValidationError
from app.providers.search.base import SearchProvider, SearchResult
from app.services.research_service import ResearchService


class FakeResponse:
    def __init__(self, status_code=200, payload=None, content=b""):
        self.status_code = status_code
        self._payload = payload or {}
        self.content = content
        self.text = str(self._payload)

    def json(self):
        return self._payload


class FakeAsyncClient:
    post_response = FakeResponse()
    get_response = FakeResponse(content=b"")
    posts = []

    def __init__(self, *_, **__):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    async def post(self, url, **kwargs):
        self.__class__.posts.append((url, kwargs))
        return self.__class__.post_response

    async def get(self, url, **kwargs):
        _ = (url, kwargs)
        return self.__class__.get_response


def _fake_settings(**overrides):
    defaults = {
        "OPENAI_API_KEY": "sk-test",
        "OPENAI_BASE_URL": None,
        "OPENAI_ORG_ID": None,
        "OPENAI_PROJECT_ID": None,
        "OPENAI_TIMEOUT_SECONDS": 10,
        "OPENAI_WEB_SEARCH_MODEL": "gpt-5.4-mini",
        "OPENAI_WEB_SEARCH_CONTEXT_SIZE": "low",
        "OPENAI_IMAGE_MODEL": "gpt-image-2",
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


@pytest.mark.asyncio
async def test_openai_web_search_parses_and_dedupes_citations(monkeypatch):
    import app.providers.search.web_search_provider as module

    FakeAsyncClient.posts = []
    FakeAsyncClient.post_response = FakeResponse(
        payload={
            "id": "resp_123",
            "output": [
                {
                    "type": "message",
                    "content": [
                        {
                            "type": "output_text",
                            "text": "Alpha source supports this. Beta source adds nuance.",
                            "annotations": [
                                {
                                    "type": "url_citation",
                                    "url": "https://alpha.example",
                                    "title": "Alpha",
                                    "start_index": 0,
                                    "end_index": 26,
                                },
                                {
                                    "type": "url_citation",
                                    "url_citation": {
                                        "url": "https://alpha.example",
                                        "title": "Alpha duplicate",
                                        "start_index": 0,
                                        "end_index": 12,
                                    },
                                },
                                {
                                    "type": "url_citation",
                                    "url_citation": {
                                        "url": "https://beta.example",
                                        "title": "Beta",
                                        "start_index": 28,
                                        "end_index": 52,
                                    },
                                },
                            ],
                        }
                    ],
                }
            ],
        }
    )
    monkeypatch.setattr(module, "settings", _fake_settings())
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    results = await module.OpenAIWebSearchProvider().search("ai shipping", limit=5)

    assert [r.url for r in results] == ["https://alpha.example", "https://beta.example"]
    assert results[0].title == "Alpha"
    assert "Alpha source" in results[0].snippet
    assert FakeAsyncClient.posts[0][0] == "https://api.openai.com/v1/responses"


@pytest.mark.asyncio
async def test_research_service_survives_one_provider_failure():
    class FailingProvider(SearchProvider):
        name = "failing"

        async def search(self, query: str, *, limit: int = 5):
            _ = (query, limit)
            raise ProviderError("boom")

    class GoodProvider(SearchProvider):
        name = "good"

        async def search(self, query: str, *, limit: int = 5):
            _ = (query, limit)
            return [SearchResult(title="ok", url="https://ok.example", snippet="ok", score=0.9)]

    results = await ResearchService(
        web_provider=FailingProvider(),
        x_provider=GoodProvider(),
    ).research("query")

    assert len(results) == 1
    assert results[0].url == "https://ok.example"


@pytest.mark.asyncio
async def test_openai_image_provider_decodes_b64(monkeypatch):
    import app.providers.media.image_provider as module

    image_bytes = b"fake-png"
    FakeAsyncClient.post_response = FakeResponse(
        payload={"data": [{"b64_json": base64.b64encode(image_bytes).decode("ascii")}]}
    )
    monkeypatch.setattr(module, "settings", _fake_settings())
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    result = await module.OpenAIImageProvider().generate_image(
        "quote card",
        aspect_ratio="1:1",
    )

    assert result.binary == image_bytes
    assert result.mime_type == "image/png"
    assert (result.width, result.height) == (1024, 1024)


@pytest.mark.asyncio
async def test_openai_image_provider_downloads_url_fallback(monkeypatch):
    import app.providers.media.image_provider as module

    FakeAsyncClient.post_response = FakeResponse(payload={"data": [{"url": "https://img.example/1.png"}]})
    FakeAsyncClient.get_response = FakeResponse(content=b"url-image")
    monkeypatch.setattr(module, "settings", _fake_settings())
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    result = await module.OpenAIImageProvider().generate_image("visual", aspect_ratio="16:9")

    assert result.binary == b"url-image"
    assert (result.width, result.height) == (1536, 1024)


@pytest.mark.asyncio
async def test_openai_image_provider_rejects_bad_aspect(monkeypatch):
    import app.providers.media.image_provider as module

    monkeypatch.setattr(module, "settings", _fake_settings())

    with pytest.raises(ValidationError):
        await module.OpenAIImageProvider().generate_image("visual", aspect_ratio="3:2")


@pytest.mark.asyncio
async def test_x_image_upload_reads_storage_key(monkeypatch):
    import app.services.x_service as module
    from app.services.x_service import XService

    class FakeStorage:
        async def get_bytes(self, key: str) -> bytes:
            assert key == "images/test.png"
            return b"image-bytes"

    class FakeSession:
        async def flush(self):
            return None

    FakeAsyncClient.post_response = FakeResponse(payload={"media_id": 12345})
    monkeypatch.setattr(module, "StorageService", lambda: FakeStorage())
    monkeypatch.setattr(module.httpx, "AsyncClient", FakeAsyncClient)

    asset = SimpleNamespace(
        id="asset-1",
        storage_key="images/test.png",
        mime_type="image/png",
        x_media_id=None,
    )

    media_id = await XService(FakeSession())._upload_image_asset("token", asset)

    assert media_id == "12345"
    assert asset.x_media_id == "12345"
