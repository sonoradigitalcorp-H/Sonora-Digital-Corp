"""Mock tests for Deezer collector — no HTTP calls, no API keys."""
from unittest.mock import patch, MagicMock
import json
import pytest

from scrapers.collectors.deezer import fetch_artist, search_artist, get_artist_detail, fetch_top_tracks

MOCK_SEARCH = {
    "data": [{
        "id": 9814216,
        "name": "Hector Rubio",
        "nb_fan": 660,
        "picture": "https://api.deezer.com/artist/9814216/image",
        "link": "https://www.deezer.com/artist/9814216",
    }]
}

MOCK_DETAIL = {
    "id": 9814216,
    "name": "Hector Rubio",
    "nb_fan": 660,
    "nb_album": 41,
    "radio": True,
    "link": "https://www.deezer.com/artist/9814216",
    "picture": "https://api.deezer.com/artist/9814216/image",
}

MOCK_TOP = {
    "data": [
        {"title": "Se Volvieron Locos", "rank": 289703},
        {"title": "Mil Historias", "rank": 87932},
    ]
}


def test_search_artist_returns_first_result():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_SEARCH)
        result = search_artist("Hector Rubio")
        assert result is not None
        assert result["id"] == 9814216
        assert result["name"] == "Hector Rubio"
        mock_get.assert_called_once()
        assert "search/artist" in mock_get.call_args[0][0]


def test_search_artist_returns_none_on_404():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=404)
        result = search_artist("Unknown Artist")
        assert result is None


def test_search_artist_returns_none_on_empty_data():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"data": []})
        result = search_artist("Nobody")
        assert result is None


def test_get_artist_detail():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_DETAIL)
        result = get_artist_detail(9814216)
        assert result["nb_fan"] == 660
        assert result["nb_album"] == 41
        assert result["radio"] is True


def test_get_artist_detail_returns_none_on_error():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=500)
        result = get_artist_detail(0)
        assert result is None


def test_fetch_top_tracks_returns_list():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: MOCK_TOP)
        result = fetch_top_tracks(9814216, limit=2)
        assert len(result) == 2
        assert result[0]["name"] == "Se Volvieron Locos"
        assert result[0]["popularity_score"] == 289703


def test_fetch_top_tracks_returns_empty_on_error():
    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=404)
        result = fetch_top_tracks(0)
        assert result == []


def test_fetch_artist_full_flow():
    """Integration-level: search → detail → top_tracks con mocks encadenados."""
    side_effects = [
        MagicMock(status_code=200, json=lambda: MOCK_SEARCH),
        MagicMock(status_code=200, json=lambda: MOCK_DETAIL),
        MagicMock(status_code=200, json=lambda: MOCK_TOP),
    ]

    with patch("scrapers.collectors.deezer.httpx.get") as mock_get:
        mock_get.side_effect = side_effects
        result = fetch_artist("Hector Rubio")

        assert result is not None
        assert result["source"] == "deezer"
        assert result["deezer_id"] == 9814216
        assert result["followers"] == 660
        assert len(result["top_tracks"]) == 2
        assert mock_get.call_count == 3


def test_fetch_artist_with_deezer_id_bypasses_search():
    """If deezer_id provided, skip search and go straight to detail."""
    with (
        patch("scrapers.collectors.deezer.search_artist") as mock_search,
        patch("scrapers.collectors.deezer.get_artist_detail") as mock_detail,
        patch("scrapers.collectors.deezer.fetch_top_tracks") as mock_top,
    ):
        mock_detail.return_value = MOCK_DETAIL
        mock_top.return_value = MOCK_TOP["data"]

        result = fetch_artist("Hector Rubio", deezer_id=9814216)
        assert result is not None
        mock_search.assert_not_called()
        mock_detail.assert_called_once_with(9814216)
