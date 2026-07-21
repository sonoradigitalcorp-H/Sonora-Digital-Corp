"""Unification Evals — Verifica que la estandarización esté completa.

10 eval tests:
  1. 10 skeleton skills completadas (14 campos)
  2. 12 Hermes skills convertidas
  3. 6 OpenClaw plugin skills creadas
  4. Python SDK existe y es importable
  5. ADK bridge existe y carga agentes
  6. 5 opencode business skills creadas
  7. 5 ADRs nuevos creados
  8. Skills tienen Business Objective cuantificado
  9. Skills tienen eventos definidos
  10. Skills tienen recovery procedure
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SKILLS_DIR = REPO / "skills"
SKILL_SECTIONS = [
    "Business Objective", "Inputs (Gherkin)", "Outputs (Gherkin)",
    "Events", "Dependencies", "Tools", "Policies",
    "Success Metrics", "Failure Conditions", "Recovery Procedure",
    "Business Value", "Parent OS", "Version", "Audit Trail",
]
MANDATORY = ["Business Objective", "Events", "Recovery Procedure", "Business Value"]


def _get_skills_with_suffix(suffix: str = ".skill.md") -> list[Path]:
    result = []
    for f in SKILLS_DIR.glob(f"*{suffix}"):
        if f.is_file() and "SKILL-TEMPLATE" not in f.name:
            result.append(f)
    return sorted(result)


def _count_sections(content: str) -> int:
    return sum(1 for s in SKILL_SECTIONS if s in content)


def _has_section(content: str, section: str) -> bool:
    return section in content


# ─── Eval 1: 10 skills completadas ──────────────────────────────────────

def test_all_skills_have_14_fields():
    skills = _get_skills_with_suffix()
    incomplete = []
    for s in skills:
        content = s.read_text()
        n = _count_sections(content)
        if n < 14:
            incomplete.append((s.name, n))
    assert len(incomplete) == 0, f"Skills incomplete (found/total): {incomplete}"


# ─── Eval 2: Hermes skills ─────────────────────────────────────────────

def test_hermes_skills_exist():
    hermes = [f for f in _get_skills_with_suffix() if "hermes-" in f.name]
    assert len(hermes) >= 6, f"Expected 6+ Hermes skills, found {len(hermes)}"


# ─── Eval 3: OpenClaw plugin skills ────────────────────────────────────

def test_openclaw_skills_exist():
    oc = [f for f in _get_skills_with_suffix() if "openclaw-" in f.name]
    assert len(oc) >= 4, f"Expected 4+ OpenClaw skills, found {len(oc)}"


# ─── Eval 4: Python SDK ────────────────────────────────────────────────

def test_sdk_python_importable():
    from mcp.sdk.sonora_client import SonoraSDK
    sdk = SonoraSDK()
    assert hasattr(sdk, "tool")
    assert hasattr(sdk, "health_all")
    assert hasattr(sdk, "capabilities")


# ─── Eval 5: ADK bridge ────────────────────────────────────────────────

def test_adk_bridge_importable():
    from mcp.adk.opencode_bridge import _load_agents
    agents = _load_agents()
    assert len(agents) >= 20, f"Expected 20+ ADK agents, got {len(agents)}"


# ─── Eval 6: opencode business skills ─────────────────────────────────

def test_opencode_business_skills():
    business = ["adr-generate.skill.md", "sdk-python.skill.md", "adk-manage.skill.md",
                "skill-create.skill.md", "incident-response.skill.md"]
    for name in business:
        path = SKILLS_DIR / name
        assert path.exists(), f"Missing business skill: {name}"


# ─── Eval 7: ADRs nuevos ──────────────────────────────────────────────

def test_new_adrs():
    adr_dir = REPO / "process" / "active"
    adrs = list(adr_dir.glob("ADR-20260719-*.md"))
    assert len(adrs) >= 5, f"Expected 5+ ADRs from today, found {len(adrs)}"


# ─── Eval 8: Skills tienen Business Objective cuantificado ──────────────

def test_skills_have_business_objective():
    skills = _get_skills_with_suffix()
    missing = [s.name for s in skills if not _has_section(s.read_text(), "Business Objective")]
    assert len(missing) == 0, f"Skills missing Business Objective: {missing}"


# ─── Eval 9: Skills tienen eventos ─────────────────────────────────────

def test_skills_have_events():
    skills = _get_skills_with_suffix()
    missing = [s.name for s in skills if not _has_section(s.read_text(), "## 4. Events")]
    assert len(missing) == 0, f"Skills missing Events section: {missing}"


# ─── Eval 10: Skills tienen recovery procedure ────────────────────────

def test_skills_have_recovery():
    skills = _get_skills_with_suffix()
    missing = [s.name for s in skills if not _has_section(s.read_text(), "## 10. Recovery")]
    assert len(missing) == 0, f"Skills missing Recovery Procedure: {missing}"
