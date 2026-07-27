"""Rate limiter per tenant.

Uses in-memory counters (or Redis if available) to enforce per-tenant rate limits.

Usage:
    from core.gateway.rate_limiter import RateLimiter
    limiter = RateLimiter()
    
    if not limiter.check("sonora-digital", "whatsapp"):
        return 429 "Rate limit exceeded"
"""

import time
from collections import defaultdict
from typing import Optional

from apps.core.tenants.resolver import TenantResolver


class RateLimiter:
    def __init__(self):
        self._buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
        self._resolver = TenantResolver()

    def check(self, tenant_id: str, channel: str = "api") -> bool:
        """Check if a request is within rate limits for the tenant+channel.

        Returns True if allowed, False if rate limited.
        """
        ctx = self._resolver.load(tenant_id)
        policies = ctx.policies
        rate_limits = policies.get("rate_limits", {})
        raw = rate_limits.get(channel, rate_limits.get("api_calls", "60"))
        limit = int(str(raw).split("/")[0].strip())
        window = 60  # seconds

        now = time.time()
        timestamps = self._buckets[tenant_id][channel]

        # Remove expired entries
        cutoff = now - window
        self._buckets[tenant_id][channel] = [t for t in timestamps if t > cutoff]

        current_count = len(self._buckets[tenant_id][channel])
        if current_count >= limit:
            return False

        self._buckets[tenant_id][channel].append(now)
        return True

    def remaining(self, tenant_id: str, channel: str = "api") -> int:
        """Get remaining requests in current window."""
        ctx = self._resolver.load(tenant_id)
        raw = ctx.policies.get("rate_limits", {}).get(channel, "60")
        limit = int(str(raw).split("/")[0].strip())
        now = time.time()
        cutoff = now - 60
        current = len([t for t in self._buckets[tenant_id][channel] if t > cutoff])
        return max(0, limit - current)

    def reset(self, tenant_id: Optional[str] = None):
        """Reset rate limiter for a tenant (or all if None)."""
        if tenant_id:
            self._buckets.pop(tenant_id, None)
        else:
            self._buckets.clear()
