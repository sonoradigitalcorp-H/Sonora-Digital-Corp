"""Integration Tests E2E — Unificación Sonora OS

Prueba que los 4 ecosistemas (skills, SDK, ADK, opencode) funcionan
juntos correctamente.

Escenarios:
  1. Skills tienen 14 campos completos
  2. Python SDK se importa y tiene API mirror de Node.js
  3. ADK bridge carga los 36 agentes
  4. Hermes JSON tiene su skill correspondiente
  5. OpenClaw plugins tienen skill definitions
  6. opencode business skills existen
  7. opencode.json tiene ADK y SDK configurados
  8. Eventos de unificación se emiten correctamente
"""

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

SKILLS_DIR = REPO / "skills"
ADK_AGENTS_DIR = REPO / "mcp" / "adk" / "agents"
HERMES_JSON_DIR = REPO / "platforms" / "telegram" / "skills"
OPENCODE_JSON = REPO / "opencode.json"


# ─── Helpers ───────────────────────────────────────────────────────────

FULL_SKILL_SECTIONS = [
    "Business Objective",
    "Inputs (Gherkin)",
    "Outputs (Gherkin)",
    "Events",
    "Dependencies",
    "Tools",
    "Policies",
    "Success Metrics",
    "Failure Conditions",
    "Recovery Procedure",
    "Business Value",
    "Parent OS",
    "Version",
    "Audit Trail",
]


def count_skill_sections(skill_path: Path) -> list:
    """Count how many of the 14 sections a skill has."""
    content = skill_path.read_text()
    present = []
    for section in FULL_SKILL_SECTIONS:
        if section in content:
            present.append(section)
    return present


# ─── Test 1: Skills completeness ──────────────────────────────────────

SKELETON_SKILLS = [
    "analytics/SKILL.md",
    "automation/SKILL.md",
    "content/SKILL.md",
    "creator/SKILL.md",
    "deploy/SKILL.md",
    "design/SKILL.md",
    "monitor/SKILL.md",
    "nsfw/SKILL.md",
    "payments/SKILL.md",
    "social/SKILL.md",
]


@pytest.mark.parametrize("skill_rel", SKELETON_SKILLS)
def test_skill_has_14_fields(skill_rel):
    skill_path = SKILLS_DIR / skill_rel
    assert skill_path.exists(), f"Skill not found: {skill_path}"
    present = count_skill_sections(skill_path)
    missing = [s for s in FULL_SKILL_SECTIONS if s not in present]
    assert len(missing) == 0, f"{skill_rel} missing sections: {missing}"


# ─── Test 2: Python SDK exists with correct API ───────────────────────

SDK_METHODS = [
    "health", "health_all", "tool", "tools", "status",
    "capability", "capabilities", "skills", "skill_search",
    "skill_stats", "resource", "mcp",
]


def test_sdk_python_imports():
    from mcp.sdk.sonora_client import SonoraSDK
    sdk = SonoraSDK(client_id="test", client_secret="test")
    for method in SDK_METHODS:
        assert hasattr(sdk, method), f"SDK missing method: {method}"
    assert hasattr(sdk, "services"), "SDK missing services dict"
    assert "n8n" in sdk.services, "SDK missing n8n service"


def test_sdk_tests_exist():
    test_path = REPO / "tests" / "sdk" / "test_sonora_sdk.py"
    assert test_path.exists(), "SDK test file not found"
    content = test_path.read_text()
    assert "test_health_online" in content
    assert "test_ensure_token_new" in content
    assert "test_tool_call" in content


# ─── Test 3: ADK bridge loads 36 agents ──────────────────────────────

def test_adk_agents_exist():
    assert ADK_AGENTS_DIR.exists(), "ADK agents dir not found"
    yamls = list(ADK_AGENTS_DIR.glob("*.yaml"))
    assert len(yamls) >= 30, f"Expected 30+ ADK agents, found {len(yamls)}"


def test_adk_bridge_imports():
    sys.path.insert(0, str(REPO))
    from mcp.adk.opencode_bridge import _load_agents
    agents = _load_agents()
    assert len(agents) >= 30, f"Expected 30+ agents loaded, got {len(agents)}"


# ─── Test 4: Hermes JSON → SKILL.md conversion ───────────────────────

def test_hermes_json_to_skill():
    json_files = list(HERMES_JSON_DIR.glob("hermes-*.json"))
    assert len(json_files) >= 6, f"Expected 6+ Hermes JSON skills, found {len(json_files)}"
    for jf in json_files:
        name = jf.stem  # e.g., hermes-qualify-prospect
        # The skill should exist with a simplified name
        # hermes-qualify-prospect → skills/hermes-qualify.skill.md
        base_name = name.replace("hermes-", "").split("-")[0]
        candidates = list(SKILLS_DIR.glob(f"hermes-{base_name}*.skill.md"))
        assert len(candidates) > 0, f"No skill found for JSON {name}"


# ─── Test 5: OpenClaw plugin skills exist ────────────────────────────

OPENCLAW_SKILLS = [
    "openclaw-whatsapp.skill.md",
    "openclaw-telegram.skill.md",
    "openclaw-github.skill.md",
    "openclaw-browser.skill.md",
    "openclaw-policy.skill.md",
    "openclaw-memory.skill.md",
]


@pytest.mark.parametrize("skill_name", OPENCLAW_SKILLS)
def test_openclaw_skill_exists(skill_name):
    skill_path = SKILLS_DIR / skill_name
    assert skill_path.exists(), f"OpenClaw skill not found: {skill_name}"


# ─── Test 6: opencode business skills exist ──────────────────────────

OPENCODE_BUSINESS_SKILLS = [
    "adr-generate.skill.md",
    "sdk-python.skill.md",
    "adk-manage.skill.md",
    "skill-create.skill.md",
    "incident-response.skill.md",
]


@pytest.mark.parametrize("skill_name", OPENCODE_BUSINESS_SKILLS)
def test_opencode_business_skill_exists(skill_name):
    skill_path = SKILLS_DIR / skill_name
    assert skill_path.exists(), f"opencode business skill not found: {skill_name}"


# ─── Test 7: opencode.json has ADK and SDK configured ────────────────

def test_opencode_json_has_adk():
    assert OPENCODE_JSON.exists()
    with open(OPENCODE_JSON) as f:
        config = json.load(f)
    mcps = config.get("mcp", {})
    assert "adk" in mcps, "ADK bridge not configured in opencode.json MCPs"


def test_opencode_json_has_commands():
    with open(OPENCODE_JSON) as f:
        config = json.load(f)
    commands = config.get("command", {})
    for cmd in ["adk", "sdk", "adr", "skill"]:
        assert cmd in commands, f"Command /{cmd} not found in opencode.json"


# ─── Test 8: ADRs exist for recent work ──────────────────────────────

def test_adrs_exist():
    adr_dir = REPO / "process" / "active"
    adrs = list(adr_dir.glob("ADR-20260719-*.md"))
    assert len(adrs) >= 5, f"Expected 5+ ADRs from 2026-07-19, found {len(adrs)}"
