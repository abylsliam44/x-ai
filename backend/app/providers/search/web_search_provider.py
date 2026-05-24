from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.providers.search.base import SearchProvider, SearchResult


def _openai_url(path: str) -> str:
    base = (settings.OPENAI_BASE_URL or "https://api.openai.com/v1").rstrip("/")
    return f"{base}{path}" if base.endswith("/v1") else f"{base}/v1{path}"


class OpenAIWebSearchProvider(SearchProvider):
    name = "openai_web_search"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        if not settings.OPENAI_API_KEY:
            raise ProviderError("OPENAI_API_KEY is required for OpenAI web search")

        payload = {
            "model": settings.OPENAI_WEB_SEARCH_MODEL,
            "input": (
                "Search the web for the user's query. Return a concise synthesis "
                "with citations from the most relevant sources.\n\n"
                f"Query: {query}"
            ),
            "tools": [
                {
                    "type": "web_search",
                    "search_context_size": settings.OPENAI_WEB_SEARCH_CONTEXT_SIZE,
                }
            ],
            "tool_choice": "required",
            "include": ["web_search_call.action.sources"],
        }
        if _supports_reasoning_effort(settings.OPENAI_WEB_SEARCH_MODEL):
            payload["reasoning"] = {"effort": settings.OPENAI_REASONING_EFFORT}
        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        if settings.OPENAI_ORG_ID:
            headers["OpenAI-Organization"] = settings.OPENAI_ORG_ID
        if settings.OPENAI_PROJECT_ID:
            headers["OpenAI-Project"] = settings.OPENAI_PROJECT_ID

        try:
            async with httpx.AsyncClient(timeout=settings.OPENAI_TIMEOUT_SECONDS) as client:
                response = await client.post(_openai_url("/responses"), json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ProviderError(f"OpenAI web search network error: {exc}") from exc

        if response.status_code >= 400:
            raise ProviderError(
                f"OpenAI web search failed ({response.status_code}): {response.text}"
            )

        data = response.json()
        return _results_from_response(data, limit=limit)


class TavilyWebSearchProvider(SearchProvider):
    name = "tavily"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        raise ProviderError(
            "Real web search is not wired in this MVP build. Implement using Tavily, Serper, or similar."
        )


def _results_from_response(data: dict[str, Any], *, limit: int) -> list[SearchResult]:
    text_blocks = _extract_text_blocks(data)
    full_text = "\n\n".join(block["text"] for block in text_blocks if block["text"]).strip()
    seen: set[str] = set()
    results: list[SearchResult] = []

    for block in text_blocks:
        text = block["text"]
        for annotation in block["annotations"]:
            citation = _extract_citation(annotation)
            if not citation:
                continue
            url = citation.get("url") or ""
            if not url or url in seen:
                continue
            seen.add(url)
            title = citation.get("title") or url
            snippet = _snippet_from_text(
                text,
                citation.get("start_index"),
                citation.get("end_index"),
            )
            results.append(
                SearchResult(
                    title=str(title),
                    url=str(url),
                    snippet=snippet or full_text[:320] or str(title),
                    source="web",
                    score=max(0.1, 1.0 - (len(results) * 0.08)),
                    raw={"provider": "openai", "annotation": annotation},
                )
            )
            if len(results) >= limit:
                return results

    if full_text and not results:
        results.append(
            SearchResult(
                title="OpenAI web search summary",
                url="",
                snippet=full_text[:500],
                source="web",
                score=0.5,
                raw={"provider": "openai", "response_id": data.get("id")},
            )
        )

    return results[:limit]


def _extract_text_blocks(data: dict[str, Any]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for output in data.get("output") or []:
        for content in output.get("content") or []:
            text = content.get("text") or content.get("output_text") or ""
            if not text:
                continue
            blocks.append(
                {
                    "text": str(text),
                    "annotations": content.get("annotations") or [],
                }
            )

    if not blocks and data.get("output_text"):
        blocks.append({"text": str(data["output_text"]), "annotations": []})

    return blocks


def _extract_citation(annotation: dict[str, Any]) -> dict[str, Any] | None:
    if annotation.get("type") != "url_citation":
        return None
    nested = annotation.get("url_citation")
    if isinstance(nested, dict):
        return nested
    return annotation


def _snippet_from_text(
    text: str,
    start_index: Any,
    end_index: Any,
) -> str:
    try:
        start = int(start_index)
        end = int(end_index)
    except (TypeError, ValueError):
        return text[:320]
    if start < 0 or end <= start or start >= len(text):
        return text[:320]
    return text[start:min(end, len(text))].strip() or text[:320]


def _supports_reasoning_effort(model: str) -> bool:
    normalized = model.lower()
    return normalized.startswith(("gpt-5", "o1", "o3", "o4"))
