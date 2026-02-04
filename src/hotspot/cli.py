from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from apscheduler.schedulers.blocking import BlockingScheduler

from .collectors import fetch_from_sources
from .config import DEFAULT_CONFIG_PATH, load_config
from .pipeline import filter_and_rank
from .processing import build_query, load_stopwords
from .storage import Storage


def _render_items(items: Iterable) -> str:
    lines = []
    for item in items:
        time_str = item.published_at.isoformat() if item.published_at else "未知时间"
        lines.append(f"[{item.source}] {item.title}")
        lines.append(f"  时间: {time_str}")
        lines.append(f"  链接: {item.url}")
        if item.summary:
            lines.append(f"  摘要: {item.summary}")
        lines.append(f"  关键词: {', '.join(item.keywords)}")
        lines.append(f"  分数: {item.score:.2f}")
        lines.append("")
    return "\n".join(lines)


def run_once(query_text: str, config_path: Path | None) -> str:
    config = load_config(config_path)
    stopwords = load_stopwords()
    query = build_query(query_text, stopwords)
    storage = Storage(config.database_path)
    storage.init()

    fetch_result = fetch_from_sources(config.sources, query)
    pipeline_result = filter_and_rank(fetch_result.items, query, stopwords)
    storage.insert_items(pipeline_result.items)

    output_items = pipeline_result.items[: config.max_items]
    output = _render_items(output_items)
    error_lines = "\n".join(fetch_result.errors)
    return output + (f"\n错误: {error_lines}" if error_lines else "")


def run_scheduler(query_text: str, interval_minutes: int, config_path: Path | None) -> None:
    scheduler = BlockingScheduler()

    def job() -> None:
        output = run_once(query_text, config_path)
        if output:
            print(output)

    scheduler.add_job(job, "interval", minutes=interval_minutes)
    job()
    scheduler.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="智能热点收集助手")
    parser.add_argument("query", help="关键词，例如：电动汽车 补贴")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="配置文件路径 (TOML)",
    )
    parser.add_argument("--interval", type=int, default=0, help="定时刷新间隔分钟数")
    args = parser.parse_args()

    if args.interval > 0:
        run_scheduler(args.query, args.interval, args.config)
    else:
        output = run_once(args.query, args.config)
        print(output)


if __name__ == "__main__":
    main()
