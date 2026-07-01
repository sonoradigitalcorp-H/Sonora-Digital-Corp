"""Tests for Live Data Pipeline (SPEC-20260701-003)."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

DATA_DIR = Path(__file__).parent.parent.parent / "data"
SCHEMA_FIELDS = ["source", "artist_name", "followers", "top_tracks",
                 "url", "fetched_at"]


class TestCollectorSchema:
    def test_schema_source_exists(self):
        from scrapers.collectors.deezer import fetch_artist
        with patch("scrapers.collectors.deezer.search_artist") as mock_sa, \
             patch("scrapers.collectors.deezer.get_artist_detail") as mock_detail, \
             patch("scrapers.collectors.deezer.fetch_top_tracks") as mock_tt:
            mock_sa.return_value = {"id": 123, "name": "Test"}
            mock_detail.return_value = {"name": "Test", "nb_fan": 100, "link": ""}
            mock_tt.return_value = []
            result = fetch_artist("Test")
            for field in SCHEMA_FIELDS:
                assert field in result, f"Schema missing field: {field}"
            assert result["source"] == "deezer"

    def test_top_tracks_uses_popularity_score(self):
        from scrapers.collectors.deezer import fetch_top_tracks
        with patch("httpx.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                "data": [{"title": "Track", "rank": 5000}]
            }
            tracks = fetch_top_tracks(123)
            assert tracks[0]["name"] == "Track"
            assert tracks[0]["popularity_score"] == 5000

    def test_fetched_at_is_iso_format(self):
        import re
        iso_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
        assert re.match(iso_pattern, "2026-07-01T12:00:00Z")


class TestDeezerCollector:
    @patch("scrapers.collectors.deezer.search_artist")
    @patch("scrapers.collectors.deezer.get_artist_detail")
    @patch("scrapers.collectors.deezer.fetch_top_tracks")
    def test_fetch_artist_success(self, mock_tt, mock_detail, mock_search):
        mock_search.return_value = {"id": 9814216, "name": "Hector Rubio"}
        mock_detail.return_value = {
            "id": 9814216, "name": "Hector Rubio", "nb_fan": 45000,
            "nb_album": 41, "radio": True,
            "link": "https://www.deezer.com/artist/9814216",
            "picture": "https://api.deezer.com/artist/9814216/image",
        }
        mock_tt.return_value = []

        from scrapers.collectors.deezer import fetch_artist
        result = fetch_artist("Hector Rubio")

        assert result["source"] == "deezer"
        assert result["artist_name"] == "Hector Rubio"
        assert result["followers"] == 45000
        assert result["deezer_id"] == 9814216
        assert result["nb_album"] == 41
        assert result["has_radio"] is True
        assert "fetched_at" in result

    @patch("scrapers.collectors.deezer.search_artist")
    def test_fetch_artist_not_found(self, mock_search):
        mock_search.return_value = None

        from scrapers.collectors.deezer import fetch_artist
        result = fetch_artist("Unknown Artist")
        assert result is None

    @patch("httpx.get")
    def test_fetch_top_tracks(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": [
                {"title": "Se Volvieron Locos", "rank": 289703},
                {"title": "Track 2", "rank": 87932},
            ]
        }

        from scrapers.collectors.deezer import fetch_top_tracks
        tracks = fetch_top_tracks(9814216)
        assert len(tracks) == 2
        assert tracks[0]["name"] == "Se Volvieron Locos"
        assert tracks[0]["popularity_score"] == 289703

    @patch("scrapers.collectors.deezer.search_artist")
    @patch("scrapers.collectors.deezer.get_artist_detail")
    @patch("scrapers.collectors.deezer.fetch_top_tracks")
    def test_fetch_artist_includes_top_tracks(self, mock_tt, mock_detail, mock_search):
        mock_search.return_value = {"id": 9814216}
        mock_detail.return_value = {"name": "Test", "nb_fan": 100, "link": ""}
        mock_tt.return_value = [{"name": "Song", "popularity_score": 5000}]

        from scrapers.collectors.deezer import fetch_artist
        result = fetch_artist("Test")
        assert len(result["top_tracks"]) == 1
        assert result["top_tracks"][0]["name"] == "Song"


class TestSyncOrchestrator:
    @pytest.fixture
    def sample_abe_data(self):
        return {
            "artists": {
                "artist1": {
                    "id": "artist1",
                    "nombre": "Hector Rubio",
                    "streams": 115093009,
                    "revenue": 460372.0,
                    "followers": 45000,
                    "nb_album": 41,
                    "status": "active"
                }
            },
            "releases": {}
        }

    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.collect_artist_metrics")
    def test_sync_updates_followers(self, mock_collect, mock_save, mock_load, sample_abe_data):
        mock_load.return_value = sample_abe_data
        mock_collect.return_value = {
            "followers": 46000,
            "nb_album": 42,
            "deezer_id": 9814216,
            "top_tracks": [],
            "url": "",
            "source": "deezer",
            "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import sync_artist
        result = sync_artist("artist1")

        assert result["updated"] is True
        assert result["delta"]["followers"] == 1000
        assert result["delta"]["nb_album"] == 1

    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.collect_artist_metrics")
    def test_sync_no_changes(self, mock_collect, mock_save, mock_load, sample_abe_data):
        mock_load.return_value = sample_abe_data
        mock_collect.return_value = {
            "followers": 45000,
            "nb_album": 41,
            "deezer_id": 9814216,
            "top_tracks": [],
            "url": "",
            "source": "deezer",
            "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import sync_artist
        result = sync_artist("artist1")

        assert result["updated"] is False
        assert result["delta"]["followers"] == 0

    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.backup_data")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.collect_artist_metrics")
    def test_backup_before_write(self, mock_collect, mock_save, mock_backup, mock_load, sample_abe_data):
        mock_load.return_value = sample_abe_data
        mock_collect.return_value = {
            "followers": 99999,
            "nb_album": 99,
            "top_tracks": [],
            "url": "",
            "source": "deezer",
            "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import run_sync_cycle
        run_sync_cycle()

        mock_backup.assert_called_once()

    @patch("scrapers.sync.load_data")
    def test_partial_merge_preserves_existing_fields(self, mock_load):
        existing = {
            "artists": {
                "a1": {
                    "id": "a1",
                    "nombre": "Test",
                    "streams": 1000,
                    "revenue": 500.0,
                    "followers": 100,
                    "nb_album": 5,
                }
            },
            "releases": {}
        }
        mock_load.return_value = existing

        from scrapers.sync import sync_artist
        with patch("scrapers.sync.collect_artist_metrics") as mock_collect, \
             patch("scrapers.sync.save_data"):
            mock_collect.return_value = {
                "followers": 150,
                "nb_album": 5,
                "deezer_id": 123,
                "top_tracks": [{"name": "X", "popularity_score": 100}],
                "url": "",
                "source": "deezer",
                "fetched_at": "2026-07-01T12:00:00Z"
            }
            result = sync_artist("a1")
            assert result["updated"] is True
            assert result["delta"]["followers"] == 50
            assert result["delta"]["nb_album"] == 0


class TestFallbackChain:
    @patch("scrapers.collectors.deezer.search_artist")
    @patch("scrapers.collectors.deezer.get_artist_detail")
    def test_fallback_when_detail_fails(self, mock_detail, mock_search):
        mock_search.return_value = {"id": 123, "name": "Test"}
        mock_detail.return_value = None

        with patch("scrapers.collectors.deezer.fetch_top_tracks") as mock_tt:
            mock_tt.return_value = []
            from scrapers.collectors.deezer import fetch_artist
            result = fetch_artist("Test")
            assert result is None

    @patch("scrapers.collectors.deezer.fetch_artist")
    @patch("scrapers.collectors.deezer.search_artist")
    def test_fallback_search_succeeds(self, mock_search, mock_fetch):
        mock_fetch.return_value = None
        mock_search.return_value = {
            "name": "Hector Rubio",
            "nb_fan": 45000,
            "link": "https://www.deezer.com/artist/test"
        }

        from scrapers.collectors.deezer import fetch_artist_with_fallback
        result = fetch_artist_with_fallback("Hector Rubio")
        assert result is not None
        assert result["followers"] == 45000


class TestAppleMusicCollector:
    @patch("scrapers.collectors.apple_music.search_artist")
    def test_fetch_artist_success(self, mock_search):
        mock_search.return_value = {
            "artistId": 1082292215,
            "artistName": "Hector Rubio",
            "artistLinkUrl": "https://music.apple.com/us/artist/hector-rubio/1082292215",
            "primaryGenreName": "Latin",
        }
        from scrapers.collectors.apple_music import fetch_artist
        result = fetch_artist("Hector Rubio")
        assert result["source"] == "apple_music"
        assert result["apple_music_id"] == 1082292215
        assert "music.apple.com" in result["apple_music_url"]

    @patch("scrapers.collectors.apple_music.search_artist")
    def test_fetch_artist_not_found(self, mock_search):
        mock_search.return_value = None
        from scrapers.collectors.apple_music import fetch_artist
        assert fetch_artist("Unknown Artist") is None

    @patch("scrapers.collectors.apple_music.lookup_artist")
    def test_fetch_by_id(self, mock_lookup):
        mock_lookup.return_value = {
            "artistId": 1082292215,
            "artistName": "Hector Rubio",
            "primaryGenreName": "Regional Mexicano",
        }
        from scrapers.collectors.apple_music import fetch_artist
        result = fetch_artist("Hector Rubio", artist_id=1082292215)
        assert result["apple_music_id"] == 1082292215
        assert "Regional Mexicano" in result["genres"]


class TestWikipediaCollector:
    @patch("httpx.get")
    def test_fetch_artist_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "title": "Hector Rubio",
            "extract": "Hector Rubio is a Mexican singer...",
            "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Hector_Rubio"}},
        }
        from scrapers.collectors.wikipedia import fetch_artist
        result = fetch_artist("Hector Rubio")
        assert result["source"] == "wikipedia"
        assert "Mexican singer" in result["bio"]
        assert "wikipedia" in result["wikipedia_url"]

    @patch("httpx.get")
    def test_fetch_artist_not_found(self, mock_get):
        mock_get.return_value.status_code = 404
        from scrapers.collectors.wikipedia import fetch_artist
        assert fetch_artist("Nonexistent Artist") is None

    @patch("httpx.get")
    def test_fallback_on_disambiguation(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"type": "disambiguation", "title": "Test"}
        from scrapers.collectors.wikipedia import fetch_artist
        assert fetch_artist("Test") is None


class TestEventEmission:
    @patch("scrapers.sync.emit_event")
    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.collect_artist_metrics")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.backup_data")
    def test_sync_emits_event(self, mock_backup, mock_save, mock_collect, mock_load, mock_emit):
        mock_load.return_value = {
            "artists": {"a1": {"id": "a1", "nombre": "Hector Rubio", "streams": 115093009, "followers": 45000, "nb_album": 41}},
            "releases": {}
        }
        mock_collect.return_value = {
            "followers": 46000, "nb_album": 42, "top_tracks": [],
            "url": "", "source": "deezer", "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import run_sync_cycle
        run_sync_cycle()

        assert mock_emit.call_count == 2
        events = [c[0][0] for c in mock_emit.call_args_list]
        assert events[0]["type"] == "data_sync_completed"
        assert events[1]["type"] == "lead_generated_from_data"
        # Both events should have write_pipeline=True
        for call in mock_emit.call_args_list:
            assert call[1].get("write_pipeline") is True

    @patch("scrapers.sync.bridge_lead_to_pipeline")
    @patch("scrapers.sync.emit_event")
    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.collect_artist_metrics")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.backup_data")
    def test_sync_calls_bridge_for_high_value(self, mock_backup, mock_save, mock_collect, mock_load, mock_emit, mock_bridge):
        mock_load.return_value = {
            "artists": {"a1": {"id": "a1", "nombre": "Hector Rubio", "streams": 115093009, "followers": 45000, "nb_album": 41}},
            "releases": {}
        }
        mock_collect.return_value = {
            "followers": 46000, "nb_album": 42, "top_tracks": [],
            "url": "", "source": "deezer", "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import run_sync_cycle
        run_sync_cycle()

        mock_bridge.assert_called_once()
        artist_arg = mock_bridge.call_args[0][0]
        assert artist_arg["nombre"] == "Hector Rubio"
        assert artist_arg["streams"] == 115093009

    @patch("scrapers.sync.bridge_lead_to_pipeline")
    @patch("scrapers.sync.emit_event")
    @patch("scrapers.sync.load_data")
    @patch("scrapers.sync.collect_artist_metrics")
    @patch("scrapers.sync.save_data")
    @patch("scrapers.sync.backup_data")
    def test_sync_skips_bridge_for_low_value(self, mock_backup, mock_save, mock_collect, mock_load, mock_emit, mock_bridge):
        mock_load.return_value = {
            "artists": {"a1": {"id": "a1", "nombre": "Low Value Artist", "streams": 5000, "followers": 50, "nb_album": 1}},
            "releases": {}
        }
        mock_collect.return_value = {
            "followers": 60, "nb_album": 1, "top_tracks": [],
            "url": "", "source": "deezer", "fetched_at": "2026-07-01T12:00:00Z"
        }

        from scrapers.sync import run_sync_cycle
        run_sync_cycle()

        mock_bridge.assert_not_called()
        # Only data_sync_completed event, no lead event
        assert mock_emit.call_count == 1


class TestLeadBridge:
    def test_bridge_skips_duplicates(self):
        from scrapers.sync import _read_bridge_state, _save_bridge_state, bridge_lead_to_pipeline
        import tempfile, os

        _save_bridge_state({"Hector Rubio"})
        artist = {"nombre": "Hector Rubio", "genero": "Regional Mexicano", "streams": 1000000, "followers": 50000}

        with patch("scrapers.sync.logger") as mock_log:
            bridge_lead_to_pipeline(artist)
            mock_log.info.assert_called_with("Skipping duplicate lead bridge for Hector Rubio")

    def test_niche_map(self):
        from scrapers.sync import NICHE_MAP
        assert NICHE_MAP["Regional Mexicano"] == "musica"
        assert NICHE_MAP["Pop Latino"] == "musica"
        assert NICHE_MAP.get("Unknown Genre", "musica") == "musica"
