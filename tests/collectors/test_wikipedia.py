"""Mock tests for Wikipedia collector."""
from unittest.mock import patch, MagicMock
from scrapers.collectors.wikipedia import fetch_artist


def test_fetch_found():
    with patch("scrapers.collectors.wikipedia.httpx.get") as m:
        m.return_value = MagicMock(status_code=200, json=lambda: {
            "title": "Hector Rubio", "extract": "Mexican singer", "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Hector_Rubio"}}
        })
        r = fetch_artist("Hector Rubio")
        assert r is not None
        assert "bio" in r


def test_fetch_not_found():
    with patch("scrapers.collectors.wikipedia.httpx.get") as m:
        m.return_value = MagicMock(status_code=404)
        r = fetch_artist("Nobody")
        assert r is None


def test_fetch_403():
    with patch("scrapers.collectors.wikipedia.httpx.get") as m:
        m.return_value = MagicMock(status_code=403)
        r = fetch_artist("Hector Rubio")
        assert r is None
