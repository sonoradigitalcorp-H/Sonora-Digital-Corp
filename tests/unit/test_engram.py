"""
Tests para src/core/engram.py — SQLite FTS5 persistent memory.
"""
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.core.engram import Engram


class TestEngram:

    @pytest.fixture
    def engram(self, tmp_path):
        db_path = str(tmp_path / "test_engram.db")
        return Engram(db_path)

    def test_store_and_query(self, engram):
        engram.store_learning("spec-001", "bug-fix", "Fixed timeout error", "Increased timeout to 30s")
        results = engram.query_context("timeout")
        assert len(results) >= 1
        assert "Fixed timeout error" in results[0]["summary"]

    def test_query_empty_returns_empty(self, engram):
        results = engram.query_context("nonexistent")
        assert results == []

    def test_get_by_spec(self, engram):
        engram.store_learning("spec-001", "bug-fix", "Fixed timeout", "Increased timeout")
        engram.store_learning("spec-002", "feature", "Added login", "OAuth flow")
        results = engram.get_by_spec("spec-001")
        assert len(results) == 1
        assert results[0]["spec_id"] == "spec-001"

    def test_multiple_learnings(self, engram):
        for i in range(5):
            engram.store_learning(f"spec-{i}", "test", f"Learning {i}", f"Context {i}")
        results = engram.query_context("Learning", limit=10)
        assert len(results) >= 5

    def test_store_with_special_chars(self, engram):
        engram.store_learning("spec-x", "test", "Handling ñ & ü special chars", "Español + English")
        results = engram.query_context("Español")
        assert len(results) >= 1
