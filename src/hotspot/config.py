from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import tomllib


@dataclass(frozen=True)
class SourceConfig:
    name: str
    type: str
    url: str
    item_selector: str | None = None
    title_selector: str | None = None
    link_selector: str | None = None
    summary_selector: str | None = None
    time_selector: str | None = None
    time_format: str | None = None
    base_url: str | None = None
    search_param: str | None = None


@dataclass(frozen=True)
class AppConfig:
    sources: tuple[SourceConfig, ...]
    database_path: Path
    max_items: int


DEFAULT_CONFIG_PATH = Path("config/sources.toml")


def _parse_source(entry: dict[str, Any]) -> SourceConfig:
    return SourceConfig(
        name=entry["name"],
        type=entry["type"],
        url=entry["url"],
        item_selector=entry.get("item_selector"),
        title_selector=entry.get("title_selector"),
        link_selector=entry.get("link_selector"),
        summary_selector=entry.get("summary_selector"),
        time_selector=entry.get("time_selector"),
        time_format=entry.get("time_format"),
        base_url=entry.get("base_url"),
        search_param=entry.get("search_param"),
    )


def load_config(path: Path | None = None) -> AppConfig:
    config_path = path or DEFAULT_CONFIG_PATH
    data = tomllib.loads(Path(config_path).read_text(encoding="utf-8"))
    sources_data = data.get("sources", [])
    sources = tuple(_parse_source(entry) for entry in sources_data)
    database_path = Path(data.get("database", {}).get("path", "hotspot.db"))
    max_items = int(data.get("output", {}).get("max_items", 50))
    return AppConfig(sources=sources, database_path=database_path, max_items=max_items)
