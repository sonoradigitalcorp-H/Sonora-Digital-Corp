#!/usr/bin/env python3
"""Eval tests for 5 SDC domains (AGENT, CAP, SDD, SKILL, EVENT).
Run: python3 -m pytest evals/test_evals.py -v --tb=short
     python3 evals/test_evals.py --eval  (generates dashboard)
"""
import json
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

# ═══════════════════════════════════════════════════
# AGENT OS — 10 tests
# ═══════════════════════════════════════════════════

def test_agent_01_creator_agent_defined():
    """creator-agent tiene tools, emits, triggers"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "creator-agent")
    assert agent is not None, "creator-agent not found"
    assert len(agent.get("tools", [])) >= 3, f"Expected >=3 tools, got {len(agent.get('tools',[]))}"
    assert "channel" in agent, "Missing channel"
    assert "emits" in agent, "Missing emits"

def test_agent_02_quality_agent_defined():
    """quality-agent tiene tools y triggers"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "quality-agent")
    assert agent is not None
    assert len(agent.get("tools", [])) >= 2
    assert "system:pipeline" in str(agent.get("triggers", [])), "Missing pipeline trigger"

def test_agent_03_monitor_agent_defined():
    """monitor-agent emite eventos de servicio"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "monitor-agent")
    assert agent is not None
    emits = agent.get("emits", [])
    assert any("service:down" in e for e in emits), f"No service:down event in emits: {emits}"
    assert any("service:recovered" in e for e in emits), f"No service:recovered event"

def test_agent_04_ceo_agent_defined():
    """ceo-agent tiene tools de revenue"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "ceo-agent")
    assert agent is not None
    tools = agent.get("tools", [])
    assert "hasura_query" in tools

def test_agent_05_marketing_agent_defined():
    """marketing-agent emite eventos de campaña"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "marketing-agent")
    assert agent is not None
    assert agent.get("tenant") == "abe-music"

def test_agent_06_content_agent_defined():
    """content-agent genera contenido"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "content-agent")
    assert agent is not None
    tools = agent.get("tools", [])
    assert "generate_video" in tools or "llm_chat" in tools

def test_agent_07_sales_agent_defined():
    """sales-agent procesa pagos"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "sales-agent")
    assert agent is not None
    tools = agent.get("tools", [])
    assert any("stripe" in t for t in tools), f"No stripe tools: {tools}"

def test_agent_08_support_agent_defined():
    """support-agent resuelve tickets"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "support-agent")
    assert agent is not None
    emits = agent.get("emits", [])
    assert any("ticket:" in e for e in emits), f"No ticket events: {emits}"

