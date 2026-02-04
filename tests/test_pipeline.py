from datetime import datetime, timezone

from hotspot.models import Query, RawItem
from hotspot.pipeline import filter_and_rank


def test_filter_and_rank():
    raw_items = [
        RawItem(
            title="智能 热点 新闻",
            url="https://example.com/a?utm_source=1",
            source="Feed",
            published_at=datetime.now(timezone.utc),
            summary="摘要",
        ),
        RawItem(
            title="无关 新闻",
            url="https://example.com/b",
            source="Feed",
            published_at=None,
            summary="其他",
        ),
    ]
    query = Query(raw="智能", tokens=("智能",))
    result = filter_and_rank(raw_items, query, stopwords=set(), min_score=1.0)
    assert result.items
    assert result.items[0].title == "智能 热点 新闻"
