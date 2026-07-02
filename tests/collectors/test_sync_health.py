"""Mock tests for sync.py orchestrator and health cache."""
from unittest.mock import patch, MagicMock, AsyncMock


# ── sync.py ──

@patch("scrapers.sync.execute_capability", new_callable=AsyncMock)
async def test_collect_artist_metrics_success(mock_exec):
    mock_exec.return_value = MagicMock(
        success=True,
        data={"followers": 100, "nb_album": 5, "deezer_id": 123},
    )
    from scrapers.sync import collect_artist_metrics
    result = await collect_artist_metrics({"nombre": "Hector Rubio", "instagram": "", "tiktok": "", "spotify_url": ""})
    assert result is not None
    assert result.get("followers") == 100


@patch("scrapers.sync.execute_capability", new_callable=AsyncMock)
async def test_collect_artist_metrics_no_provider(mock_exec):
    from scrapers.sync import NoProviderAvailableError
    mock_exec.side_effect = NoProviderAvailableError("acquire-metadata")
    from scrapers.sync import collect_artist_metrics
    result = await collect_artist_metrics({"nombre": "Nobody", "instagram": "", "tiktok": "", "spotify_url": ""})
    assert result is None


def test_load_save_data(tmp_path):
    import json
    from scrapers.sync import load_data, save_data
    test_file = tmp_path / "abe-music.json"
    with patch("scrapers.sync.DATA_FILE", test_file):
        data = load_data()
        assert "artists" in data
        data["artists"]["test"] = {"name": "test"}
        save_data(data)
        loaded = load_data()
        assert "test" in loaded["artists"]


def test_merge_skip_keys():
    from scrapers.sync import _merge
    result = {"followers": 0}
    collector = {"followers": 100, "source": "deezer", "artist_name": "Test", "fetched_at": "now"}
    _merge(result, collector)
    assert result["followers"] == 100
    assert "source" not in result
    assert "artist_name" not in result
    assert "fetched_at" not in result


# ── Health Cache ──

def test_health_cache_set_and_get():
    from planner.health import invalidate_all, get_provider_health, set_health
    from planner.models import ProviderHealth
    from datetime import datetime, timezone

    invalidate_all()
    h = ProviderHealth(provider_id="test-api", status="healthy", last_checked=datetime.now(timezone.utc))
    set_health(h)
    cached = get_provider_health("test-api")
    assert cached is not None
    assert cached.status == "healthy"


def test_health_cache_miss():
    from planner.health import invalidate_all, get_provider_health
    invalidate_all()
    assert get_provider_health("nonexistent") is None


def test_is_healthy_default():
    """is_healthy should return True for uncached providers (assume healthy)."""
    from planner.health import invalidate_all, is_healthy
    invalidate_all()
    assert is_healthy("anything") is True


def test_is_healthy_cached_down():
    from planner.health import invalidate_all, set_health, is_healthy
    from planner.models import ProviderHealth
    from datetime import datetime, timezone

    invalidate_all()
    h = ProviderHealth(provider_id="down-api", status="down", last_checked=datetime.now(timezone.utc))
    set_health(h)
    assert is_healthy("down-api") is False


def test_cache_stats():
    from planner.health import invalidate_all, set_health, get_cache_stats
    from planner.models import ProviderHealth
    from datetime import datetime, timezone

    invalidate_all()
    h1 = ProviderHealth(provider_id="a", status="healthy", last_checked=datetime.now(timezone.utc))
    h2 = ProviderHealth(provider_id="b", status="down", last_checked=datetime.now(timezone.utc))
    set_health(h1)
    set_health(h2)
    stats = get_cache_stats()
    assert stats["total"] == 2
    assert stats["healthy"] == 1
    assert stats["down"] == 1
