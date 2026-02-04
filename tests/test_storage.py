from datetime import datetime, timezone

from hotspot.models import Item
from hotspot.storage import Storage


def test_storage_roundtrip(tmp_path):
    db_path = tmp_path / "test.db"
    storage = Storage(db_path)
    storage.init()
    item = Item(
        title="title",
        url="https://example.com",
        source="Feed",
        published_at=datetime.now(timezone.utc),
        summary="summary",
        keywords=("k1", "k2"),
        score=2.0,
    )
    storage.insert_items([item])
    results = storage.latest(limit=10)
    assert results
    assert results[0].url == item.url
