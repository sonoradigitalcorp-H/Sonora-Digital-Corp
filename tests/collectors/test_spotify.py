"""Mock tests for Spotify collector (Playwright browser)."""
from unittest.mock import patch, MagicMock
from scrapers.collectors.spotify import fetch_artist


@patch("playwright.sync_api.sync_playwright")
def test_fetch_artist_with_url(mock_pw):
    mock_page = MagicMock()
    mock_page.content.return_value = '<html><div>1,028,288 monthly listener</div></html>'
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

    r = fetch_artist("https://open.spotify.com/artist/2uSJ9ywE44eIRoTMatARAy")
    assert r is not None
    assert r.get("spotify_monthly_listeners") == 1028288


@patch("playwright.sync_api.sync_playwright")
def test_fetch_artist_by_name(mock_pw):
    mock_page = MagicMock()
    mock_page.content.return_value = '<html><div>24,278 monthly listener</div></html>'
    mock_browser = MagicMock()
    mock_browser.new_page.return_value = mock_page
    mock_pw.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser

    r = fetch_artist("Jesus Urquijo")
    assert r is not None



