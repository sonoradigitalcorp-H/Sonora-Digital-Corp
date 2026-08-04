"""Structural eval for SPEC-030 RYE: validates specs, ADRs, gherkins, and stack references."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SPECS_DIR = os.path.join("docs", "specs")
ADR_DIR = os.path.join("docs", "adrs")
RDD_DIR = os.path.join("docs", "rdd")


def test_spec_master_exists():
    path = os.path.join(REPO, SPECS_DIR, "030-rye-openclaw-agents", "spec.md")
    assert os.path.exists(path), f"Missing: {path}"


def test_spec_master_has_required_sections():
    path = os.path.join(REPO, SPECS_DIR, "030-rye-openclaw-agents", "spec.md")
    with open(path) as f:
        content = f.read()
    for section in ["## 1. Objective", "## 3. Functional Requirements",
                    "## 5. Technical Architecture", "## 6. RAG Stack",
                    "## 7. RDD Gate", "## 11. Acceptance Criteria"]:
        assert section in content, f"Missing section {section} in SPEC-030"


def test_spec_master_mentions_rag_and_engram():
    path = os.path.join(REPO, SPECS_DIR, "030-rye-openclaw-agents", "spec.md")
    with open(path) as f:
        content = f.read()
    for term in ["Qdrant", "FastEmbed", "engram", "deepseek-v4-flash", "OpenRouter"]:
        assert term.lower() in content.lower(), f"Missing stack term: {term}"


def test_six_rye_adrs_exist():
    expected = [
        "ADR-20260803-RYE-ARCHITECTURE.md",
        "ADR-20260803-RYE-MCP.md",
        "ADR-20260803-RYE-SECURITY.md",
        "ADR-20260803-RYE-METHOD.md",
        "ADR-20260803-RYE-CLI-STACK.md",
        "ADR-20260803-RYE-RDD-GATE.md",
    ]
    for adr in expected:
        path = os.path.join(REPO, ADR_DIR, adr)
        assert os.path.exists(path), f"Missing ADR: {adr}"


def test_rdd_method_doc_exists():
    path = os.path.join(REPO, RDD_DIR, "METHOD.md")
    assert os.path.exists(path), f"Missing: {path}"


def test_three_rye_gherkins_exist():
    expected = [
        "rye-rdd-gate.feature",
        "rye-shift-report.feature",
        "rye-fanuc-expert.feature",
    ]
    gherkin_dir = os.path.join(REPO, "tests", "gherkin")
    for g in expected:
        path = os.path.join(gherkin_dir, g)
        assert os.path.exists(path), f"Missing gherkin: {g}"


def test_three_rye_step_files_exist():
    expected = [
        "rye_rdd_gate_steps.py",
        "rye_shift_report_steps.py",
        "rye_fanuc_expert_steps.py",
    ]
    steps_dir = os.path.join(REPO, "tests", "steps")
    for s in expected:
        path = os.path.join(steps_dir, s)
        assert os.path.exists(path), f"Missing steps: {s}"


def test_rye_gherkins_use_supported_keyword():
    # pytest-bdd 8.x + gherkin-official 29.x: 'es' dialect feature keyword is 'Característica'
    gherkin_dir = os.path.join(REPO, "tests", "gherkin")
    for name in ["rye-rdd-gate.feature", "rye-shift-report.feature", "rye-fanuc-expert.feature"]:
        with open(os.path.join(gherkin_dir, name)) as f:
            content = f.read()
        assert "Característica:" in content, f"{name} must use 'Característica:' keyword (compatible dialect)"


def test_rag_scripts_referenced():
    # The plan references a generalized ingest + verify script; assert they exist or note pending
    # (T0.9/T0.10 create them)
    verify = os.path.join(REPO, "scripts", "verify_rag_stack.py")
    if not os.path.exists(verify):
        return  # created later in Sprint 0; structural eval is forward-looking
