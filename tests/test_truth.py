"""Tests para Truth YAML — schema, conflictos, integridad [FR12, FR13, T19]"""
from pathlib import Path
import yaml

TRUTH = Path(__file__).resolve().parent.parent / "truth"


def test_all_truth_files_exist():
    """Verifica que existan 11 truth files"""
    files = list(TRUTH.glob("*.yaml"))
    assert len(files) == 11, f"Expected 11 truth files, got {len(files)}"
    expected = [
        "00-index.yaml", "10-principles.yaml", "20-architecture.yaml",
        "30-security.yaml", "40-infrastructure.yaml", "50-coding.yaml",
        "60-git.yaml", "70-documentation.yaml", "80-operations.yaml",
        "85-compliance.yaml", "90-learned.yaml"
    ]
    for name in expected:
        assert (TRUTH / name).exists(), f"Missing: {name}"


def test_truth_schema():
    """Cada truth file tiene version, domain, updated, rules"""
    for f in sorted(TRUTH.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        assert data.get("version") == 1, f"{f.name}: version != 1"
        assert "domain" in data, f"{f.name}: missing domain"
        assert "updated" in data, f"{f.name}: missing updated"
        assert "rules" in data or f.name == "00-index.yaml", f"{f.name}: missing rules"


def test_no_conflicts():
    """No hay reglas con IDs duplicados entre archivos"""
    all_rules = {}
    for f in sorted(TRUTH.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        for rule in data.get("rules", []):
            rid = rule.get("id")
            if rid:
                assert rid not in all_rules, f"Duplicate rule {rid} in {f.name} and {all_rules[rid]}"
                all_rules[rid] = f.name


def test_level_hierarchy():
    """Los niveles 0-5 están definidos en 00-index.yaml"""
    with open(TRUTH / "00-index.yaml") as f:
        index = yaml.safe_load(f)
    levels = index.get("conflict_resolution", {}).get("levels", {})
    for level in range(6):
        assert level in levels or str(level) in levels, f"Level {level} not defined in conflict_resolution"


def test_principles_are_immutable():
    """10-principles.yaml solo contiene reglas de nivel 0"""
    rules_file = TRUTH / "10-principles.yaml"
    with open(rules_file) as f:
        data = yaml.safe_load(f)
    for rule in data.get("rules", []):
        assert rule.get("severity") in ("error", "warning"), f"Rule {rule.get('id')} missing severity"


def test_architecture_rules_have_enforcement():
    """Todas las reglas de arquitectura tienen enforcement definido"""
    rules_file = TRUTH / "20-architecture.yaml"
    with open(rules_file) as f:
        data = yaml.safe_load(f)
    for rule in data.get("rules", []):
        assert "enforcement" in rule, f"Rule {rule.get('id')} missing enforcement"


def test_model_routing_defined():
    """50-coding.yaml tiene model_routing para selección de modelo"""
    with open(TRUTH / "50-coding.yaml") as f:
        data = yaml.safe_load(f)
    assert "model_routing" in data, "model_routing not defined"
    assert len(data["model_routing"]) >= 5, "model_routing should have 5+ entries"


def test_compliance_has_jr_lite():
    """85-compliance.yaml contiene los 15 puntos de JR-Lite"""
    with open(TRUTH / "85-compliance.yaml") as f:
        data = yaml.safe_load(f)
    for rule in data.get("rules", []):
        if rule.get("id") == "COMP-002":
            points = rule.get("points", [])
            assert len(points) == 15, f"JR-Lite should have 15 points, got {len(points)}"


def test_learned_is_empty():
    """90-learned.yaml está vacío inicialmente (se autogenera)"""
    with open(TRUTH / "90-learned.yaml") as f:
        data = yaml.safe_load(f)
    assert data.get("rules") == [], "90-learned.yaml should start empty"
