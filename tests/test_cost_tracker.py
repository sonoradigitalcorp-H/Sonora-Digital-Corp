"""Tests para Cost Intelligence — FR-01/FR-02/FR-03: Tracking de costos reales por tenant"""

import json
import os
import sqlite3
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

_TEST_DB = Path(tempfile.mkdtemp()) / "test_cost.db"


def _set_db():
    os.environ["COST_DB_PATH"] = str(_TEST_DB)


def _clean_db():
    conn = sqlite3.connect(str(_TEST_DB))
    conn.execute("DROP TABLE IF EXISTS cost_log")
    conn.commit()
    conn.close()

def _init_test_db():
    _clean_db()
    _set_db()
    conn = sqlite3.connect(str(_TEST_DB))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cost_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT,
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            cost_usd REAL NOT NULL,
            duration_ms INTEGER DEFAULT 0,
            meta TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def _seed_test_data():
    conn = sqlite3.connect(str(_TEST_DB))
    data = [
        ("tenant_a", "llm_chat", "openrouter", "gpt-4o-mini", 1.00, 0, 0),
        ("tenant_a", "llm_chat", "openrouter", "gpt-4o-mini", 2.00, 0, 0),
        ("tenant_a", "generate_image", "fal_ai", "flux-lora", 0.50, 0, 0),
        ("tenant_b", "llm_chat", "openrouter", "claude-3.5-sonnet", 5.00, 0, 0),
        ("tenant_b", "train_lora", "fal_ai", "flux-lora-train", 4.00, 0, 0),
    ]
    conn.executemany(
        "INSERT INTO cost_log (tenant_id, operation, provider, model, cost_usd, tokens_in, tokens_out) VALUES (?, ?, ?, ?, ?, ?, ?)",
        data,
    )
    conn.commit()
    conn.close()


class TestLogCost:
    def test_logs_simple_cost(self):
        _init_test_db()
        import asyncio

        from mcp.servers.cost_tracker_mcp import log_cost
        result = json.loads(asyncio.run(log_cost("tenant-test", "llm_chat", "openrouter", 0.50)))
        assert result["logged"] is True
        assert result["cost_usd"] == 0.50
        assert result["tenant_id"] == "tenant-test"

    def test_rejects_negative_cost(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import log_cost
        result = json.loads(asyncio.run(log_cost("tenant-test", "test", "test", -1.0)))
        assert "error" in result

    def test_rejects_empty_tenant(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import log_cost
        result = json.loads(asyncio.run(log_cost("", "test", "test", 1.0)))
        assert "error" in result


class TestGetTenantCosts:
    def test_returns_correct_total(self):
        _init_test_db()
        _seed_test_data()
        import asyncio

        from mcp.servers.cost_tracker_mcp import get_tenant_costs
        result = json.loads(asyncio.run(get_tenant_costs("tenant_a", 30)))
        assert result["tenant_id"] == "tenant_a"
        assert result["total_cost_usd"] == 3.50  # 1+2+0.5
        assert len(result["breakdown"]) == 2  # llm_chat + generate_image

    def test_returns_zero_for_unknown_tenant(self):
        _init_test_db()
        import asyncio

        from mcp.servers.cost_tracker_mcp import get_tenant_costs
        result = json.loads(asyncio.run(get_tenant_costs("nonexistent", 30)))
        assert result["total_cost_usd"] == 0
        assert result["breakdown"] == []

    def test_by_provider_aggregation(self):
        _init_test_db()
        _seed_test_data()
        import asyncio

        from mcp.servers.cost_tracker_mcp import get_tenant_costs
        result = json.loads(asyncio.run(get_tenant_costs("tenant_b", 30)))
        assert "openrouter" in result["by_provider"]
        assert "fal_ai" in result["by_provider"]
        assert result["by_provider"]["openrouter"] == 5.0
        assert result["by_provider"]["fal_ai"] == 4.0


class TestGetAllTenantsSummary:
    def test_returns_all_tenants(self):
        _init_test_db()
        _seed_test_data()
        import asyncio

        from mcp.servers.cost_tracker_mcp import get_all_tenants_summary
        result = json.loads(asyncio.run(get_all_tenants_summary(30)))
        assert result["tenant_count"] == 2
        assert result["total_cost_usd"] == 12.50  # 3.5 + 9.0

    def test_returns_empty_with_no_data(self):
        _init_test_db()
        import asyncio

        from mcp.servers.cost_tracker_mcp import get_all_tenants_summary
        result = json.loads(asyncio.run(get_all_tenants_summary(30)))
        assert result["tenant_count"] == 0
        assert result["total_cost_usd"] == 0


class TestCalculateLLMCost:
    def test_calculates_gpt4o_mini(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import calculate_llm_cost
        result = json.loads(asyncio.run(calculate_llm_cost("gpt-4o-mini", 1000, 500)))
        assert result["cost_usd"] == 0.00045  # (1000/1000)*0.00015 + (500/1000)*0.00060
        assert result["model"] == "gpt-4o-mini"

    def test_calculates_claude_sonnet(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import calculate_llm_cost
        result = json.loads(asyncio.run(calculate_llm_cost("claude-3.5-sonnet", 2000, 1000)))
        assert result["cost_usd"] == 0.021  # (2000/1000)*0.003 + (1000/1000)*0.015


class TestCalculateFALCost:
    def test_calculates_lora_train(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import calculate_fal_cost
        result = json.loads(asyncio.run(calculate_fal_cost("flux_lora_train", 1)))
        assert result["total_cost_usd"] == 4.0

    def test_calculates_image_batch(self):
        import asyncio

        from mcp.servers.cost_tracker_mcp import calculate_fal_cost
        result = json.loads(asyncio.run(calculate_fal_cost("flux_lora_inference", 10)))
        assert result["total_cost_usd"] == 0.10
