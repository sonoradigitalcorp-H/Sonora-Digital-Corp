"""
Tests base para el pack {business_type}.
"""

import pytest
import yaml
from pathlib import Path

PACK_DIR = Path(__file__).parent.parent


def test_pack_yaml_exists():
    assert (PACK_DIR / "pack.yaml").exists()


def test_pack_yaml_is_valid():
    with open(PACK_DIR / "pack.yaml") as f:
        data = yaml.safe_load(f)
    assert "name" in data
    assert "agents" in data
    assert "skills" in data
    assert "tools" in data


def test_agents_defined():
    with open(PACK_DIR / "pack.yaml") as f:
        data = yaml.safe_load(f)
    for agent in data.get("agents", []):
        name = agent if isinstance(agent, str) else agent.get("nombre-agente")
        assert (PACK_DIR / "agents" / f"{name}.yaml").exists(), f"Agent {name} missing"


def test_skills_defined():
    agents_dir = PACK_DIR / "skills"
    if agents_dir.exists():
        files = list(agents_dir.glob("*.yaml"))
        assert len(files) > 0, "No skill files found"
