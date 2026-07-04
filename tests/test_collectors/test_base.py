"""Tests para el Artist Intelligence Network (Collectors)"""
import json
import sys
import pytest
from pathlib import Path
from datetime import datetime, timezone

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from collectors.base import RawMetric, NormalizedMetric, DerivedMetric, Normalizer, MetricsEngine


class TestRawMetric:
    def test_create(self):
        m = RawMetric(platform="spotify", metric="followers", value=1000, timestamp="2026-01-01", artist_id="test")
        assert m.platform == "spotify"
        assert m.value == 1000

    def test_with_extra(self):
        m = RawMetric(platform="spotify", metric="popularity", value=85, timestamp="2026-01-01", artist_id="test", extra={"rank": 10})
        assert m.extra["rank"] == 10


class TestNormalizer:
    def test_normalize_spotify(self):
        normalizer = Normalizer()
        raw = RawMetric(platform="spotify", metric="monthly_listeners", value=50000, timestamp="2026-01-01", artist_id="test")
        norm = normalizer.normalize(raw)
        assert norm.metric == "streams"
        assert norm.value == 50000
        assert norm.raw_value == 50000
        assert norm.platform == "spotify"

    def test_normalize_unknown_metric(self):
        normalizer = Normalizer()
        raw = RawMetric(platform="spotify", metric="unknown_metric", value=42, timestamp="2026-01-01", artist_id="test")
        norm = normalizer.normalize(raw)
        assert norm.metric == "unknown_metric"

    def test_normalize_batch(self):
        normalizer = Normalizer()
        raws = [
            RawMetric(platform="spotify", metric="monthly_listeners", value=50000, timestamp="2026-01-01", artist_id="test"),
            RawMetric(platform="spotify", metric="followers", value=2000, timestamp="2026-01-01", artist_id="test"),
        ]
        norms = normalizer.normalize_batch(raws)
        assert len(norms) == 2
        assert norms[0].metric == "streams"
        assert norms[1].metric == "followers"

    def test_normalize_tiktok(self):
        normalizer = Normalizer()
        raw = RawMetric(platform="tiktok", metric="followers", value=10000, timestamp="2026-01-01", artist_id="test")
        norm = normalizer.normalize(raw)
        assert norm.metric == "followers"

    def test_normalize_instagram(self):
        normalizer = Normalizer()
        raw = RawMetric(platform="instagram", metric="followers_count", value=5000, timestamp="2026-01-01", artist_id="test")
        norm = normalizer.normalize(raw)
        assert norm.metric == "followers"

    def test_normalize_youtube(self):
        normalizer = Normalizer()
        raw = RawMetric(platform="youtube", metric="subscribers", value=100000, timestamp="2026-01-01", artist_id="test")
        norm = normalizer.normalize(raw)
        assert norm.metric == "followers"


class TestMetricsEngine:
    def test_growth_calculation(self):
        engine = MetricsEngine(history={
            "test": {"spotify.streams": 1000}
        })
        current = [
            NormalizedMetric(metric="streams", platform="spotify", value=1200, raw_value=1200, artist_id="test", normalized_at="2026-01-02"),
        ]
        derived = engine.calculate(current, "test")
        growth = [d for d in derived if d.metric == "streams_growth_pct"]
        assert len(growth) == 1
        assert growth[0].value == 20.0

    def test_no_history_no_derived(self):
        engine = MetricsEngine()
        current = [
            NormalizedMetric(metric="streams", platform="spotify", value=1200, raw_value=1200, artist_id="test", normalized_at="2026-01-02"),
        ]
        derived = engine.calculate(current, "test")
        growth = [d for d in derived if d.metric == "streams_growth_pct"]
        assert len(growth) == 0

    def test_momentum(self):
        engine = MetricsEngine(history={
            "test": {"spotify.followers": 100}
        })
        current = [
            NormalizedMetric(metric="followers", platform="spotify", value=150, raw_value=150, artist_id="test", normalized_at="2026-01-02"),
        ]
        derived = engine.calculate(current, "test")
        momentum = [d for d in derived if d.metric == "followers_momentum"]
        assert len(momentum) == 1
        assert momentum[0].value == 1.5

    def test_momentum_no_previous(self):
        engine = MetricsEngine()
        current = [
            NormalizedMetric(metric="followers", platform="spotify", value=150, raw_value=150, artist_id="test", normalized_at="2026-01-02"),
        ]
        derived = engine.calculate(current, "test")
        momentum = [d for d in derived if d.metric == "followers_momentum"]
        assert len(momentum) == 1
        assert momentum[0].value == 1.0

    def test_save_and_load_history(self, tmp_path):
        engine = MetricsEngine(history={"test": {"spotify.streams": 100}})
        hfile = tmp_path / "history.json"
        engine.save_history(hfile)
        assert hfile.exists()

        loaded = MetricsEngine.load_history(hfile)
        assert loaded.history == {"test": {"spotify.streams": 100}}


class TestScheduler:
    def test_dry_run(self):
        """Verify dry run does not raise"""
        import asyncio
        from collectors.scheduler import run_all
        asyncio.run(run_all(dry_run=True))

    def test_registry_loading(self):
        from collectors.scheduler import load_registry
        reg = load_registry()
        assert "platforms" in reg
        assert "artists" in reg
        assert len(reg["artists"]) > 0

    def test_collector_registration(self):
        from collectors.scheduler import COLLECTOR_MAP
        assert "spotify" in COLLECTOR_MAP
        assert "instagram" in COLLECTOR_MAP
        assert "tiktok" in COLLECTOR_MAP
        assert "youtube" in COLLECTOR_MAP


class TestStatePersistence:
    def test_collector_state(self, tmp_path):
        from collectors.spotify.collector import SpotifyCollector
        collector = SpotifyCollector(state_dir=tmp_path)
        state = collector.load_state()
        assert "last_sync" in state
        assert state["last_sync"] is None

        collector.update_state("test-artist")
        state2 = collector.load_state()
        assert state2["last_sync"] is not None
        assert state2["artists"]["test-artist"]["last_sync"] is not None
