from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.parse import urlencode, urljoin

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .config import SourceConfig
from .models import RawItem, Query


@dataclass
class FetchResult:
    items: list[RawItem]
    errors: list[str]


def _safe_parse_time(value: str | None, time_format: str | None = None) -> datetime | None:
    if not value:
        return None
    try:
        if time_format:
            return datetime.strptime(value, time_format)
        return date_parser.parse(value)
    except (ValueError, TypeError):
        return None


def _normalize_url(link: str, base_url: str | None) -> str:
    if base_url:
        return urljoin(base_url, link)
    return link


def fetch_rss(source: SourceConfig, query: Query) -> FetchResult:
    parsed = feedparser.parse(source.url)
    items: list[RawItem] = []
    for entry in parsed.entries:
        title = entry.get("title", "").strip()
        summary = entry.get("summary", "").strip()
        link = entry.get("link", "").strip()
        published = entry.get("published", None) or entry.get("updated", None)
        published_at = _safe_parse_time(published)
        if not title or not link:
            continue
        items.append(
            RawItem(
                title=title,
                url=link,
                source=source.name,
                published_at=published_at,
                summary=summary,
            )
        )
    return FetchResult(items=items, errors=[])


def fetch_html(source: SourceConfig, query: Query) -> FetchResult:
    if not source.item_selector:
        return FetchResult(items=[], errors=[f"Missing item_selector for {source.name}"])
    params = {}
    if source.search_param:
        params[source.search_param] = query.raw
    url = source.url
    if params:
        url = f"{url}?{urlencode(params)}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    for item in soup.select(source.item_selector):
        title_element = item.select_one(source.title_selector) if source.title_selector else None
        link_element = item.select_one(source.link_selector) if source.link_selector else None
        summary_element = (
            item.select_one(source.summary_selector) if source.summary_selector else None
        )
        time_element = item.select_one(source.time_selector) if source.time_selector else None
        title = title_element.get_text(strip=True) if title_element else ""
        link = link_element.get("href") if link_element else ""
        summary = summary_element.get_text(strip=True) if summary_element else ""
        published_raw = time_element.get_text(strip=True) if time_element else None
        published_at = _safe_parse_time(published_raw, source.time_format)
        if not title or not link:
            continue
        items.append(
            RawItem(
                title=title,
                url=_normalize_url(link, source.base_url),
                source=source.name,
                published_at=published_at,
                summary=summary,
            )
        )
    return FetchResult(items=items, errors=[])


def fetch_from_sources(sources: Iterable[SourceConfig], query: Query) -> FetchResult:
    items: list[RawItem] = []
    errors: list[str] = []
    for source in sources:
        try:
            if source.type == "rss":
                result = fetch_rss(source, query)
            elif source.type == "html":
                result = fetch_html(source, query)
            else:
                errors.append(f"Unsupported source type {source.type} for {source.name}")
                continue
            items.extend(result.items)
            errors.extend(result.errors)
        except requests.RequestException as exc:
            errors.append(f"{source.name}: {exc}")
    return FetchResult(items=items, errors=errors)
