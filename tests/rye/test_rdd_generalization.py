"""Structural tests for Sprint 4: RDD script generalization + kill switch + gate."""
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RDD = os.path.join("scripts", "rdd")


def _read(path):
    with open(os.path.join(REPO, RDD, path)) as f:
        return f.read()


def test_lib_sh_exists_and_sourced():
    assert os.path.exists(os.path.join(REPO, RDD, "lib.sh"))


def test_lib_sh_has_generic_dirs():
    content = _read("lib.sh")
    assert "RDD_ROOT" in content
    assert "RDD_APP_DIR" in content
    assert "RDD_FREEZE_DIR" in content


def test_no_hardcoded_agentic_os_paths():
    for script in ["freeze.sh", "validate.sh", "review.sh", "fix.sh", "receipt.sh", "commit.sh"]:
        content = _read(script)
        assert "agentic-os" not in content, f"{script} still hardcodes agentic-os"
        assert "sonora-digital-corp/.rdd" not in content, f"{script} hardcodes freeze dir"


def test_scripts_source_lib_sh():
    for script in ["freeze.sh", "validate.sh", "review.sh", "fix.sh", "receipt.sh", "commit.sh",
                   "run.sh"]:
        content = _read(script)
        assert 'source "$SCRIPT_DIR/lib.sh"' in content, f"{script} does not source lib.sh"


def test_killswitch_exists_and_enabled():
    path = os.path.join(REPO, ".rdd", "killswitch.json")
    assert os.path.exists(path), "Missing .rdd/killswitch.json"
    with open(path) as f:
        data = json.load(f)
    assert data.get("enabled") in (True, "true"), "killswitch should be enabled by default"
    assert "reason" in data and "activated_at" in data


def test_commit_script_respects_killswitch():
    content = _read("commit.sh")
    assert "rdd_gate_enabled" in content
    assert "rdd_require_gate" in content
    assert "Kill switch active" in content


def test_run_script_has_all_actions():
    content = _read("run.sh")
    for action in ["freeze", "review", "fix", "validate", "receipt", "commit", "full", "gate"]:
        assert action in content, f"run.sh missing action guard: {action}"
