#!/usr/bin/env python3
"""Constitution Gate — 6 sub-gates: Policy → Security → Cost → Compliance → Quality → Knowledge (HAS-001)

Usage:
  python3 scripts/constitution-gate.py --plan PLAN.yaml
  python3 scripts/constitution-gate.py --plan PLAN.yaml --json
  python3 scripts/constitution-gate.py --plan PLAN.yaml --gate security
"""
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CONSTITUTION_DIR = REPO / "constitution"
PLAN_FILE = REPO / "process" / "active" / "PLAN.yaml"


def load_constitution(domain=None):
    rules = []
    if not CONSTITUTION_DIR.exists():
        return rules
    for f in sorted(CONSTITUTION_DIR.glob("*.yaml")):
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


def policy_gate(plan):
    violations = []
    rules = load_constitution("policy")
    for rule in rules:
        rid = rule.get("id", "")
        severity = rule.get("severity", "warning")
        if rid == "POLICY-001":
            for task in plan.get("tasks", []):
                if task.get("bind") == "0.0.0.0":
                    violations.append({
                        "gate": "policy", "rule": rid, "severity": severity,
                        "detail": f"Task '{task.get('name')}' binds 0.0.0.0",
                        "fix": "Change bind to 127.0.0.1"
                    })
        if rid == "POLICY-002":
            if not plan.get("emit_events", True):
                violations.append({
                    "gate": "policy", "rule": rid, "severity": severity,
                    "detail": "Plan does not emit events",
                    "fix": "Set emit_events: true"
                })
    return violations


def security_gate(plan):
    violations = []
    rules = load_constitution("security")
    for rule in rules:
        rid = rule.get("id", "")
        severity = rule.get("severity", "error")
        if rid == "SEC-001":
            for task in plan.get("tasks", []):
                if task.get("type") == "secret" and not task.get("encrypted"):
                    violations.append({
                        "gate": "security", "rule": rid, "severity": severity,
                        "detail": f"Task '{task.get('name')}' handles secrets without encryption",
                        "fix": "Add encrypted: true or use age"
                    })
        if rid == "SEC-002":
            for task in plan.get("tasks", []):
                if task.get("type") == "network" and task.get("protocol") == "http":
                    violations.append({
                        "gate": "security", "rule": rid, "severity": severity,
                        "detail": f"Task '{task.get('name')}' uses HTTP instead of HTTPS",
                        "fix": "Change to HTTPS"
                    })
    return violations


def cost_gate(plan):
    violations = []
    estimated = plan.get("estimated_cost_tokens", 0)
    budget = plan.get("budget_tokens", 50000)
    if estimated > budget:
        violations.append({
            "gate": "cost", "rule": "COST-001", "severity": "warning",
            "detail": f"Estimated cost ({estimated}) exceeds budget ({budget})",
            "fix": "Increase budget or reduce task complexity"
        })
    return violations


def compliance_gate(plan):
    violations = []
    rules = load_constitution("compliance")
    for rule in rules:
        rid = rule.get("id", "")
        severity = rule.get("severity", "error")
        if rid == "COMP-001":
            agent = plan.get("meta", {}).get("agent", "unknown")
            allowed = plan.get("allowed_agents", [])
            if allowed and agent not in allowed:
                violations.append({
                    "gate": "compliance", "rule": rid, "severity": severity,
                    "detail": f"Agent '{agent}' not in allowed list: {allowed}",
                    "fix": "Add agent to allowed_agents or use authorized agent"
                })
        if rid == "COMP-002":
            tier = plan.get("meta", {}).get("tier", 1)
            for task in plan.get("tasks", []):
                if tier < task.get("min_tier", 1):
                    violations.append({
                        "gate": "compliance", "rule": rid, "severity": severity,
                        "detail": f"Task '{task.get('name')}' requires tier {task.get('min_tier')} but plan is tier {tier}",
                        "fix": f"Upgrade plan to tier {task.get('min_tier')} or remove task"
                    })
    return violations


def quality_gate(plan):
    violations = []
    test_path = plan.get("test_path", "tests/")
    test_dir = REPO / test_path
    if not test_dir.exists():
        violations.append({
            "gate": "quality", "rule": "QUAL-001", "severity": "error",
            "detail": f"Test directory '{test_path}' does not exist",
            "fix": "Create test directory or set correct test_path"
        })
    min_coverage = plan.get("min_coverage", 60)
    if min_coverage < 60:
        violations.append({
            "gate": "quality", "rule": "QUAL-002", "severity": "warning",
            "detail": f"Minimum coverage {min_coverage}% is below threshold (60%)",
            "fix": "Set min_coverage >= 60"
        })
    return violations


def knowledge_gate(plan):
    violations = []
    leccion_path = plan.get("leccion_path", "")
    if not leccion_path:
        violations.append({
            "gate": "knowledge", "rule": "KNOW-001", "severity": "warning",
            "detail": "No leccion_path set — learnings may not be saved",
            "fix": "Set leccion_path in plan"
        })
    return violations


def run_gates(plan):
    gates = [
        ("policy", policy_gate),
        ("security", security_gate),
        ("cost", cost_gate),
        ("compliance", compliance_gate),
        ("quality", quality_gate),
        ("knowledge", knowledge_gate),
    ]
    all_violations = []
    gate_results = []
    for name, gate_fn in gates:
        try:
            violations = gate_fn(plan)
            status = "FAIL" if violations else "PASS"
            gate_results.append({"gate": name, "status": status, "violations": violations})
            all_violations.extend(violations)
        except Exception as e:
            gate_results.append({"gate": name, "status": "ERROR", "error": str(e)})
    return gate_results, all_violations


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Constitution Gate (HAS-001)")
    parser.add_argument("--plan", help="Path to PLAN.yaml")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--gate", choices=["policy", "security", "cost", "compliance", "quality", "knowledge"],
                        help="Run a single gate")
    args = parser.parse_args()

    plan_path = Path(args.plan) if args.plan else PLAN_FILE
    if not plan_path.exists():
        print(f"ERROR: Plan not found: {plan_path}")
        sys.exit(1)

    with open(plan_path) as f:
        plan = yaml.safe_load(f)

    if args.gate:
        gate_fn = {"policy": policy_gate, "security": security_gate, "cost": cost_gate,
                    "compliance": compliance_gate, "quality": quality_gate, "knowledge": knowledge_gate}[args.gate]
        violations = gate_fn(plan)
        if args.json:
            print(json.dumps({"gate": args.gate, "violations": violations}, indent=2))
        else:
            for v in violations:
                print(f"  [{v.get('severity', 'error')}] {v.get('detail', '')}")
                if v.get("fix"):
                    print(f"  → Fix: {v['fix']}")
            if violations:
                print(f"  ✗ {args.gate.upper()} GATE: FAIL ({len(violations)} violations)")
                sys.exit(1)
            else:
                print(f"  ✓ {args.gate.upper()} GATE: PASS")
        return

    gate_results, violations = run_gates(plan)
    has_failures = any(r["status"] == "FAIL" for r in gate_results)

    if args.json:
        print(json.dumps({"gates": gate_results, "total_violations": len(violations)}, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"CONSTITUTION GATE — {plan_path.name} (HAS-001)")
        print(f"{'='*50}")
        for r in gate_results:
            icon = {"PASS": "✓", "FAIL": "✗", "ERROR": "!"}.get(r["status"], "?")
            print(f"\n  {icon} {r['gate'].upper()} GATE: {r['status']}")
            for v in r.get("violations", []):
                print(f"     [{v.get('severity', 'error')}] {v.get('detail', '')}")
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
