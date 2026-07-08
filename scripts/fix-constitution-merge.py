#!/usr/bin/env python3
"""Fix merged constitution files — semantically merge rules from old truth/ files."""
import yaml
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OLD = REPO / "truth.bak"
NEW = REPO / "constitution"

# Mapping: old_file -> new_file
MERGE_MAP = {
    "00-index.yaml": "00-index.yaml",
    "10-principles.yaml": "10-principles.yaml",
    "20-architecture.yaml": "30-architecture.yaml",
    "30-security.yaml": "40-security.yaml",
    "40-infrastructure.yaml": "30-architecture.yaml",
    "45-execution.yaml": "90-governance.yaml",
    "50-coding.yaml": "20-engineering.yaml",
    "60-git.yaml": "20-engineering.yaml",
    "70-documentation.yaml": "20-engineering.yaml",
    "80-operations.yaml": "90-governance.yaml",
    "85-compliance.yaml": "90-governance.yaml",
    "90-learned.yaml": "90-governance.yaml",
}

def load_rules(path):
    """Load rules from a YAML file."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])
    except Exception:
        return []

def merge():
    # Collect all rules per target file
    target_rules: dict[str, list] = {}

    # Load existing rules in new files (already created with skeleton)
    for new_file in sorted(NEW.glob("*.yaml")):
        if new_file.stem == "00-index.yaml":
            continue
        rules = load_rules(new_file)
        target_rules[new_file.name] = rules

    # Merge rules from old truth files
    for old_name, new_name in MERGE_MAP.items():
        old_path = OLD / old_name
        if not old_path.exists():
            print(f"  SKIP {old_name} (not found in truth.bak/)")
            continue
        old_rules = load_rules(old_path)
        if not old_rules:
            print(f"  SKIP {old_name} (no rules)")
            continue
        print(f"  {old_name} → {new_name}: {len(old_rules)} rules")

        # Add rules, avoiding duplicates by rule ID
        existing_ids = {r.get("id") for r in target_rules.get(new_name, [])}
        for rule in old_rules:
            rid = rule.get("id")
            if rid and rid not in existing_ids:
                target_rules.setdefault(new_name, []).append(rule)
                existing_ids.add(rid)
            elif rid:
                print(f"    SKIP duplicate rule: {rid}")

    # Write back new files
    for new_name, rules in target_rules.items():
        new_path = NEW / new_name
        if new_name == "00-index.yaml":
            continue  # index is special
        existing = yaml.safe_load(new_path.read_text())
        existing["rules"] = rules
        existing["updated"] = "2026-07-08T20:00:00Z"
        with open(new_path, "w") as f:
            yaml.dump(existing, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"  WROTE {new_name}: {len(rules)} rules")

    # Fix index
    index_path = NEW / "00-index.yaml"
    index_data = yaml.safe_load(index_path.read_text())
    index_data["updated"] = "2026-07-08T20:00:00Z"
    with open(index_path, "w") as f:
        yaml.dump(index_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"  WROTE 00-index.yaml (updated timestamp)")

if __name__ == "__main__":
    merge()
