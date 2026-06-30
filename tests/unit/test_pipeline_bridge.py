"""Tests for pipeline_bridge.py — Engram pipeline connection."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from src.core.pipeline_bridge import (
    store_spec_completion,
    query_engram_context,
    format_engram_context,
    scan_and_store_pipeline,
)
from src.core.engram import engram


class TestStoreSpecCompletion:
    def test_store_success(self):
        result = store_spec_completion("SPEC-TEST-001", "Test completion", ["test", "spec"])
        assert result is True

    def test_store_without_tags(self):
        result = store_spec_completion("SPEC-TEST-002", "Test no tags")
        assert result is True

    def test_store_with_empty_spec_id(self):
        result = store_spec_completion("", "Empty spec", ["test"])
        assert result is False

    def test_stored_value_is_queryable(self):
        store_spec_completion("SPEC-TEST-QUERY", "Queryable completion", ["test"])
        results = query_engram_context("Queryable completion")
        summaries = [r["summary"] for r in results]
        assert "Queryable completion" in summaries


class TestQueryEngramContext:
    def test_query_returns_relevant_results(self):
        store_spec_completion("SPEC-CONTEXT-1", "Debugging connection timeout in Neo4j", ["neo4j", "debug"])
        results = query_engram_context("Neo4j connection timeout", limit=3)
        summaries = [r["summary"] for r in results]
        assert any("timeout" in s.lower() or "Neo4j" in s for s in summaries)

    def test_query_empty_returns_empty(self):
        results = query_engram_context("xyznonexistent12345xyz")
        assert results == []

    def test_query_limit_respected(self):
        for i in range(10):
            store_spec_completion(f"SPEC-LIMIT-{i}", f"Limit test {i}", ["test"])
        results = query_engram_context("Limit test", limit=3)
        assert len(results) <= 3


class TestFormatEngramContext:
    def test_format_empty_list_returns_empty_string(self):
        result = format_engram_context([])
        assert result == ""

    def test_format_with_results(self):
        results = [
            {"spec_id": "SPEC-001", "summary": "First learning", "context": "ctx1"},
            {"spec_id": "SPEC-002", "summary": "Second learning", "context": "ctx2"},
        ]
        formatted = format_engram_context(results)
        assert "SPEC-001" in formatted
        assert "First learning" in formatted
        assert "SPEC-002" in formatted
        assert "Second learning" in formatted
        assert formatted.startswith("\n")

    def test_format_includes_lines_and_markers(self):
        results = [{"spec_id": "SPEC-X", "summary": "Summary X", "context": "ctx"}]
        formatted = format_engram_context(results)
        assert "--- Relevant past learnings ---" in formatted
        assert "---" in formatted


class TestScanAndStorePipeline:
    def test_scan_does_not_crash(self):
        result = scan_and_store_pipeline()
        assert isinstance(result, int)
        assert result >= 0
