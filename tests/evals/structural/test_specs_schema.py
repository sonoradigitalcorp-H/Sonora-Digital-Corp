import os
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


SPECS_DIR = os.path.join("process", "specs")


def test_specs_index_exists():
    path = os.path.join(REPO, SPECS_DIR, "index.yaml")
    assert os.path.exists(path), f"Missing: {path}"


def test_specs_index_valid_yaml():
    path = os.path.join(REPO, SPECS_DIR, "index.yaml")
    with open(path) as f:
        data = yaml.safe_load(f)
    assert "capabilities" in data
    assert len(data["capabilities"]) > 0


def test_specs_schema_exists():
    path = os.path.join(REPO, SPECS_DIR, "schema", "spec-v1.yaml")
    assert os.path.exists(path)


def test_all_capabilities_have_specs():
    index_path = os.path.join(REPO, SPECS_DIR, "index.yaml")
    with open(index_path) as f:
        index = yaml.safe_load(f)

    for cap in index["capabilities"]:
        spec_path = os.path.join(REPO, "process", cap["path"], "spec.md") if not cap["path"].startswith("process/") else os.path.join(REPO, cap["path"], "spec.md")
        assert os.path.exists(spec_path), f"Missing spec for {cap['id']}: {spec_path}"


def test_all_capabilities_have_gherkin():
    index_path = os.path.join(REPO, SPECS_DIR, "index.yaml")
    with open(index_path) as f:
        index = yaml.safe_load(f)

    for cap in index["capabilities"]:
        gherkin_dir = os.path.join(REPO, cap["path"], "gherkin")
        if os.path.exists(gherkin_dir):
            feature_files = [f for f in os.listdir(gherkin_dir) if f.endswith(".feature")]
            if cap["status"] == "active":
                assert len(feature_files) > 0, f"Missing Gherkin for active capability: {cap['id']}"
