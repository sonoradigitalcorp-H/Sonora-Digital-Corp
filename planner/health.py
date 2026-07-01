"""Health checker with TTL cache for provider availability."""
from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from planner.models import ProviderHealth

log = logging.getLogger("planner.health")

HEALTH_TIMEOUT = 5.0
CACHE_TTL_SECONDS = 300  # 5 minutes
DEGRADED_THRESHOLD_MS = 2000  # 2 seconds

_cache: dict[str, ProviderHealth] = {}


def get_provider_health(provider_id: str, force: bool = False) -> ProviderHealth | None:
    """Return cached health for a provider. Refreshes if stale or forced."""
    now = time.time()

    if not force and provider_id in _cache:
        cached = _cache[provider_id]
        age = now - cached.last_checked.timestamp()
        if age < CACHE_TTL_SECONDS:
            return cached

    return None


def set_health(health: ProviderHealth):
    """Store health in cache."""
    _cache[health.provider_id] = health


def is_healthy(provider_id: str) -> bool:
    """Check if a provider is currently healthy (from cache or default)."""
    health = get_provider_health(provider_id)
    if health is not None:
        return health.status == "healthy"
    return True  # assume healthy if no health data


def is_stale(provider_id: str) -> bool:
    """Check if cached health data is stale."""
    if provider_id not in _cache:
        return True
    age = time.time() - _cache[provider_id].last_checked.timestamp()
    return age > CACHE_TTL_SECONDS


def invalidate(provider_id: str):
    """Remove a provider from cache."""
    _cache.pop(provider_id, None)


def invalidate_all():
    """Clear entire health cache."""
    _cache.clear()


async def check_provider_health(health_url: str | None = None, provider_id: str = "",
                                timeout: float = HEALTH_TIMEOUT) -> ProviderHealth:
    """Execute health check against a provider's health URL.

    If no health_url, assume healthy with zero latency.
    """
    now = datetime.now(timezone.utc)
    start = time.time()

    if not health_url:
        return ProviderHealth(
            provider_id=provider_id,
            status="healthy",
            last_checked=now,
            latency_ms=0.0,
        )

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(health_url, follow_redirects=True)
        latency_ms = (time.time() - start) * 1000

        if resp.status_code < 500:
            status = "healthy"
            error = None
        else:
            status = "down"
            error = f"HTTP {resp.status_code}"

        if status == "healthy" and latency_ms > DEGRADED_THRESHOLD_MS:
            status = "degraded"
            error = f"High latency: {latency_ms:.0f}ms"

        health = ProviderHealth(
            provider_id=provider_id,
            status=status,
            last_checked=now,
            latency_ms=latency_ms,
            error=error,
        )
    except httpx.TimeoutException:
        latency_ms = (time.time() - start) * 1000
        health = ProviderHealth(
            provider_id=provider_id,
            status="degraded",
            last_checked=now,
            latency_ms=latency_ms,
            error=f"Timeout after {timeout}s",
        )
    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        health = ProviderHealth(
            provider_id=provider_id,
            status="down",
            last_checked=now,
            latency_ms=latency_ms,
            error=str(e),
        )

    set_health(health)
    return health


def get_cache_stats() -> dict[str, Any]:
    """Return cache statistics."""
    total = len(_cache)
    healthy = sum(1 for h in _cache.values() if h.status == "healthy")
    degraded = sum(1 for h in _cache.values() if h.status == "degraded")
    down = sum(1 for h in _cache.values() if h.status == "down")
    return {
        "total": total,
        "healthy": healthy,
        "degraded": degraded,
        "down": down,
    }
