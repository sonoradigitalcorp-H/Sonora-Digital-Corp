"""Mock tests for TikTok collector."""
from unittest.mock import patch
from scrapers.collectors.tiktok import fetch_artist


def test_fetch_no_playwright():
    with patch("builtins.__import__", side_effect=ImportError("No playwright")):
        with patch("scrapers.collectors.tiktok.log.warning") as mock_log:
            r = fetch_artist("tiktok")
            assert r is None


@patch("playwright.sync_api.sync_playwright")
def test_fetch_with_html(mock_pw):
    from unittest.mock import MagicMock
    mock_page = MagicMock()
    mock_page.content.return_value = '<html><body><script type="application/ld+json">{"name":"TikTok","description":"Video platform","interactionStatistic":[{"interactionType":"FollowAction","userInteractionCount":94600000}]}</script></body></html>'
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

    r = fetch_artist("tiktok")
    assert r is not None
