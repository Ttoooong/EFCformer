from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable


@dataclass(frozen=True)
class Item:
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    score: float = 0.0

    def with_score(self, score: float) -> "Item":
        return Item(
            title=self.title,
            url=self.url,
            source=self.source,
            published_at=self.published_at,
            summary=self.summary,
            keywords=self.keywords,
            score=score,
        )


@dataclass(frozen=True)
class RawItem:
    title: str
    url: str
    source: str
    published_at: datetime | None
    summary: str


@dataclass
class Query:
    raw: str
    tokens: tuple[str, ...]

    @property
    def token_set(self) -> set[str]:
        return set(self.tokens)

    def iter_terms(self) -> Iterable[str]:
        return (token for token in self.tokens if token)
