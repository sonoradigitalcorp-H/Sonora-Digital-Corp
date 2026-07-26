"""Tests for mem_sabe.py — MemSabe conscious memory layer."""

import pytest
from src.core.engram import Engram
from src.core.mem_sabe import MemSabe


class TestMemSabe:
    @pytest.fixture
    def memsabe(self, tmp_path):
        db = Engram(str(tmp_path / "test_memsabe.db"))
        return MemSabe(db)

    def test_sabe_returns_not_found_on_empty(self, memsabe):
        result = memsabe.sabe("nonexistent")
        assert result["found"] is False

    def test_sabe_returns_memories(self, memsabe):
        memsabe._engram.store_learning("spec-1", "test", "Hello world", "context")
        result = memsabe.sabe("Hello")
        assert result["found"] is True
        assert len(result["memories"]) >= 1

    def test_guarda_stores_and_returns_id(self, memsabe):
        mem_id = memsabe.guarda("test-key", "test-value", channels=["telegram"])
        assert isinstance(mem_id, str)
        assert int(mem_id) > 0

    def test_guarda_with_channels(self, memsabe):
        memsabe.guarda("multi-channel", "data", channels=["telegram", "web"])
        results = memsabe._engram.query_context("multi-channel")
        assert len(results) >= 1

    def test_get_channel_context(self, memsabe):
        memsabe.guarda("user1", "Hello from Telegram", channels=["telegram"])
        memsabe.guarda("user1", "Hello from Web", channels=["web"])
        ctx = memsabe.get_channel_context("user1", "telegram")
        assert ctx["channel"] == "telegram"
        assert ctx["count"] >= 1

    def test_get_unified_context(self, memsabe):
        memsabe.guarda("user2", "TG msg", channels=["telegram"])
        memsabe.guarda("user2", "WA msg", channels=["whatsapp"])
        unified = memsabe.get_unified_context("user2")
        assert unified["memory_count"] >= 2
        assert "telegram" in unified["channels"]
        assert "whatsapp" in unified["channels"]

    def test_verify_adr_compliance_no_memories(self, memsabe):
        result = memsabe.verify_adr_compliance("ADR-NONEXISTENT")
        assert result["compliant"] is False
        assert "No memories" in result["reason"]

    def test_verify_adr_compliance_evidence_found(self, memsabe):
        memsabe._engram.store_learning("ADR-001", "adr", "Implemented ADR-001 changes", "done")
        memsabe._engram.store_learning("ADR-001", "adr", "Applied security policy", "done")
        result = memsabe.verify_adr_compliance("ADR-001")
        assert result["compliant"] is True
        assert len(result["evidence"]) >= 1

    def test_build_continuity_summary(self, memsabe):
        memsabe.guarda("user3", "TG: Hello", channels=["telegram"])
        memsabe.guarda("user3", "WA: Hi", channels=["whatsapp"])
        summary = memsabe.build_continuity_summary("user3", ["telegram", "whatsapp"])
        assert summary["total_memories"] >= 2

    def test_detect_patterns_empty(self, memsabe):
        patterns = memsabe.detect_patterns(2)
        assert patterns == []

    def test_detect_patterns_finds_groups(self, memsabe):
        for i in range(3):
            memsabe._engram.store_learning(f"spec-{i}", "bug-fix", f"Bug fix {i}", "ctx")
        for i in range(2):
            memsabe._engram.store_learning(f"feat-{i}", "feature", f"Feature {i}", "ctx")
        patterns = memsabe.detect_patterns(2)
        assert len(patterns) >= 1

    def test_suggest_relevant_knowledge(self, memsabe):
        memsabe._engram.store_learning("spec-ref", "ref", "Reference data", "ctx")
        suggestions = memsabe.suggest_relevant_knowledge("Reference")
        assert len(suggestions) >= 1

    def test_sync_knowledge_graph_no_config(self, memsabe):
        synced = memsabe.sync_knowledge_graph()
        assert synced == 0
