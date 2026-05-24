import hashlib
import json
import random
from typing import Optional

from app.providers.llm.base import LLMProvider, LLMResponse, Message


class MockLLMProvider(LLMProvider):
    name = "mock"

    async def complete(
        self,
        messages: list[Message],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        json_mode: bool = False,
    ) -> LLMResponse:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        joined = "\n".join(m.content for m in messages)

        if json_mode:
            payload = self._mock_json_payload(joined)
            text = json.dumps(payload, ensure_ascii=False)
        else:
            text = self._mock_text(last_user)

        return LLMResponse(
            text=text,
            model=model or "mock-llm-1",
            tokens_input=max(1, len(joined) // 4),
            tokens_output=max(1, len(text) // 4),
            raw={"mock": True},
        )

    async def embed(self, texts: list[str], *, model: Optional[str] = None) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16) % (2**32)
            rng = random.Random(seed)
            vectors.append([rng.uniform(-1.0, 1.0) for _ in range(64)])
        return vectors

    @staticmethod
    def _mock_text(prompt: str) -> str:
        snippet = prompt.strip().split("\n")[0][:140]
        return (
            "The real bottleneck is not output — it is judgment.\n\n"
            f"On the topic of \"{snippet}\", the strongest move is to narrow the claim, "
            "anchor it to a specific case, and let the reader feel the constraint."
        )

    @staticmethod
    def _mock_json_payload(prompt: str) -> dict:
        # Match on the JSON schema requested in the prompt so the right branch fires
        # regardless of incidental keywords (e.g. an "angle" mentioned in context).
        if '"thread_items"' in prompt:
            return {
                "thread_items": [
                    {"index": 1, "text": "The real bottleneck in AI coding is no longer code generation. It is judgment."},
                    {"index": 2, "text": "The best engineers in 2026 will not be the fastest typists. They will be the people who can frame the problem."},
                    {"index": 3, "text": "Frame > generate > review > ship. Skip the first step and you ship noise."},
                ]
            }
        if '"claims"' in prompt:
            return {
                "claims": [
                    {
                        "claim": "AI coding tools have reduced senior engineer demand.",
                        "verdict": "weakly_supported",
                        "confidence": 0.45,
                        "evidence": [{"source": "industry_survey_2025", "summary": "Mixed signals"}],
                        "suggested_fix": "Reframe as a shift in seniority requirements rather than a reduction.",
                    }
                ]
            }
        if '"angles"' in prompt:
            return {
                "angles": [
                    {
                        "title": "Judgment is the new bottleneck",
                        "thesis": "The scarcest skill in AI-era engineering is judgment, not speed.",
                        "hook": "Code generation is solved. Knowing what to build still is not.",
                        "rationale": "Concrete, contrarian, and grounded in current developer experience.",
                    },
                    {
                        "title": "The agent is a junior engineer",
                        "thesis": "Treat AI agents like fast junior engineers: constrain, review, repeat.",
                        "hook": "Stop expecting senior output from a tireless intern.",
                        "rationale": "Reframes hype into a workable mental model.",
                    },
                    {
                        "title": "Throughput is a trap",
                        "thesis": "Optimizing for AI-driven throughput without judgment compounds technical debt.",
                        "hook": "More PRs is not more progress.",
                        "rationale": "Counterintuitive take that resonates with senior practitioners.",
                    },
                ]
            }
        if '"outline"' in prompt:
            return {
                "outline": [
                    {"section": "Hook", "beats": ["Sharp claim", "Concrete example"]},
                    {"section": "Tension", "beats": ["Why the obvious answer is wrong"]},
                    {"section": "Resolution", "beats": ["What good actually looks like"]},
                    {"section": "Takeaway", "beats": ["One memorable line"]},
                ]
            }
        if '"insights"' in prompt:
            return {
                "insights": [
                    {
                        "insight": "Code generation is becoming a commodity; engineering judgment is not.",
                        "why_it_matters": "Hiring, review, and ownership patterns reshape around judgment.",
                        "evidence_refs": ["research_agent#0"],
                    }
                ]
            }
        if '"media_plan"' in prompt:
            return {
                "media_plan": [
                    {
                        "type": "image",
                        "prompt": "Concept card: judgment is the bottleneck",
                        "aspect_ratio": "1:1",
                        "notes": "Minimal, dark background, single sharp claim",
                    }
                ]
            }
        if '"score"' in prompt and '"notes"' in prompt:
            return {"score": 0.78, "notes": "Sharp opening; trim adverbs in the middle."}
        if '"title"' in prompt and '"text"' in prompt:
            return {
                "title": "Judgment is the new bottleneck",
                "text": (
                    "Code generation is becoming a commodity. Engineering judgment is not.\n\n"
                    "The best engineers in 2026 frame the right problem, constrain the agent, "
                    "and catch the answers that are subtly wrong."
                ),
            }
        if '"text"' in prompt:
            return {
                "text": (
                    "Code generation is becoming a commodity. Engineering judgment is not.\n\n"
                    "The best engineers in 2026 frame the right problem, constrain the agent, "
                    "and catch the answers that are subtly wrong."
                )
            }
        return {"text": "Mock JSON payload"}
