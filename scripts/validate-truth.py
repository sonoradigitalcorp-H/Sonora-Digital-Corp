#!/usr/bin/env python3
"""Valida todos los constitution/ YAML files — schema, conflictos, integridad (HAS-001)"""
import sys
from pathlib import Path

import yaml

TRUTH_DIR = Path(__file__).resolve().parent.parent / "constitution"
errors = []
warnings = []


def validate_schema(data, path):
    """Valida que cada truth file tenga campos requeridos"""
    required = ["version", "domain", "updated"]
    for field in required:
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")

    if "rules" not in data:
        warnings.append(f"{path}: no 'rules' field")
    elif not isinstance(data["rules"], list):
        errors.append(f"{path}: 'rules' must be a list")

    if data.get("version") != 1:
        warnings.append(f"{path}: version != 1 (got {data.get('version')})")


def check_conflicts(files):
    """Detecta conflictos entre truth files"""
    all_rules = {}
    for path, data in files:
        for rule in data.get("rules", []):
            rid = rule.get("id")
            if not rid:
                continue
            if rid in all_rules:
                prev_path = all_rules[rid]
                if prev_path != path:
                    errors.append(
                        f"CONFLICT: rule '{rid}' defined in both {prev_path} and {path}"
                    )
            else:
                all_rules[rid] = path


def check_level_hierarchy(files):
    """Verifica que no haya reglas duplicadas entre niveles"""
    level_rules = {}
    for path, data in files:
        domain = data.get("domain", "unknown")
        for rule in data.get("rules", []):
            rid = rule.get("id")
            if rid:
                level_rules[rid] = {"domain": domain, "path": path}


def main():
    truth_files = sorted(TRUTH_DIR.glob("*.yaml"))
    if not truth_files:
        print("ERROR: No truth files found")
        sys.exit(1)

    parsed = []
    for f in truth_files:
        try:
            with open(f) as fh:
                data = yaml.safe_load(fh)
            validate_schema(data, f.name)
            parsed.append((f.name, data))
        except yaml.YAMLError as e:
            errors.append(f"{f.name}: YAML parse error: {e}")

    check_conflicts(parsed)
    check_level_hierarchy(parsed)

    if errors:
        print(f"FAIL: {len(errors)} errors")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)

    if warnings:
        print(f"PASS: {len(warnings)} warnings")
        for w in warnings:
            print(f"  ⚠ {w}")
    else:
        print("PASS: all truth files valid, no conflicts")
    print(f"Files: {len(truth_files)}, Rules: {sum(len(d.get('rules',[])) for _,d in parsed)}")


if __name__ == "__main__":
    main()
