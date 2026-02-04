import feedparser

from hotspot.collectors import fetch_html, fetch_rss
from hotspot.config import SourceConfig
from hotspot.models import Query


def test_fetch_rss(monkeypatch):
    feed_xml = """
    <rss version="2.0">
      <channel>
        <title>Test Feed</title>
        <item>
          <title>智能热点新闻</title>
          <link>https://example.com/a</link>
          <description>摘要</description>
          <pubDate>Mon, 20 Jan 2025 10:00:00 GMT</pubDate>
        </item>
      </channel>
    </rss>
    """
    source = SourceConfig(name="Feed", type="rss", url="https://example.com/feed")
    parsed = feedparser.parse(feed_xml)

    def fake_parse(url):
        return parsed

    monkeypatch.setattr(feedparser, "parse", fake_parse)
    result = fetch_rss(source, Query(raw="智能", tokens=("智能",)))
    assert result.items


def test_fetch_html(monkeypatch):
    html = """
    <html><body>
      <div class="item">
        <h3>热点新闻</h3>
        <a href="/news/1">link</a>
        <p class="summary">摘要内容</p>
        <time>2025-01-02</time>
      </div>
    </body></html>
    """

    class FakeResponse:
        text = html

        def raise_for_status(self):
            return None

    def fake_get(url, timeout):
        return FakeResponse()

    monkeypatch.setattr("requests.get", fake_get)
    source = SourceConfig(
        name="HTML",
        type="html",
        url="https://example.com/search",
        item_selector=".item",
        title_selector="h3",
        link_selector="a",
        summary_selector=".summary",
        time_selector="time",
        base_url="https://example.com",
        search_param="q",
    )
    result = fetch_html(source, Query(raw="热点", tokens=("热点",)))
    assert result.items
    assert result.items[0].url == "https://example.com/news/1"