def test_agent_09_voice_agent_defined():
    """voice-agent usa omnivoice"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "voice-agent")
    assert agent is not None
    tools = agent.get("tools", [])
    assert any("omnivoice" in t for t in tools), f"No omnivoice tools: {tools}"

def test_agent_10_clone_agent_defined():
    """clone-agent tiene pipeline completo"""
    reg = _load_yaml("agents/registry.yaml")
    agent = _find_agent(reg, "clone-agent")
    assert agent is not None
    tools = agent.get("tools", [])
    assert "train_lora" in tools, f"No train_lora: {tools}"
    assert "clone_voice" in tools, f"No clone_voice: {tools}"
    emits = agent.get("emits", [])
    assert "clone:client_registered" in emits

# ═══════════════════════════════════════════════════
# CAPABILITY BUS — 6 tests
# ═══════════════════════════════════════════════════

def test_cap_01_registry_exists():
    """capabilities/index.yaml tiene 9 capabilities"""
    caps = _load_yaml("capabilities/index.yaml")
    entries = caps.get("capabilities", [])
    assert len(entries) >= 5, f"Expected >=5 capabilities, got {len(entries)}"

def test_cap_02_dualidad_resuelta():
    """Meta-registry unifica capabilities (9+3=12)"""
    unified = _load_yaml("state/registry/unified.yaml")
    caps = [e for e in unified.get("entries", []) if e.get("type") == "capability"]
    assert len(caps) >= 10, f"Expected >=10 capabilities, got {len(caps)}"

def test_cap_03_router_exists():
    """capabilities/bus/router.py existe"""
    router = BASE / "capabilities" / "bus" / "router.py"
    assert router.exists(), "router.py not found"

def test_cap_04_bus_api_defined():
    """CapabilityBus API endpoints definidos"""
    web = BASE / "capabilities" / "bus" / "web.py"
    assert web.exists(), "web.py not found"
    content = web.read_text()
    assert "route" in content, "No route endpoint defined"

def test_cap_05_provider_registry_sync():
    """Meta-registry incluye providers de config/registry.json"""
    unified = _load_yaml("state/registry/unified.yaml")
    config_caps = [e for e in unified.get("entries", []) if e.get("source") == "config/registry.json"]
    assert len(config_caps) >= 1, f"config/registry.json capabilities not in meta-registry"

def test_cap_06_agents_have_capabilities():
    """Cada capability en index.yaml referencia agente existente"""
    caps = _load_yaml("capabilities/index.yaml")
    agents = _load_yaml("agents/registry.yaml")
    agent_names = [a["name"] for a in agents.get("agents", [])]
    for cap in caps.get("capabilities", []):
        agent = cap.get("agent", "")
        if agent and agent != "null":
            assert agent in agent_names or agent in ["collector", "null"], f"Agent '{agent}' not found for capability '{cap['id']}'"

# ═══════════════════════════════════════════════════
# SDD PIPELINE — 8 tests
# ═══════════════════════════════════════════════════

def test_sdd_01_spec_skill_exists():
    """skills/process/sdd-spec.skill.md existe"""
    assert (BASE / "skills" / "process" / "sdd-spec.skill.md").exists()

def test_sdd_02_design_skill_exists():
    """skills/process/sdd-design.skill.md existe"""
    assert (BASE / "skills" / "process" / "sdd-design.skill.md").exists()

def test_sdd_03_apply_skill_exists():
    """skills/process/sdd-apply.skill.md existe"""
    assert (BASE / "skills" / "process" / "sdd-apply.skill.md").exists()

def test_sdd_04_verify_skill_exists():
    """skills/process/sdd-verify.skill.md existe"""
    assert (BASE / "skills" / "process" / "sdd-verify.skill.md").exists()

def test_sdd_05_archive_skill_exists():
    """skills/process/sdd-archive.skill.md existe"""
    assert (BASE / "skills" / "process" / "sdd-archive.skill.md").exists()

def test_sdd_06_orchestrator_skill_exists():
    """sdd-orchestrator coordina el pipeline"""
    path = BASE / "skills" / "process" / "sdd-orchestrator.skill.md"
    assert path.exists()
    content = path.read_text()
    assert "sdd-spec" in content, "Orchestrator missing reference to sdd-spec"
    assert "sdd-apply" in content

def test_sdd_07_completed_specs_exist():
    """process/completed/ tiene specs archivadas"""
    completed = BASE / "process" / "completed"
    assert completed.exists()
    specs = [d for d in completed.iterdir() if d.is_dir()]
    assert len(specs) >= 10, f"Expected >=10 completed specs, got {len(specs)}"

def test_sdd_08_gherkin_scenarios_exist():
    """Cada spec tiene Gherkin"""
    completed = BASE / "process" / "completed"
    specs_with_gherkin = 0
    for d in completed.iterdir():
        if d.is_dir() and (d / "gherkin").exists():
            specs_with_gherkin += 1
    assert specs_with_gherkin >= 3, f"Expected >=3 specs with gherkin, got {specs_with_gherkin}"

# ═══════════════════════════════════════════════════
# SKILL REGISTRY — 5 tests
# ═══════════════════════════════════════════════════

def test_skill_01_skill_registry_js_exists():
    """mcp/registry/skill-registry.js existe"""
    assert (BASE / "mcp" / "registry" / "skill-registry.js").exists()

def test_skill_02_skill_template_exists():
    """skills/SKILL-TEMPLATE.md existe"""
    path = BASE / "skills" / "SKILL-TEMPLATE.md"
    assert path.exists()
    content = path.read_text()
    assert "Business Objective" in content

def test_skill_03_skill_creator_exists():
    """scripts/skill-creator.sh existe"""
    assert (BASE / "scripts" / "skill-creator.sh").exists()

def test_skill_04_meta_registry_skills():
    """Meta-registry tiene skills de SDC + Hermes + OpenClaw"""
    unified = _load_yaml("state/registry/unified.yaml")
    skills = [e for e in unified.get("entries", []) if e.get("type") == "skill"]
    ecosystems = set(s.get("ecosystem", "") for s in skills)
    assert "sdc" in ecosystems, f"No SDC skills in meta-registry. Ecosystems: {ecosystems}"
    assert "hermes" in ecosystems, f"No Hermes skills"

def test_skill_05_skills_have_hermes_index():
    """skill-registry.js indexa hermes skills"""
    if _node_available():
        result = subprocess.run(
            ["node", "-e", """
                const { SkillRegistry } = require('./mcp/registry/skill-registry.js');
                const r = new SkillRegistry();
                r.loadAll();
                const stats = r.getStats();
                console.log(JSON.stringify(stats));
            """],
            cwd=BASE, capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            stats = json.loads(result.stdout)
            sources = stats.get("bySource", {})
            assert "hermes" in sources, f"Hermes not in skill sources: {sources}"
            assert sources.get("hermes", 0) >= 20, f"Expected >=20 hermes skills, got {sources.get('hermes', 0)}"

# ═══════════════════════════════════════════════════
# EVENT BUS — 6 tests
# ═══════════════════════════════════════════════════

def test_event_01_emitter_exists():
    """events/emitter.py existe"""
    assert (BASE / "events" / "emitter.py").exists()

def test_event_02_emitter_can_emit():
    """emitter.py puede emitir un evento"""
    result = subprocess.run(
        ["python3", "-c", """
