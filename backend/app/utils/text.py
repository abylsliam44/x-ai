import re
from collections import Counter
from typing import Iterable

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_SENTENCE_END_RE = re.compile(r"(?<=[.!?])\s+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _WORD_RE.findall(text)]


def split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = _SENTENCE_END_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def chunk_text(text: str, *, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
        if start < 0:
            start = 0
    return [c for c in chunks if c]


def bm25_like_score(query_tokens: Iterable[str], doc_tokens: list[str]) -> float:
    if not doc_tokens:
        return 0.0
    counter = Counter(doc_tokens)
    score = 0.0
    doc_len = len(doc_tokens)
    for q in query_tokens:
        tf = counter.get(q, 0)
        if tf == 0:
            continue
        score += tf / (tf + 1.5 * (0.25 + 0.75 * (doc_len / 200.0)))
    return score


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_claim_candidates(text: str) -> list[str]:
    sentences = split_sentences(text)
    candidates: list[str] = []
    for s in sentences:
        if any(ch.isdigit() for ch in s):
            candidates.append(s)
            continue
        lowered = s.lower()
        if any(kw in lowered for kw in (
            "according to", "research shows", "studies", "the majority",
            "most ", "all ", "never", "always", "first ", "largest",
            "biggest", "fastest", "best ", "proven", "data shows",
        )):
            candidates.append(s)
    if not candidates and sentences:
        candidates.append(sentences[0])
    return candidates[:6]
