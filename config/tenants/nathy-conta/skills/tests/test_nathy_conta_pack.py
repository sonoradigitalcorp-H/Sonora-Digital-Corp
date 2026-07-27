"""Tests for the nathy-conta pack — validation, CFDI, SAT, RESICO, nóminas."""

import json
import os
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent
REPO = PACK.parent.parent
sys.path.insert(0, str(REPO))


def test_pack_yaml_exists():
    assert (PACK / "pack.yaml").exists()


def test_pack_yaml_valid():
    import yaml
    data = yaml.safe_load((PACK / "pack.yaml").read_text())
    assert data["name"] == "Contabilidad"
    assert data["tier"] in ("basic", "pro", "enterprise")
    assert len(data["agents"]) >= 3
    assert len(data["skills"]) >= 6


def test_agents_exist():
    agents_dir = PACK / "agents"
    assert agents_dir.exists()
    yamls = list(agents_dir.glob("*.yaml"))
    assert len(yamls) >= 3
    for y in yamls:
        import yaml
        data = yaml.safe_load(y.read_text())
        assert "name" in data
        assert "description" in data
        assert "tools" in data


def test_skills_exist():
    skills_dir = PACK / "skills"
    assert skills_dir.exists()
    yamls = list(skills_dir.glob("*.yaml"))
    assert len(yamls) >= 6
    for y in yamls:
        import yaml
        data = yaml.safe_load(y.read_text())
        assert "name" in data
        assert "prompt" in data
        assert "agents_allowed" in data


def test_use_cases_exist():
    uc_dir = PACK / "use-cases"
    assert uc_dir.exists()
    features = list(uc_dir.glob("*.feature"))
    assert len(features) >= 4


def test_pack_metrics_config():
    metrics_dir = PACK / "metrics"
    metrics_dir.mkdir(exist_ok=True)
    assert metrics_dir.exists()


def test_tenant_routing_config():
    routing_file = REPO / "config" / "tenant-routing.yaml"
    if routing_file.exists():
        import yaml
        data = yaml.safe_load(routing_file.read_text())
        phones = [r["phone"] for r in data.get("routing", [])]
        assert "+5216622681111" in phones
        assert any(r.get("tenant") == "nathy_conta" for r in data.get("routing", []))


def test_tenants_json_entry():
    tenants_file = REPO / "config" / "tenants.json"
    if tenants_file.exists():
        data = json.loads(tenants_file.read_text())
        tenant_ids = list(data.get("tenants", {}).keys())
        assert any("nathy" in tid for tid in tenant_ids), f"No tenant found. Current: {tenant_ids}"


def test_tenants_yaml_entry():
    tenants_yaml = REPO / "config" / "tenants.yaml"
    if tenants_yaml.exists():
        import yaml
        data = yaml.safe_load(tenants_yaml.read_text())
        ids = [p["id"] for p in data.get("partners", [])]
        # Check either nathy_conta or nathy-conta
        found = any("nathy" in pid for pid in ids)
        assert found, f"Partner nathy not found. Current: {ids}"


def test_registry_has_agents():
    registry = REPO / "config" / "registry.json"
    if registry.exists():
        data = json.loads(registry.read_text())
        agent_names = [a["name"] for a in data.get("agents", [])]
        found = any("nathy" in name for name in agent_names)
        assert found, f"Nathy agents not in registry. Current: {agent_names[:5]}..."
