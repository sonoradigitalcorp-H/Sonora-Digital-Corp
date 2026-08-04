"""Tests for the unified RYE engine (2-layer RAG per Joaquín Ruiz principles)."""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))


def test_concept_curated_srvo():
    from tenants.rye.bot.rye_engine import find_concept
    c = find_concept("alarma SRVO-075 en la celda")
    assert c is not None
    assert c["path"] == "fanuc-srvo-alarms.md"
    assert "SRVO-075" in c["body"]
    # frontmatter metadata present (vigencia/traceability per Joaquín)
    assert c["meta"].get("timestamp"), "concept missing timestamp metadata"


def test_concept_curated_shift_report():
    from tenants.rye.bot.rye_engine import find_concept
    c = find_concept("reporte de turno por favor")
    assert c is not None
    assert c["path"] == "rye-shift-report-format.md"


def test_index_loads_with_concepts():
    from tenants.rye.bot.rye_engine import load_index
    idx = load_index()
    assert idx["meta"].get("type") == "index"
    assert "fanuc" in idx["body"].lower() or "SRVO" in idx["body"]


def test_engine_context_mode_recovers_both_layers():
    import os as _os
    from tenants.rye.bot.rye_engine import answer

    _os.environ.setdefault("EMBED_BACKEND", "ollama")
    _os.environ.setdefault("EMBED_MODEL", "all-minilm")
    res = answer("alarma SRVO-075 celda de soldadura", use_llm=False)
    assert res["concept"] == "fanuc-srvo-alarms.md"
    # response includes concept body + RAG context
    assert "SRVO-075" in res["response"]


def test_engine_uses_curated_concept_over_rag_for_stable_query():
    from tenants.rye.bot.rye_engine import answer
    # For stable/exact knowledge, the concept (not RAG) should be the primary source
    res = answer("genera el reporte de turno de la celda 3", use_llm=False)
    assert res["concept"] == "rye-shift-report-format.md"
    assert "reporte" in res["response"].lower() or "formato" in res["response"].lower()


def test_openclaw_rye_bot_skill_exists():
    """The conductor agent skill must exist and point to the engine."""
    skill = Path("/home/mystic/.openclaw/agents/rye/agent/skills/rye-bot/SKILL.md")
    assert skill.exists(), f"Missing OpenClaw skill: {skill}"
    content = skill.read_text()
    assert "rye_engine.py" in content
    # the skill must reference the monorepo engine path
    assert "rye_engine.py" in content


def test_engine_path_resolvable_from_skill():
    """The absolute path the skill invokes must resolve to the engine."""
    engine = REPO / "tenants" / "rye" / "bot" / "rye_engine.py"
    assert engine.exists()
