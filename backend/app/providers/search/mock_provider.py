from app.providers.search.base import SearchProvider, SearchResult


class MockWebSearchProvider(SearchProvider):
    name = "mock_web"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        seed = query.strip()[:80] or "AI"
        return [
            SearchResult(
                title=f"State of {seed} in 2026",
                url="https://example.com/state-of-the-art-2026",
                snippet=(
                    f"Recent industry analysis on {seed}, including measured outcomes and "
                    "where the consensus view is shifting."
                ),
                published_at="2026-03-12",
                author="Industry Lab",
                source="web",
                score=0.82,
            ),
            SearchResult(
                title=f"{seed}: practitioner field notes",
                url="https://example.com/field-notes",
                snippet=(
                    f"Hands-on notes from teams shipping with {seed}; what worked, what regressed."
                ),
                published_at="2026-02-04",
                author="Practitioner Weekly",
                source="web",
                score=0.74,
            ),
            SearchResult(
                title=f"A skeptical look at {seed}",
                url="https://example.com/skeptical-view",
                snippet=(
                    f"Counterargument to the dominant narrative around {seed}, with concrete examples."
                ),
                published_at="2026-01-22",
                author="Skeptic Quarterly",
                source="web",
                score=0.66,
            ),
        ][:limit]


class MockXSearchProvider(SearchProvider):
    name = "mock_x"

    async def search(self, query: str, *, limit: int = 5) -> list[SearchResult]:
        return [
            SearchResult(
                title=f"Tweet thread: {query[:60]}",
                url="https://x.com/example/status/1",
                snippet="Sharp take from a respected practitioner on this exact question.",
                published_at="2026-04-29",
                author="@example_practitioner",
                source="x",
                score=0.71,
            ),
            SearchResult(
                title=f"Counter-thread: {query[:60]}",
                url="https://x.com/example/status/2",
                snippet="Reasoned pushback with concrete numbers and one anecdote.",
                published_at="2026-04-30",
                author="@example_skeptic",
                source="x",
                score=0.64,
            ),
        ][:limit]
