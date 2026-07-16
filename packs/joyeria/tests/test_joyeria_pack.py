"""
Tests del pack Joyería — validan estructura, agentes, skills, tools
"""

import pytest
import yaml
from pathlib import Path

PACK_DIR = Path(__file__).parent.parent


class TestPackStructure:
    def test_pack_yaml_exists(self):
        assert (PACK_DIR / "pack.yaml").exists()

    def test_pack_yaml_valid(self):
        with open(PACK_DIR / "pack.yaml") as f:
            data = yaml.safe_load(f)
        assert data["name"] == "Joyería"
        assert len(data["agents"]) > 0
        assert len(data["skills"]) > 0
        assert len(data["tools"]) > 0

    def test_agents_dir_exists(self):
        assert (PACK_DIR / "agents").exists()

    def test_skills_dir_exists(self):
        assert (PACK_DIR / "skills").exists()

    def test_tools_dir_exists(self):
        assert (PACK_DIR / "tools").exists()

    def test_use_cases_dir_exists(self):
        assert (PACK_DIR / "use-cases").exists()


class TestAgentSalesJoyeia:
    def test_agent_file_exists(self):
        assert (PACK_DIR / "agents" / "sales-joyeria.yaml").exists()

    def test_agent_valid(self):
        with open(PACK_DIR / "agents" / "sales-joyeria.yaml") as f:
            agent = yaml.safe_load(f)
        assert agent["name"] == "sales-joyeria"
        assert agent["role"] == "sales"
        assert "prompt" in agent
        assert len(agent.get("capabilities", [])) > 0
        assert len(agent.get("skills", [])) > 0
        assert len(agent.get("tools", [])) > 0


class TestSkills:
    def test_catalogar_producto(self):
        path = PACK_DIR / "skills" / "catalogar-producto.yaml"
        assert path.exists()
        with open(path) as f:
            skill = yaml.safe_load(f)
        assert "inputs" in skill
        assert "outputs" in skill
        assert "prompt" in skill

    def test_cotizar(self):
        path = PACK_DIR / "skills" / "cotizar.yaml"
        assert path.exists()
        with open(path) as f:
            skill = yaml.safe_load(f)
        assert "inputs" in skill
        assert skill.get("name") == "joyeria/cotizar"

    def test_atender_cliente(self):
        path = PACK_DIR / "skills" / "atender-cliente.yaml"
        assert path.exists()
        with open(path) as f:
            skill = yaml.safe_load(f)
        assert "inputs" in skill
        assert skill.get("name") == "joyeria/atender-cliente"


class TestUseCases:
    def test_gherkin_files_exist(self):
        feature_dir = PACK_DIR / "use-cases"
        features = list(feature_dir.glob("*.feature"))
        assert len(features) >= 3  # venta, cotizacion, atencion-cliente

    def test_gherkin_valid(self):
        feature_dir = PACK_DIR / "use-cases"
        for feature_file in feature_dir.glob("*.feature"):
            with open(feature_file) as f:
                content = f.read()
            assert "Feature:" in content
            assert "Scenario:" in content or "Scenario Outline:" in content


class TestPackConsistency:
    def test_all_agents_have_yaml(self):
        with open(PACK_DIR / "pack.yaml") as f:
            data = yaml.safe_load(f)
        agent_names = data.get("agents", [])
        for agent_name in agent_names:
            agent_file = PACK_DIR / "agents" / f"{agent_name}.yaml"
            assert agent_file.exists(), f"Agent {agent_name} missing YAML"

    def test_all_skills_have_yaml(self):
        with open(PACK_DIR / "pack.yaml") as f:
            data = yaml.safe_load(f)
        for skill_ref in data.get("skills", []):
            skill_name = skill_ref.split("/")[-1]
            skill_file = PACK_DIR / "skills" / f"{skill_name}.yaml"
            assert skill_file.exists(), f"Skill {skill_name} missing YAML"
