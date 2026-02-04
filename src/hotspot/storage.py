from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .models import Item


@dataclass
class Storage:
    path: Path

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source TEXT NOT NULL,
                    published_at TEXT,
                    summary TEXT,
                    keywords TEXT,
                    score REAL NOT NULL
                )
                """
            )
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_items_url ON items(url)"
            )

    def insert_items(self, items: list[Item]) -> None:
        with self.connect() as conn:
            for item in items:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO items
                    (title, url, source, published_at, summary, keywords, score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        item.title,
                        item.url,
                        item.source,
                        item.published_at.isoformat() if item.published_at else None,
                        item.summary,
                        ",".join(item.keywords),
                        item.score,
                    ),
                )

    def latest(self, limit: int) -> list[Item]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT title, url, source, published_at, summary, keywords, score
                FROM items
                ORDER BY score DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        items = []
        for title, url, source, published_at, summary, keywords, score in rows:
            items.append(
                Item(
                    title=title,
                    url=url,
                    source=source,
                    published_at=datetime.fromisoformat(published_at)
                    if published_at
                    else None,
                    summary=summary,
                    keywords=tuple(keyword for keyword in (keywords or "").split(",") if keyword),
                    score=score,
                )
            )
        return items
