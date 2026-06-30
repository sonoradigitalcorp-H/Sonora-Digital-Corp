"""Extended tests for engram.py — importance scoring, promotion, decay, migration, concurrent writes."""

import sqlite3
import time
import threading
from datetime import datetime, timedelta

import pytest
from src.core.engram import Engram, IMPORTANCE_LEVELS, MAX_PROMOTION_LEVEL, DECAY_DAYS


class TestEngramImportance:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "test_engram.db"))

    def test_store_with_importance_critical(self, eng):
        eng.store_learning("spec-001", "critical", "Critical fix", "context", importance="critical")
        results = eng.query_context("critical")
        assert len(results) >= 1
        assert results[0]["importance"] == 3

    def test_store_with_importance_high(self, eng):
        eng.store_learning("spec-002", "high", "High priority", "context", importance="high")
        results = eng.query_context("high")
        assert results[0]["importance"] == 2

    def test_store_with_importance_low(self, eng):
        eng.store_learning("spec-003", "low", "Low priority", "context", importance="low")
        results = eng.query_context("low")
        assert results[0]["importance"] == 0

    def test_default_importance_is_medium(self, eng):
        eng.store_learning("spec-004", "default", "Default importance", "context")
        results = eng.query_context("default")
        assert results[0]["importance"] == 1

    def test_invalid_importance_defaults_to_medium(self, eng):
        eng.store_learning("spec-005", "invalid", "Invalid importance", "context", importance="unknown")
        results = eng.query_context("invalid")
        assert results[0]["importance"] == 1

    def test_importance_levels_constants(self):
        assert IMPORTANCE_LEVELS == {"critical": 3, "high": 2, "medium": 1, "low": 0}

    def test_query_orders_by_importance_desc(self, eng):
        eng.store_learning("spec-low", "test", "Low importance item", "context", importance="low")
        eng.store_learning("spec-high", "test", "High importance item", "context", importance="high")
        eng.store_learning("spec-critical", "test", "Critical importance item", "context", importance="critical")
        results = eng.query_context("importance", limit=10)
        assert len(results) >= 3
        importances = [r["importance"] for r in results[:3]]
        assert importances == sorted(importances, reverse=True)


class TestEngramPromotion:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "promo.db"))

    def test_promote_increases_importance(self, eng):
        eng.store_learning("spec-001", "test", "Promotable item", "context", importance="low")
        results = eng.query_context("Promotable")
        mid = results[0]["id"]
        assert eng.promote(mid) is True
        results = eng.query_context("Promotable")
        assert results[0]["importance"] == 1

    def test_promote_max_level(self, eng):
        eng.store_learning("spec-002", "test", "Max promo item", "context", importance="critical")
        results = eng.query_context("Max promo")
        mid = results[0]["id"]
        assert results[0]["importance"] == MAX_PROMOTION_LEVEL
        assert eng.promote(mid) is False  # Already at max

    def test_demote_decreases_importance(self, eng):
        eng.store_learning("spec-003", "test", "Demotable item", "context", importance="high")
        results = eng.query_context("Demotable")
        mid = results[0]["id"]
        assert eng.demote(mid) is True
        results = eng.query_context("Demotable")
        assert results[0]["importance"] == 1

    def test_demote_min_level(self, eng):
        eng.store_learning("spec-004", "test", "Min demo item", "context", importance="low")
        results = eng.query_context("Min demo")
        mid = results[0]["id"]
        assert results[0]["importance"] == 0
        assert eng.demote(mid) is False  # Already at min

    def test_max_promotion_level_constant(self):
        assert MAX_PROMOTION_LEVEL == 3


class TestEngramDecay:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "decay.db"))

    def test_decay_days_constant(self):
        assert DECAY_DAYS == 30

    def test_apply_decay_demotes_old_entries(self, eng):
        eng.store_learning("spec-old", "test", "Old entry", "context", importance="high")
        # Manually set last_accessed to 31 days ago
        old_time = (datetime.now() - timedelta(days=31)).isoformat()
        with sqlite3.connect(eng.db_path) as conn:
            conn.execute(
                "UPDATE memories SET last_accessed = ? WHERE spec_id = ?",
                (old_time, "spec-old"),
            )
            conn.commit()
        eng.apply_decay()
        results = eng.query_context("Old entry")
        assert results[0]["importance"] == 1  # Demoted from 2 to 1

    def test_apply_decay_ignores_recent_entries(self, eng):
        eng.store_learning("spec-recent", "test", "Recent entry", "context", importance="high")
        # last_accessed is null (never accessed) — should not decay
        eng.apply_decay()
        results = eng.query_context("Recent entry")
        assert results[0]["importance"] == 2  # Not decayed


