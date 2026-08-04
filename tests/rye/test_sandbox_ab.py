"""Sandbox A/B baseline tests for RYE fake bot — runs with make test."""
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SANDBOX = REPO / "sandbox" / "rye"
RESULTS = SANDBOX / "evals" / "ab_baseline.jsonl"

import pytest


def _run_fake_bot():
    env = dict(os.environ)
    env.setdefault("EMBED_BACKEND", "ollama")
    env.setdefault("EMBED_MODEL", "all-minilm")
    env.setdefault("EMBEDDING_DIM", "384")
    proc = subprocess.run(
        [sys.executable, str(SANDBOX / "fake_bot.py")],
        capture_output=True, text=True, timeout=120, env=env,
    )
    return proc


def test_fake_bot_ab_baseline():
    """Seed fixtures, run A/B, assert RAG variant gets context for all queries."""
    proc = _run_fake_bot()
    assert proc.returncode == 0, f"fake_bot failed: {proc.stderr[-500:]}"
    assert RESULTS.exists(), f"Results file missing: {RESULTS}"

    rows = [json.loads(line) for line in RESULTS.read_text().splitlines() if line.strip()]
    results = {r["variant"]: [r for r in rows if r["variant"] == r["variant"]] for r in rows} if False else None
    rag = [r for r in rows if r["variant"] == "rag"]
    baseline = [r for r in rows if r["variant"] == "baseline"]

    assert len(rag) == 5, f"Expected 5 rag results, got {len(rag)}"
    assert len(baseline) == 5, f"Expected 5 baseline results, got {len(baseline)}"

    assert all(r["has_context"] for r in rag), "RAG variant should have context for all queries"
    assert not any(r["has_context"] for r in baseline), "Baseline should have no context"

    rag_lat = sum(r["latency_ms"] for r in rag) / len(rag)
    assert rag_lat < 2000, f"RAG latency too high: {rag_lat}ms"


def test_fanuc_fixtures_jsonl_valid():
    """All 13 fixture lines must be valid JSON."""
    fixtures = SANDBOX / "fixtures" / "fanuc_knowledge.jsonl"
    assert fixtures.exists()
    lines = [l for l in fixtures.read_text().splitlines() if l.strip()]
    assert len(lines) >= 10
    for i, line in enumerate(lines, 1):
        obj = json.loads(line)
        assert "doc_id" in obj and "text" in obj
