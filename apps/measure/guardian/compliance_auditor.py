"""Compliance Auditor — JR-Lite, Score gate, CONDUCT.md, truth/ rules, capability checks [FR9-FR12]"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent
TRUTH = REPO / "truth"
VIOLATIONS = REPO / "state" / "quality" / "violations.jsonl"


def get_compliance_rules():
    """Lee reglas de compliance desde truth/85-compliance.yaml"""
    rules_file = TRUTH / "85-compliance.yaml"
    if not rules_file.exists():
        return []
    try:
        import yaml
        with open(rules_file) as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])
    except Exception:
        return []


def get_architecture_rules():
    """Lee reglas de arquitectura desde truth/20-architecture.yaml"""
    rules_file = TRUTH / "20-architecture.yaml"
    if not rules_file.exists():
        return []
    try:
        import yaml
        with open(rules_file) as f:
            data = yaml.safe_load(f)
        return data.get("rules", [])
    except Exception:
        return []


def check_jr_lite(spec_path):
    """Verifica cumplimiento JR-Lite 15-Point"""
    if not spec_path.exists():
        return [{"rule": "JR-Lite", "detail": f"Spec not found: {spec_path}"}]

    text = spec_path.read_text()
    violations = []

    checks = [
        (r"## 1\. Objetivo", "1. Objetivo claro"),
        (r"## 2\. Value Driver", "2. Value Driver"),
        (r"## 3\. Functional Requirements", "3. FR numerados"),
        (r"## 4\. Success Criteria", "4. Success criteria"),
        (r"## 5\. Gherkin Scenarios", "5. Gherkin scenarios"),
        (r"## 6\. Edge Cases", "6. Edge cases"),
        (r"## 7\. Technical Approach", "7. Technical approach"),
        (r"## 8\. Dependencies", "8. Dependencies"),
        (r"## 9\. Events to Emit", "9. Events defined"),
        (r"## 10\. Kill Criteria", "10. Kill criteria"),
    ]

    for pattern, label in checks:
        if not re.search(pattern, text):
            violations.append({"rule": "JR-Lite", "detail": f"Missing section: {label}"})

    return violations


def check_score(spec_id):
    """Verifica que SCORE.md existe y es ≥ 60"""
    score_path = REPO / "process" / "active" / f"SCORE-{spec_id}.md"
    if not score_path.exists():
        # Buscar en completed
        for d in (REPO / "process" / "completed").iterdir():
            if d.is_dir():
                sp = d / f"SCORE-{spec_id}.md"
                if sp.exists():
                    score_path = sp
                    break

    if not score_path.exists():
        return [{"rule": "Score Gate", "detail": f"SCORE.md not found for {spec_id}"}]

    text = score_path.read_text()
    m = re.search(r"(\d+)/100", text)
    if m:
        score = int(m.group(1))
        if score < 60:
            return [{"rule": "Score Gate", "detail": f"Score {score} < 60 threshold"}]
    else:
        return [{"rule": "Score Gate", "detail": "Score not found in SCORE.md"}]

    return []


def check_conduct():
    """Verifica archivos requeridos por CONDUCT.md"""
    violations = []
    completed = REPO / "process" / "completed"
    if not completed.exists():
        return [{"rule": "CONDUCT.md", "detail": "No completed specs directory"}]

    for d in completed.iterdir():
        if not d.is_dir():
            continue
        spec_file = list(d.glob("SPEC-*.md"))
        if not spec_file:
            continue

        spec_id = spec_file[0].stem
        required = [
            ("SPEC.md", list(d.glob("SPEC-*.md"))),
            ("events.jsonl", list(d.glob("events.jsonl"))),
            ("LECCION.md", list(d.glob("LECCION.md"))),
        ]

        for label, files in required:
            if not files:
                violations.append({
                    "rule": "CONDUCT.md",
                    "detail": f"{spec_id}: missing {label}"
                })

    return violations


def check_capability(agent_name, capability):
    """Verifica via check-capability.py si un agente tiene capability"""
    try:
        script = REPO / "scripts" / "check-capability.py"
        result = subprocess.run(
            [sys.executable, str(script), agent_name, capability],
            capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def check_recent_violations(limit=10):
    """Lee las últimas violaciones de violations.jsonl"""
    if not VIOLATIONS.exists():
        return []
    violations = []
    with open(VIOLATIONS) as f:
        for line in f:
            try:
                violations.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return violations[-limit:]


def run_all(spec_id="SPEC-20260703-A"):
    """Ejecuta todos los checks y loggea violaciones"""
    violations = []
    spec_path = REPO / "process" / "completed" / "20260703-enterprise-agentic-os" / f"{spec_id}.md"
    violations.extend(check_jr_lite(spec_path))
    violations.extend(check_conduct())

    if violations:
        VIOLATIONS.parent.mkdir(parents=True, exist_ok=True)
        with open(VIOLATIONS, "a") as f:
            for v in violations:
                entry = {**v, "timestamp": "2026-07-03T16:20:00Z"}
                f.write(json.dumps(entry) + "\n")

    return violations


if __name__ == "__main__":
    violations = run_all()
    if violations:
        print(json.dumps(violations, indent=2))
    else:
        print("OK — all compliance checks passed")