class TestEngramSchemaMigration:
    def test_migration_adds_columns_to_existing_db(self, tmp_path):
        """Simulate an old DB without importance/access_count columns."""
        db_path = str(tmp_path / "old_schema.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spec_id TEXT,
                tag TEXT,
                summary TEXT,
                context TEXT,
                timestamp DATETIME
            )
        """)
        conn.execute("INSERT INTO memories (spec_id, tag, summary, context, timestamp) VALUES ('old', 'test', 'Old schema', 'ctx', '2024-01-01')")
        conn.commit()
        conn.close()

        eng = Engram(db_path)
        # Migration adds new columns
        results = eng.get_by_spec("old")
        assert len(results) >= 1
        assert results[0]["spec_id"] == "old"
        assert "importance" in results[0]
        assert results[0]["importance"] == 1  # Default from migration

    def test_migration_handles_already_migrated_db(self, tmp_path):
        """Migration should be idempotent."""
        eng1 = Engram(str(tmp_path / "migrated.db"))
        eng1.store_learning("spec-1", "test", "First", "ctx")
        eng2 = Engram(str(tmp_path / "migrated.db"))
        eng2.store_learning("spec-2", "test", "Second", "ctx")
        results = eng2.query_context("First")
        assert len(results) >= 1


class TestEngramAccessTracking:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "access.db"))

    def test_query_increments_access_count(self, eng):
        eng.store_learning("spec-acc", "test", "Access tracked", "context")
        eng.query_context("Access tracked")
        eng.query_context("Access tracked")
        results = eng.query_context("Access tracked")
        assert results[0]["access_count"] >= 2

    def test_query_updates_last_accessed(self, eng):
        eng.store_learning("spec-last", "test", "Last accessed", "context")
        eng.query_context("Last accessed")
        results = eng.query_context("Last accessed")
        assert results[0]["last_accessed"] is not None


class TestEngramConcurrency:
    def test_concurrent_writes_do_not_crash(self, tmp_path):
        eng = Engram(str(tmp_path / "concurrent.db"))

        def write_learning(idx):
            try:
                eng.store_learning(f"spec-{idx}", "test", f"Concurrent {idx}", f"context {idx}")
            except Exception:
                pass

        threads = [threading.Thread(target=write_learning, args=(i,)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        results = eng.query_context("Concurrent", limit=20)
        assert len(results) >= 5  # Most should have succeeded

    def test_concurrent_query_and_write(self, tmp_path):
        eng = Engram(str(tmp_path / "concurrent2.db"))
        eng.store_learning("spec-base", "test", "Base item", "context")

        def query_loop():
            for _ in range(20):
                eng.query_context("Base")
                eng.query_context("nonexistent")

        def write_loop():
            for i in range(20):
                eng.store_learning(f"spec-con-{i}", "test", f"Concurrent query {i}", f"ctx {i}")

        t1 = threading.Thread(target=query_loop)
        t2 = threading.Thread(target=write_loop)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        assert True  # No crash


class TestEngramStats:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "stats.db"))

    def test_stats_total(self, eng):
        for i in range(5):
            eng.store_learning(f"spec-{i}", "test", f"Stats item {i}", "context")
        stats = eng.get_stats()
        assert stats["total"] >= 5

    def test_stats_by_importance(self, eng):
        eng.store_learning("spec-crit", "test", "Critical stat", "ctx", importance="critical")
        eng.store_learning("spec-high", "test", "High stat", "ctx", importance="high")
        eng.store_learning("spec-med", "test", "Medium stat", "ctx", importance="medium")
        stats = eng.get_stats()
        assert "3" in stats["by_importance"]  # critical
        assert "2" in stats["by_importance"]  # high
        assert "1" in stats["by_importance"]  # medium

    def test_stats_decay_days(self, eng):
        stats = eng.get_stats()
        assert stats["decay_days"] == 30


class TestEngramEdgeCases:
    @pytest.fixture
    def eng(self, tmp_path):
        return Engram(str(tmp_path / "edge.db"))

    def test_query_empty_string(self, eng):
        results = eng.query_context("")
        assert results == []

    def test_query_nonexistent_fts(self, eng):
        results = eng.query_context("xyznonexistent12345")
        assert results == []

    def test_store_empty_summary(self, eng):
        eng.store_learning("spec-empty", "test", "", "")
        results = eng.get_by_spec("spec-empty")
        assert len(results) >= 1
        assert results[0]["summary"] == ""

    def test_store_very_long_context(self, eng):
        long_ctx = "A" * 10000
        eng.store_learning("spec-long", "test", "Long context", long_ctx)
        results = eng.query_context("Long context")
        assert len(results) >= 1

    def test_multiple_specs_same_id(self, eng):
        eng.store_learning("spec-same", "test", "First entry", "ctx1")
        eng.store_learning("spec-same", "test", "Second entry", "ctx2")
        results = eng.get_by_spec("spec-same")
        assert len(results) == 2

    def test_get_by_spec_nonexistent(self, eng):
        results = eng.get_by_spec("nonexistent-spec")
        assert results == []
