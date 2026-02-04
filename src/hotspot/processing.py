from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from pathlib import Path

import jieba

from .models import Item, Query, RawItem

STOPWORDS_PATH = Path("data/stopwords.txt")


def load_stopwords(path: Path | None = None) -> set[str]:
    stopwords_path = path or STOPWORDS_PATH
    if not stopwords_path.exists():
        return set()
    return {
        line.strip()
        for line in stopwords_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def tokenize(text: str, stopwords: set[str]) -> tuple[str, ...]:
    text = re.sub(r"\s+", " ", text)
    tokens = [token.strip() for token in jieba.cut(text) if token.strip()]
    filtered = [token for token in tokens if token not in stopwords]
    return tuple(filtered)


def build_query(raw: str, stopwords: set[str]) -> Query:
    return Query(raw=raw, tokens=tokenize(raw, stopwords))


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not (key.startswith("utm_") or key == "spm")
    ]
    query = urlencode(filtered_query, doseq=True)
    return urlunparse(parsed._replace(query=query))


def _token_set(text: str, stopwords: set[str]) -> set[str]:
    return set(tokenize(text, stopwords))


def is_similar(a: str, b: str, stopwords: set[str], threshold: float = 0.7) -> bool:
    set_a = _token_set(a, stopwords)
    set_b = _token_set(b, stopwords)
    if not set_a or not set_b:
        return False
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return (intersection / union) >= threshold


def relevance_score(item: RawItem, query: Query, stopwords: set[str]) -> float:
    title_tokens = tokenize(item.title, stopwords)
    summary_tokens = tokenize(item.summary, stopwords)
    query_set = query.token_set
    title_hits = len(query_set & set(title_tokens))
    summary_hits = len(query_set & set(summary_tokens))
    return title_hits * 2.0 + summary_hits * 1.0


def recency_boost(published_at: datetime | None) -> float:
    if not published_at:
        return 0.0
    now = datetime.now(timezone.utc)
    if published_at.tzinfo is None:
        published_at = published_at.replace(tzinfo=timezone.utc)
    age_hours = max((now - published_at).total_seconds() / 3600, 0.0)
    return math.exp(-age_hours / 24)


def build_item(item: RawItem, query: Query, stopwords: set[str]) -> Item:
    score = relevance_score(item, query, stopwords) + recency_boost(item.published_at)
    keywords = tuple(token for token in tokenize(item.title, stopwords)[:8])
    return Item(
        title=item.title,
        url=item.url,
        source=item.source,
        published_at=item.published_at,
        summary=item.summary,
        keywords=keywords,
        score=score,
    )
