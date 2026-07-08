"""Tests para Constitution YAML — schema, integridad, reglas [HAS-001]"""
from pathlib import Path
import yaml

CONST = Path(__file__).resolve().parent.parent / "constitution"


def test_all_constitution_files_exist():
    """Verifica que existan 16 constitution files + old truth symlink"""
    files = list(CONST.glob("*.yaml"))
    assert len(files) == 16, f"Expected 16 constitution files, got {len(files)}"
    expected = [
        "00-index.yaml", "01-mission.yaml", "02-vision.yaml",
        "10-principles.yaml", "20-engineering.yaml", "30-architecture.yaml",
        "40-security.yaml", "50-quality.yaml", "60-agents.yaml",
        "70-memory.yaml", "80-events.yaml", "90-governance.yaml",
        "100-cost.yaml", "110-brand.yaml", "120-ux.yaml", "130-ethics.yaml",
    ]
    for name in expected:
        assert (CONST / name).exists(), f"Missing: {name}"


def test_constitution_schema():
    """Cada constitution file tiene version, domain, updated, rules"""
    for f in sorted(CONST.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        assert data.get("version") == 1, f"{f.name}: version != 1"
        assert "domain" in data, f"{f.name}: missing domain"
        assert "updated" in data, f"{f.name}: missing updated"
        if f.name != "00-index.yaml":
            assert "rules" in data, f"{f.name}: missing rules"
            assert isinstance(data["rules"], list), f"{f.name}: rules not a list"


def test_no_duplicate_rule_ids():
    """No hay reglas con IDs duplicados entre archivos"""
    all_rules = {}
    for f in sorted(CONST.glob("*.yaml")):
        with open(f) as fh:
            data = yaml.safe_load(fh)
        for rule in data.get("rules", []):
            rid = rule.get("id")
            if rid:
                assert rid not in all_rules, \
                    f"Duplicate rule {rid} in {f.name} and {all_rules[rid]}"
                all_rules[rid] = f.name


def test_index_catalogs_all_files():
    """00-index.yaml lista todos los archivos de la constitución"""
    with open(CONST / "00-index.yaml") as f:
        index = yaml.safe_load(f)
    indexed_files = {e["file"] for e in index.get("files", [])}
    actual_files = {f.name for f in CONST.glob("*.yaml")}
    # All actual files should be in index
    for f in actual_files:
        assert f in indexed_files, f"{f} not in index"
    # No extra entries in index
    for f in indexed_files:
        assert f in actual_files, f"{f} in index but not on disk"


def test_principles_are_immutable():
    """10-principles.yaml solo contiene reglas con severity"""
    with open(CONST / "10-principles.yaml") as f:
        data = yaml.safe_load(f)
    for rule in data.get("rules", []):
        assert rule.get("severity") in ("error", "warning"), \
            f"Rule {rule.get('id')} missing severity"


def test_architecture_rules_have_enforcement():
    """Todas las reglas de arquitectura tienen enforcement definido"""
    with open(CONST / "30-architecture.yaml") as f:
        data = yaml.safe_load(f)
    for rule in data.get("rules", []):
        assert "enforcement" in rule, \
            f"Rule {rule.get('id')} missing enforcement"


def test_engineering_has_git_and_code_rules():
    """20-engineering.yaml tiene reglas de git (GIT-NNN) y código (CODE-NNN)"""
    with open(CONST / "20-engineering.yaml") as f:
        data = yaml.safe_load(f)
    rule_ids = [r.get("id", "") for r in data.get("rules", [])]
    git_rules = [r for r in rule_ids if r.startswith("GIT-")]
    code_rules = [r for r in rule_ids if r.startswith("CODE-")]
    docs_rules = [r for r in rule_ids if r.startswith("DOC-")]
    assert len(git_rules) >= 5, f"Expected 5+ git rules, got {len(git_rules)}"
    assert len(code_rules) >= 3, f"Expected 3+ code rules, got {len(code_rules)}"


def test_governance_has_learned_rules():
    """90-governance.yaml tiene reglas aprendidas (LEARNED-NNN)"""
    with open(CONST / "90-governance.yaml") as f:
        data = yaml.safe_load(f)
    learned = [r for r in data.get("rules", [])
               if r.get("id", "").startswith("LRN-")]
    assert len(learned) >= 9, f"Expected 9+ learned rules, got {len(learned)}"


def test_level_system_in_index():
    """00-index.yaml tiene levels definidos en los files"""
    with open(CONST / "00-index.yaml") as f:
        index = yaml.safe_load(f)
    levels = {e.get("level") for e in index.get("files", [])}
    assert 0 in levels, "Level 0 (immutable) not present"
    assert 1 in levels, "Level 1 (stable) not present"
    assert 2 in levels, "Level 2 (managed) not present"
    assert 3 in levels, "Level 3 (flexible) not present"
    assert 4 in levels, "Level 4 (ephemeral) not present"


def test_truth_symlink_works():
    """El symlink truth/ → constitution/ funciona para backward compat"""
    truth_dir = Path(__file__).resolve().parent.parent / "truth"
    assert truth_dir.is_symlink(), "truth/ is not a symlink"
    assert truth_dir.resolve() == CONST.resolve(), \
        f"truth/ points to {truth_dir.resolve()}, expected {CONST.resolve()}"
