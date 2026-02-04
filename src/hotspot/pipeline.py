from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Item, Query, RawItem
from .processing import build_item, is_similar, normalize_url


@dataclass
class PipelineResult:
    items: list[Item]
    dropped: int


def filter_and_rank(
    raw_items: Iterable[RawItem],
    query: Query,
    stopwords: set[str],
    min_score: float = 1.0,
) -> PipelineResult:
    items: list[Item] = []
    dropped = 0
    seen_urls: set[str] = set()
    seen_texts: list[str] = []
    for raw in raw_items:
        normalized_url = normalize_url(raw.url)
        if normalized_url in seen_urls:
            dropped += 1
            continue
        normalized_raw = RawItem(
            title=raw.title,
            url=normalized_url,
            source=raw.source,
            published_at=raw.published_at,
            summary=raw.summary,
        )
        item = build_item(normalized_raw, query, stopwords)
        if item.score < min_score:
            dropped += 1
            continue
        combined_text = f"{item.title} {item.summary}"
        if any(is_similar(combined_text, existing, stopwords) for existing in seen_texts):
            dropped += 1
            continue
        seen_urls.add(normalized_url)
        seen_texts.append(combined_text)
        items.append(item)
    items.sort(key=lambda x: x.score, reverse=True)
    return PipelineResult(items=items, dropped=dropped)
