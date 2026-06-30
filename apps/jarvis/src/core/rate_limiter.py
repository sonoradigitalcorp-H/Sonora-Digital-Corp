#!/usr/bin/env python3
"""
SDC Rate Limiter — Token bucket en Redis para multi-tenant.

Uso:
    from rate_limiter import check_rate_limit
    
    if not check_rate_limit("sdc-core"):
        return {"error": "Rate limit exceeded"}
"""

import json
import os
from pathlib import Path

# Redis connection (lazy init)
_redis = None

def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis
            _redis = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
                decode_responses=True,
                socket_connect_timeout=2,
            )
            _redis.ping()
        except Exception:
            _redis = None
    return _redis

# Load tenant config
_config_path = Path(__file__).parent.parent.parent / "config" / "tenants.json"
_tenant_config = {}
if _config_path.exists():
    try:
        with open(_config_path) as f:
            _tenant_config = json.load(f).get("tenants", {})
    except Exception:
        pass


def get_tenant_config(tenant_id: str) -> dict:
    """Get config for a tenant, falling back to defaults."""
    defaults = {
        "rate_limit": 10,
        "period_seconds": 60,
        "max_tokens_monthly": 10000,
    }
    tenant = _tenant_config.get(tenant_id, {})
    return {**defaults, **tenant}


def check_rate_limit(tenant_id: str) -> bool:
    """Check if tenant is within rate limit. Returns True if allowed."""
    config = get_tenant_config(tenant_id)
    max_req = config.get("rate_limit", 10)
    window = config.get("period_seconds", 60)
    
    r = _get_redis()
    if r is None:
        # Redis not available — allow (fail open)
        return True
    
    key = f"rate_limit:{tenant_id}"
    try:
        current = r.incr(key)
        if current == 1:
            r.expire(key, window)
        return current <= max_req
    except Exception:
        return True


def get_usage(tenant_id: str) -> dict:
    """Get current rate limit usage for a tenant."""
    config = get_tenant_config(tenant_id)
    max_req = config.get("rate_limit", 10)
    
    r = _get_redis()
    if r is None:
        return {"current": 0, "limit": max_req, "remaining": max_req}
    
    key = f"rate_limit:{tenant_id}"
    try:
        current = int(r.get(key) or 0)
        ttl = r.ttl(key)
        return {
            "current": current,
            "limit": max_req,
            "remaining": max(0, max_req - current),
            "reset_in_seconds": ttl if ttl > 0 else config.get("period_seconds", 60),
        }
    except Exception:
        return {"current": 0, "limit": max_req, "remaining": max_req}
