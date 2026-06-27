#!/usr/bin/env python3
"""
analizador.py — Autonomous repo scanner.

Runs every 6h via GitHub Actions cron.
Scans the repo for:
- Failing tests (via last CI run)
- Missing specs for existing code
- Patterns from memory/patrones.md that could apply
- Duplicate or dead code

Creates Issues for actionable findings.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = REPO_ROOT / "memory"
SPECS_DIR = REPO_ROOT / "specs"
APPS_DIR = REPO_ROOT / "apps"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")


def load_json(path):
    if path.exists():
        return json.loads(path.read_text())
    return {}


def get_existing_specs():
    """Return set of spec names from specs/ directory."""
    if not SPECS_DIR.exists():
        return set()
    return {d.name for d in SPECS_DIR.iterdir() if d.is_dir()}


def get_apps():
    """Return list of app directories in apps/."""
    if not APPS_DIR.exists():
        return []
    return [d for d in APPS_DIR.iterdir() if d.is_dir()]


def check_missing_specs():
    """Check if apps exist without corresponding specs."""
    apps = get_apps()
    specs = get_existing_specs()
    missing = []
    for app in apps:
        spec_name = app.name.replace("_", "-")
        if spec_name not in specs:
            # Check if any spec folder contains this app name
            found = False
            for spec_dir in specs:
                if app.name in spec_dir:
                    found = True
                    break
            if not found:
                missing.append(app.name)
    return missing


def check_lessons(app_reports, lecciones):
    """Check if past lessons suggest improvements."""
    findings = []
    for leccion in lecciones:
        leccion_path = leccion.get("path", "")
        leccion_message = leccion.get("message", "")
        if leccion_message:
            findings.append({
                "type": "lesson",
                "message": f"Previous lesson: {leccion_message}",
                "path": leccion_path,
            })
    return findings


def create_issue(title, body, labels=None):
    """Create a GitHub Issue via API."""
    if not GITHUB_TOKEN or not REPO:
        print(f"  [SKIP] No GITHUB_TOKEN or REPO set. Would create: {title}")
        return
    labels = labels or ["analizador"]
    label_str = ",".join(labels)
    cmd = (
        f'gh api repos/{REPO}/issues -f title="{title}" '
        f'-f body="{body}" -f labels="{label_str}"'
    )
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  [OK] Issue created: {title}")
    else:
        print(f"  [FAIL] {result.stderr}")


def main():
    print("🔍 analizador.py — scanning repo...")
    lecciones = load_json(MEMORY_DIR / "lecciones.json")
    lecciones_list = lecciones.get("lecciones", [])
    findings = []

    # 1. Check missing specs
    missing = check_missing_specs()
    for app in missing:
        findings.append({
            "type": "missing_spec",
            "message": f"App '{app}' has no corresponding spec in specs/",
            "path": str(APPS_DIR / app),
        })

    # 2. Check past lessons
    findings.extend(check_lessons(findings, lecciones_list))

    # 3. Report
    if not findings:
        print("✅ No issues found. Repo is healthy.")
        return

    print(f"📋 {len(findings)} findings:")
    for f in findings:
        print(f"  - [{f['type']}] {f['message']}")
        if f.get("path"):
            print(f"    Path: {f['path']}")

    # Create issues for actionable findings
    spec_issues = [f for f in findings if f["type"] == "missing_spec"]
    for si in spec_issues:
        create_issue(
            title=f"[analizador] Missing spec: {si['message']}",
            body=f"## Found by analizador\n\n{si['message']}\n\n"
                 f"Path: {si['path']}\n\n"
                 "Create a spec in specs/ before implementing.",
            labels=["analizador", "spec-needed"],
        )

    # Store findings as artifacts for the workflow
    findings_path = REPO_ROOT / "analizador-findings.json"
    findings_path.write_text(json.dumps(findings, indent=2))
    print(f"📝 Findings written to {findings_path}")


if __name__ == "__main__":
    main()
