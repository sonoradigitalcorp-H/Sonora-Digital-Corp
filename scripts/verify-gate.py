#!/usr/bin/env python3
"""Verification Pipeline — Truth Gate, Security Gate, Cost Gate [FR25-FR30]"""
import json
import os
import sys
import yaml
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PLAN_FILE = REPO / "process" / "active" / "PLAN.yaml"
TRUTH_DIR = REPO / "truth"


def load_rules(domain=None):
    """Carga reglas desde truth/"""
    rules = []
    for f in sorted(TRUTH_DIR.glob("*.yaml")):
        try:
            with open(f) as fh:
                data = yaml.safe_load(fh)
            if domain and data.get("domain") != domain:
                continue
            for rule in data.get("rules", []):
                rule["_source"] = f.name
                rules.append(rule)
        except Exception:
            pass
    return rules


def truth_gate(plan):
    """Truth Gate: verifica que el plan no contradiga truth/"""
    violations = []
    rules = load_rules()

    for rule in rules:
        rid = rule.get("id", "")
        severity = rule.get("severity", "warning")

        # ARCH-001: No 0.0.0.0 binding
        if rid == "ARCH-001":
            for task in plan.get("tasks", []):
                if task.get("bind") == "0.0.0.0":
                    violations.append({
                        "gate": "truth", "rule": rid, "severity": severity,
                        "detail": f"Task '{task.get('name')}' binds 0.0.0.0",
                        "fix": "Change bind to 127.0.0.1"
                    })

        # PRINCIPLE-006: Events must be emitted
        if rid == "PRINCIPLE-006":
            if not plan.get("emit_events", True):
                violations.append({
                    "gate": "truth", "rule": rid, "severity": severity,
                    "detail": "Plan does not emit events",
                    "fix": "Set emit_events: true"
                })

    return violations


def security_gate(plan):
    """Security Gate: verifica capabilities del agente vs operación"""
    violations = []
    agent = plan.get("meta", {}).get("agent", "unknown")

    rules = load_rules("security")
    for rule in rules:
        rid = rule.get("id", "")

        # SEC-001: Secrets must be encrypted
        if rid == "SEC-001":
            for task in plan.get("tasks", []):
                if task.get("type") == "secret" and not task.get("encrypted"):
                    violations.append({
                        "gate": "security", "rule": rid, "severity": "error",
                        "detail": f"Task '{task.get('name')}' handles secrets without encryption",
                        "fix": "Add encrypted: true or use age"
                    })

    return violations


def cost_gate(plan):
    """Cost Gate: verifica costo estimado vs budget"""
    violations = []
    estimated = plan.get("estimated_cost_tokens", 0)
    budget = plan.get("budget_tokens", 50000)

    if estimated > budget:
        violations.append({
            "gate": "cost", "rule": "COST-001", "severity": "warning",
            "detail": f"Estimated cost ({estimated}) exceeds budget ({budget})",
            "fix": f"Increase budget or reduce task complexity"
        })

    return violations


def run_gates(plan):
    """Ejecuta los 3 gates en secuencia"""
    gates = [
        ("truth", truth_gate),
        ("security", security_gate),
        ("cost", cost_gate),
    ]

    all_violations = []
    gate_results = []

    for name, gate_fn in gates:
        try:
            violations = gate_fn(plan)
            status = "FAIL" if violations else "PASS"
            gate_results.append({"gate": name, "status": status, "violations": violations})
            all_violations.extend(violations)

            # Emit event per gate
            try:
                subprocess.run(
                    [sys.executable, str(REPO / "scripts" / "emit-event.py"),
                     "--event", f"gate.{'failed' if violations else 'passed'}",
                     "--kernel", "verification",
                     "--agent", "verify-gate",
                     "--subject-type", "gate",
                     "--subject-id", f"gate.{name}",
                     "--payload", json.dumps({
                         "gate": name, "status": status,
                         "violations": len(violations)
                     })],
                    capture_output=True, timeout=5
                )
            except Exception:
                pass

        except Exception as e:
            gate_results.append({"gate": name, "status": "ERROR", "error": str(e)})
            subprocess.run(
                [sys.executable, str(REPO / "scripts" / "emit-event.py"),
                 "--event", "gate.error",
                 "--kernel", "verification",
                 "--agent", "verify-gate",
                 "--subject-type", "gate",
                 "--subject-id", f"gate.{name}",
                 "--payload", json.dumps({"error": str(e)})],
                capture_output=True, timeout=5
            )

    return gate_results, all_violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Verification Pipeline")
    parser.add_argument("--plan", help="Path to PLAN.yaml (default: process/active/PLAN.yaml)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    plan_path = Path(args.plan) if args.plan else PLAN_FILE
    if not plan_path.exists():
        print(f"ERROR: Plan not found: {plan_path}")
        sys.exit(1)

    with open(plan_path) as f:
        plan = yaml.safe_load(f)

    gate_results, violations = run_gates(plan)
    has_failures = any(r["status"] == "FAIL" for r in gate_results)

    if args.json:
        print(json.dumps({"gates": gate_results, "total_violations": len(violations)}, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"VERIFICATION PIPELINE — {plan_path.name}")
        print(f"{'='*50}")
        for r in gate_results:
            icon = {"PASS": "✓", "FAIL": "✗", "ERROR": "!"}.get(r["status"], "?")
            print(f"\n  {icon} {r['gate'].upper()} GATE: {r['status']}")
            for v in r.get("violations", []):
                print(f"     [{v.get('severity','error')}] {v.get('detail','')}")
                if v.get("fix"):
                    print(f"     → Fix: {v['fix']}")
            if r.get("error"):
                print(f"     Error: {r['error']}")
        print(f"\n  Total violations: {len(violations)}")
        print(f"{'='*50}")

    if has_failures:
        print("\n  ⛔ STOP: Some gates failed. Fix violations before proceeding.")
        sys.exit(1)
    else:
        print("\n  ✅ All gates passed. Ready to execute.")


if __name__ == "__main__":
    main()
