"""Mock tests for Apple Music collector."""
from unittest.mock import patch, MagicMock
from scrapers.collectors.apple_music import search_artist

MOCK_RESULT = {
    "resultCount": 1,
    "results": [{
        "artistId": 1082292215,
        "artistName": "Hector Rubio",
        "artistLinkUrl": "https://music.apple.com/us/artist/hector-rubio/1082292215",
    }]
}

def test_search_found():
    with patch("scrapers.collectors.apple_music.httpx.get") as m:
        m.return_value = MagicMock(status_code=200, json=lambda: MOCK_RESULT)
        r = search_artist("Hector Rubio")
        assert r is not None
        assert r.get("artistId") == 1082292215

def test_search_not_found():
    with patch("scrapers.collectors.apple_music.httpx.get") as m:
        m.return_value = MagicMock(status_code=200, json=lambda: {"resultCount": 0, "results": []})
        assert search_artist("Nobody") is None

def test_search_http_error():
    with patch("scrapers.collectors.apple_music.httpx.get") as m:
        m.return_value = MagicMock(status_code=500)
        assert search_artist("Error") is None
