import os
import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_skills_index_matches_specs():
    skills_path = os.path.join(REPO, "skills", "index.yaml")
    specs_path = os.path.join(REPO, "specs", "index.yaml")

    assert os.path.exists(skills_path)
    assert os.path.exists(specs_path)

    with open(skills_path) as f:
        skills = yaml.safe_load(f)
    with open(specs_path) as f:
        specs = yaml.safe_load(f)

    skill_ids = {c["id"] for c in skills["capabilities"]}
    spec_ids = {c["id"] for c in specs["capabilities"]}

    missing_in_specs = skill_ids - spec_ids
    missing_in_skills = spec_ids - skill_ids

    assert not missing_in_specs, f"Capabilities in skills/index.yaml but missing in specs/index.yaml: {missing_in_specs}"
    assert not missing_in_skills, f"Capabilities in specs/index.yaml but missing in skills/index.yaml: {missing_in_skills}"


def test_adrs_index_exists():
    path = os.path.join(REPO, "adrs", "README.md")
    assert os.path.exists(path), f"Missing: {path}"
