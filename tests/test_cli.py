from datetime import datetime, timezone
from pathlib import Path

from hotspot.cli import run_once
from hotspot.models import RawItem


def test_run_once(monkeypatch, tmp_path):
    config_path = tmp_path / "sources.toml"
    config_path.write_text(
        """
        [database]
        path = "test.db"

        [output]
        max_items = 5
        """,
        encoding="utf-8",
    )

    def fake_fetch(sources, query):
        return type(
            "Result",
            (),
            {
                "items": [
                    RawItem(
                        title="智能 热点",
                        url="https://example.com",
                        source="Feed",
                        published_at=datetime.now(timezone.utc),
                        summary="摘要",
                    )
                ],
                "errors": [],
            },
        )()

    monkeypatch.setattr("hotspot.cli.fetch_from_sources", fake_fetch)
    output = run_once("智能", config_path)
    assert "智能 热点" in output
    assert (tmp_path / "test.db").exists()
