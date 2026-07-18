"""Tests para Provisioning Multi-Tenant — FR-07: Creación de tenants en <5s"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

_TEST_DB = Path(tempfile.mkdtemp()) / "test_provision.db"


def _setup():
    os.environ["TENANT_DB_PATH"] = str(_TEST_DB)
    conn = sqlite3.connect(str(_TEST_DB))
    conn.execute("DROP TABLE IF EXISTS tenants")
    conn.execute("DROP TABLE IF EXISTS partners")
    conn.commit()
    conn.close()
    from scripts.provision_tenant import _init_db
    _init_db()


class TestProvision:
    def test_creates_aztrotech_tenant(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Juan Pérez", "pro")))
        assert result["status"] == "active"
        assert result["partner_id"] == "aztrotech"
        assert result["client_name"] == "Juan Pérez"
        assert result["plan"] == "pro"
        assert "tenant_id" in result
        assert result["tenant_id"].startswith("aztrotech_")

    def test_creates_abe_music_tenant(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("abe_music", "Artista X", "enterprise")))
        assert result["partner_id"] == "abe_music"
        assert result["plan"] == "enterprise"

    def test_provisions_under_5_seconds(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "basic")))
        assert result["provisioning_ms"] < 5000

    def test_rejects_empty_partner(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("", "Test", "basic")))
        assert "error" in result

    def test_rejects_empty_client(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "", "basic")))
        assert "error" in result

    def test_rejects_unknown_partner(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("unknown", "Test", "basic")))
        assert "error" in result

    def test_rejects_unknown_plan(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "platinum")))
        assert "error" in result

    def test_branding_included(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Cliente A", "basic")))
        assert "branding" in result
        assert result["branding"]["primary_color"] == "#00d4ff"
        assert result["branding"]["powered_by"] is True
        assert "Sonora Digital Corp" in result.get("powered_by", "")

    def test_abe_branding_different(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("abe_music", "Artista", "basic")))
        assert result["branding"]["primary_color"] == "#FF6B35"

    def test_each_tenant_has_unique_id(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        r1 = json.loads(asyncio.run(provision("aztrotech", "A", "basic")))
        r2 = json.loads(asyncio.run(provision("aztrotech", "B", "basic")))
        assert r1["tenant_id"] != r2["tenant_id"]

    def test_engram_namespace_generated(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "basic")))
        assert result["engram_namespace"].endswith("/")
        assert result["engram_namespace"].startswith("aztrotech_")

    def test_supabase_path_generated(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "basic")))
        assert result["supabase_path"].startswith("tenants/")

    def test_qdrant_collection_generated(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "basic")))
        assert result["qdrant_collection"].startswith("vectors_")

    def test_neo4j_label_generated(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import provision
        result = json.loads(asyncio.run(provision("aztrotech", "Test", "basic")))
        assert result["neo4j_label"].startswith("Tenant_")


class TestListTenants:
    def test_lists_all_tenants(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import list_tenants, provision
        asyncio.run(provision("aztrotech", "A", "basic"))
        asyncio.run(provision("aztrotech", "B", "pro"))
        result = json.loads(asyncio.run(list_tenants()))
        assert result["count"] == 2

    def test_filters_by_partner(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import list_tenants, provision
        asyncio.run(provision("aztrotech", "A", "basic"))
        asyncio.run(provision("abe_music", "B", "pro"))
        result = json.loads(asyncio.run(list_tenants("aztrotech")))
        assert result["count"] == 1
        assert result["partner_filter"] == "aztrotech"


class TestStats:
    def test_returns_counts(self):
        _setup()
        import asyncio

        from scripts.provision_tenant import get_stats, provision
        asyncio.run(provision("aztrotech", "A", "basic"))
        asyncio.run(provision("aztrotech", "B", "pro"))
        result = json.loads(asyncio.run(get_stats()))
        assert result["total_tenants"] >= 2
        assert result["total_partners"] >= 1
