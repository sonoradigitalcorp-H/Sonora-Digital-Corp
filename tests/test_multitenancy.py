"""Tests for Multi-tenancy (HAS-011)"""
import json
import shutil
import tempfile
from pathlib import Path

import pytest

from tenants.manager import TenantManager
from tenants.models import TenantConfig
from memory.tenant import TenantAwareStore
from memory.stores import WorkingMemory


def test_tenant_manager_creates_default():
    with tempfile.TemporaryDirectory() as tmp:
        mgr = TenantManager()
        mgr.TENANTS_DIR = Path(tmp)
        mgr._tenants = {}
        mgr._load_defaults()
        tenant = mgr.get("abe-music")
        assert tenant is not None
        assert tenant.config.name == "ABE Music OS"
        assert tenant.config.isolation == "column"


def test_tenant_manager_list():
    mgr = TenantManager()
    tenants = mgr.list_tenants()
    assert len(tenants) >= 1
    assert tenants[0].id == "abe-music"


def test_tenant_enabled():
    mgr = TenantManager()
    assert mgr.is_enabled("abe-music") is True
    assert mgr.is_enabled("nonexistent") is False


def test_tenant_capability_allowed_wildcard():
    mgr = TenantManager()
    assert mgr.is_capability_allowed("abe-music", "analyze-artist") is True
    assert mgr.is_capability_allowed("abe-music", "anything") is True


def test_tenant_capability_restricted():
    mgr = TenantManager()
    restricted = TenantConfig(
        id="restricted-tenant",
        name="Restricted",
        capabilities=["analyze-artist", "search-knowledge"],
    )
    mgr._tenants["restricted-tenant"] = type("Tenant", (), {"config": restricted, "active": True})()
    assert mgr.is_capability_allowed("restricted-tenant", "analyze-artist") is True
    assert mgr.is_capability_allowed("restricted-tenant", "generate-video") is False


def test_tenant_budget():
    mgr = TenantManager()
    assert mgr.get_budget("abe-music") == 500.0
    assert mgr.get_budget("nonexistent") == 0.0


def test_tenant_stats():
    mgr = TenantManager()
    stats = mgr.get_stats()
    assert stats["total_tenants"] >= 1
    assert stats["tenants"][0]["id"] == "abe-music"


@pytest.mark.asyncio
async def test_tenant_aware_store():
    with tempfile.TemporaryDirectory() as tmp:
        base = WorkingMemory(tmp)
        tenant_a = TenantAwareStore(base, "tenant-a")
        tenant_b = TenantAwareStore(base, "tenant-b")

        await tenant_a.store("key1", {"data": "from A"})
        await tenant_b.store("key1", {"data": "from B"})

        result_a = await tenant_a.retrieve("key1")
        assert result_a.found
        assert result_a.data["data"] == "from A"

        result_b = await tenant_b.retrieve("key1")
        assert result_b.found
        assert result_b.data["data"] == "from B"


@pytest.mark.asyncio
async def test_tenant_isolation():
    with tempfile.TemporaryDirectory() as tmp:
        base = WorkingMemory(tmp)
        tenant_a = TenantAwareStore(base, "tenant-a")

        await tenant_a.store("private_key", {"secret": "A's secret"})
        result = await tenant_a.retrieve("private_key")
        assert result.found

        other = TenantAwareStore(base, "tenant-b")
        result_b = await other.retrieve("private_key")
        assert not result_b.found


@pytest.mark.asyncio
async def test_tenant_list_keys():
    with tempfile.TemporaryDirectory() as tmp:
        base = WorkingMemory(tmp)
        tenant_a = TenantAwareStore(base, "tenant-a")
        tenant_b = TenantAwareStore(base, "tenant-b")

        await tenant_a.store("x", {})
        await tenant_a.store("y", {})
        await tenant_b.store("x", {})

        a_keys = await tenant_a.list_keys()
        b_keys = await tenant_b.list_keys()
        assert len(a_keys) == 2
        assert len(b_keys) == 1


@pytest.mark.asyncio
async def test_tenant_delete():
    with tempfile.TemporaryDirectory() as tmp:
        base = WorkingMemory(tmp)
        tenant = TenantAwareStore(base, "my-tenant")
        await tenant.store("delete_me", {"v": 1})
        assert await tenant.delete("delete_me") is True
        result = await tenant.retrieve("delete_me")
        assert not result.found


def test_tenant_config_default():
    cfg = TenantConfig.default()
    assert cfg.id == "abe-music"
    assert cfg.budget == 500.0
    assert "*" in cfg.capabilities
