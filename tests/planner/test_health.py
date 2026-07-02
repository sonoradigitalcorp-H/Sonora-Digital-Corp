"""Tests for planner health checker."""
from datetime import datetime, timezone

import pytest

from planner.health import (
    check_provider_health,
    get_cache_stats,
    get_provider_health,
    invalidate,
    invalidate_all,
    is_healthy,
    is_stale,
    set_health,
)
from planner.models import ProviderHealth


class TestHealthCache:
    def test_set_and_get(self):
        invalidate_all()
        h = ProviderHealth(
            provider_id="test",
            status="healthy",
            last_checked=datetime.now(timezone.utc),
        )
        set_health(h)
        cached = get_provider_health("test")
        assert cached is not None
        assert cached.status == "healthy"

    def test_miss_returns_none(self):
        invalidate_all()
        cached = get_provider_health("nonexistent")
        assert cached is None

    def test_cache_not_stale_early(self):
        invalidate_all()
        h = ProviderHealth(
            provider_id="test",
            status="healthy",
            last_checked=datetime.now(timezone.utc),
        )
        set_health(h)
        assert not is_stale("test")

    def test_invalidate_removes(self):
        invalidate_all()
        h = ProviderHealth(
            provider_id="test",
            status="healthy",
            last_checked=datetime.now(timezone.utc),
        )
        set_health(h)
        invalidate("test")
        assert get_provider_health("test") is None

    def test_invalidate_all(self):
        invalidate_all()
        for i in range(3):
            set_health(ProviderHealth(
                provider_id=f"p{i}",
                status="healthy",
                last_checked=datetime.now(timezone.utc),
            ))
        invalidate_all()
        stats = get_cache_stats()
        assert stats["total"] == 0


class TestIsHealthy:
    def test_healthy_returns_true(self):
        invalidate_all()
        set_health(ProviderHealth(
            provider_id="test",
            status="healthy",
            last_checked=datetime.now(timezone.utc),
        ))
        assert is_healthy("test") is True

    def test_down_returns_false(self):
        invalidate_all()
        set_health(ProviderHealth(
            provider_id="test",
            status="down",
            last_checked=datetime.now(timezone.utc),
        ))
        assert is_healthy("test") is False

    def test_no_cache_returns_true(self):
        invalidate_all()
        assert is_healthy("unknown") is True  # assume healthy


class TestCheckProviderHealth:
    @pytest.mark.asyncio
    async def test_no_url_assumes_healthy(self):
        health = await check_provider_health(provider_id="test")
        assert health.status == "healthy"
        assert health.latency_ms == 0.0

    @pytest.mark.asyncio
    async def test_healthy_url(self):
        # Use a real fast endpoint
        health = await check_provider_health(
            health_url="https://api.deezer.com/artist/0",
            provider_id="deezer",
        )
        assert health.status in ("healthy", "degraded")
        assert health.latency_ms >= 0

    @pytest.mark.asyncio
    async def test_timeout(self):
        health = await check_provider_health(
            health_url="https://httpbin.org/delay/10",
            provider_id="slow",
            timeout=1,
        )
        assert health.status == "down"
        assert health.error is not None


class TestCacheStats:
    def test_stats_counts(self):
        invalidate_all()
        set_health(ProviderHealth(
            provider_id="h1", status="healthy",
            last_checked=datetime.now(timezone.utc),
        ))
        set_health(ProviderHealth(
            provider_id="h2", status="healthy",
            last_checked=datetime.now(timezone.utc),
        ))
        set_health(ProviderHealth(
            provider_id="d1", status="down",
            last_checked=datetime.now(timezone.utc),
        ))
        set_health(ProviderHealth(
            provider_id="dg1", status="degraded",
            last_checked=datetime.now(timezone.utc),
        ))
        stats = get_cache_stats()
        assert stats["total"] == 4
        assert stats["healthy"] == 2
        assert stats["down"] == 1
        assert stats["degraded"] == 1
