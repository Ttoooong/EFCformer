from datetime import datetime, timezone, timedelta

from hotspot.processing import build_query, load_stopwords, normalize_url, recency_boost, tokenize


def test_tokenize_and_build_query(tmp_path):
    stopwords_path = tmp_path / "stopwords.txt"
    stopwords_path.write_text("的\n是\n", encoding="utf-8")
    stopwords = load_stopwords(stopwords_path)
    tokens = tokenize("我 是 测试", stopwords)
    assert "是" not in tokens
    query = build_query("智能 热点", stopwords)
    assert "智能" in query.tokens


def test_recency_boost():
    now = datetime.now(timezone.utc)
    recent = recency_boost(now - timedelta(hours=1))
    older = recency_boost(now - timedelta(hours=48))
    assert recent > older


def test_normalize_url():
    url = "https://example.com/news?a=1&utm_source=test&spm=123"
    assert normalize_url(url) == "https://example.com/news?a=1"
