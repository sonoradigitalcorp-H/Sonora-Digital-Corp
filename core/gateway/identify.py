"""Tenant identification from inbound requests.

Identifies which tenant a request belongs to based on:
- HTTP header (X-Tenant-ID)
- Channel (Telegram chat_id, WhatsApp number)
- API key prefix
- Subdomain/hostname

Usage:
    from core.gateway.identify import identify_tenant
    tenant_id = identify_tenant(request)
"""

import re
from pathlib import Path
from typing import Optional

from core.tenants.resolver import TenantResolver, UnknownTenantError


# Channel-to-tenant mapping: populated from registry or environment
# Format: {channel_type: {channel_id: tenant_id}}
_CHANNEL_MAP: dict[str, dict[str, str]] = {}


def identify_tenant(
    headers: Optional[dict] = None,
    channel: Optional[str] = None,
    channel_id: Optional[str] = None,
    api_key: Optional[str] = None,
    host: Optional[str] = None,
) -> str:
    """Identify tenant from request attributes. Returns tenant_id or raises."""

    # 1. HTTP Header (most explicit)
    if headers and "X-Tenant-ID" in headers:
        tid = headers["X-Tenant-ID"].strip().lower()
        _validate_tenant(tid)
        return tid

    if headers and "X-Tenant-Id" in headers:
        tid = headers["X-Tenant-Id"].strip().lower()
        _validate_tenant(tid)
        return tid

    # 2. API Key prefix (sk_<tenant>_<random>)
    if api_key:
        match = re.match(r"^sk_([a-z]+)_", api_key)
        if match:
            tid = match.group(1)
            _validate_tenant(tid)
            return tid

    # 3. Channel mapping (Telegram chat, WhatsApp number)
    if channel and channel_id:
        mapping = _CHANNEL_MAP.get(channel, {})
        tid = mapping.get(channel_id)
        if tid:
            return tid

    # 4. Subdomain: tenant.myserver.com -> tenant_id
    if host:
        subdomain = host.split(".")[0].strip().lower()
        try:
            _validate_tenant(subdomain)
            return subdomain
        except UnknownTenantError:
            pass

    # 5. Fallback: default tenant
    return "sonora-digital"


def register_channel(channel_type: str, channel_id: str, tenant_id: str):
    """Register a channel-to-tenant mapping."""
    if channel_type not in _CHANNEL_MAP:
        _CHANNEL_MAP[channel_type] = {}
    _CHANNEL_MAP[channel_type][channel_id] = tenant_id


def _validate_tenant(tenant_id: str):
    resolver = TenantResolver()
    if tenant_id not in resolver.list_tenants():
        raise UnknownTenantError(f"Unknown tenant: {tenant_id}")