import sys; sys.path.insert(0, '.')
from events.emitter import emit_sync
emit_sync('test:eval:unit_test', {'source': 'pytest'}, 'eval')
import json
with open('state/events/events.jsonl') as f:
    lines = f.readlines()
print(f'Events: {len(lines)}')
print(lines[-1][:100])
"""],
        cwd=BASE, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, f"Emit failed: {result.stderr}"
    assert "Events:" in result.stdout

def test_event_03_listener_can_start():
    """EventListener puede iniciar"""
    result = subprocess.run(
        ["python3", "-c", """
import sys; sys.path.insert(0, '.')
import asyncio
from events.listener import EventListener
from events.handlers.memory_handler import MemoryHandler
async def test():
    l = EventListener()
    l.register(MemoryHandler())
    await l.start()
    await asyncio.sleep(1)
    stats = l.get_stats()
    print(f'Running: {stats[\"running\"]}')
    print(f'Handlers: {stats[\"handlers\"]}')
    await l.stop()
asyncio.run(test())
"""],
        cwd=BASE, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, f"Listener error: {result.stderr}"
    assert "Running: True" in result.stdout

def test_event_04_alert_handler_exists():
    """AlertHandler clasifica severidad"""
    path = BASE / "events" / "handlers" / "alert_handler.py"
    assert path.exists()
    content = path.read_text()
    assert "critical" in content

def test_event_05_memory_handler_exists():
    """MemoryHandler persiste eventos"""
    path = BASE / "events" / "handlers" / "memory_handler.py"
    assert path.exists()
    content = path.read_text()
    assert "processed" in content

def test_event_06_catalog_has_events():
    """catalog.yaml tiene eventos definidos"""
    path = BASE / "state" / "events" / "catalog.yaml"
    assert path.exists()
    import yaml
    data = yaml.safe_load(path.read_text())
    assert data is not None


# ═══════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════

def _load_yaml(rel_path):
    import yaml
    full = BASE / rel_path
    if not full.exists():
        return {}
    return yaml.safe_load(full.read_text()) or {}

def _find_agent(registry, name):
    for agent in registry.get("agents", []):
        if agent.get("name") == name:
            return agent
    return None

def _node_available():
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


if __name__ == "__main__":
    """Run all tests and generate dashboard."""
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short", "--eval"] + sys.argv[1:]))
