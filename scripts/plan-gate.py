#!/usr/bin/env python3
"""Planning Gate — descompone objetivos en tareas, genera PLAN.yaml, valida contra truth/ [FR21-FR24]"""
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
PLAN_FILE = REPO / "process" / "active" / "PLAN.yaml"
TRUTH_DIR = REPO / "truth"


def load_truth_rules():
    """Carga todas las reglas de truth/ para validación"""
    rules = []
    for f in sorted(TRUTH_DIR.glob("*.yaml")):
        try:
            with open(f) as fh:
                data = yaml.safe_load(fh)
            for rule in data.get("rules", []):
                rule["_source"] = f.name
                rules.append(rule)
        except Exception as e:
            print(f"WARNING: could not load {f.name}: {e}", file=sys.stderr)
    return rules


def validate_plan(plan, rules):
    """Valida plan contra truth/ rules"""
    violations = []
    for rule in rules:
        rid = rule.get("id", "unknown")
        severity = rule.get("severity", "warning")
        applies_to = rule.get("applies_to", [])

        # Check if rule applies to this plan
        if "all_agents" in applies_to or "all_services" in applies_to:
            pass  # applies to everything
        elif plan.get("agent") in applies_to:
            pass
        else:
            continue

        # Rule-specific checks
        if rid == "ARCH-001":
            # No service binds 0.0.0.0
            for task in plan.get("tasks", []):
                if task.get("bind") == "0.0.0.0":
                    violations.append({
                        "rule": rid,
                        "severity": severity,
                        "detail": f"Task '{task.get('name')}' binds 0.0.0.0 — violates ARCH-001",
                        "source": rule.get("_source")
                    })

        if rid == "PRINCIPLE-004":
            # Every execution requires a plan
            pass  # we're already in plan-gate, so this is satisfied

        if rid == "PRINCIPLE-006":
            # Every event must be emitted
            if not plan.get("emit_events", True):
                violations.append({
                    "rule": rid,
                    "severity": severity,
                    "detail": "Plan does not emit events — violates PRINCIPLE-006",
                    "source": rule.get("_source")
                })

    return violations


def estimate_cost(tasks):
    """Estima costo en tokens para el plan"""
    total_tokens = 0
    for task in tasks:
        complexity = task.get("complexity", "medium")
        model = task.get("model", "opencode-go")
        tokens = {
            "simple": 1000,
            "medium": 5000,
            "complex": 15000
        }.get(complexity, 5000)
        total_tokens += tokens
    return total_tokens


def create_plan(objective, agent="mystic", tasks=None):
    """Crea un plan estructurado"""
    if tasks is None:
        tasks = []

    plan = {
        "meta": {
            "created": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "agent": agent,
            "source": "plan-gate.py"
        },
        "objective": objective,
        "tasks": tasks,
        "dependencies": [],
        "risks": [],
        "estimated_cost_tokens": estimate_cost(tasks),
    }

    # Auto-detect dependencies between tasks
    task_names = {t.get("name") for t in tasks}
    for task in tasks:
        for dep in task.get("depends_on", []):
            if dep in task_names:
                plan["dependencies"].append({"from": dep, "to": task.get("name")})
            else:
                plan["risks"].append(f"Task '{task.get('name')}' depends on unknown '{dep}'")

    return plan


def save_plan(plan):
    """Guarda el plan como YAML"""
    PLAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PLAN_FILE, "w") as f:
        yaml.dump(plan, f, default_flow_style=False, sort_keys=False)
    print(f"Plan saved: {PLAN_FILE}", file=sys.stderr)
    return PLAN_FILE


def emit_plan_event(plan, status):
    """Emite evento de plan creation"""
    try:
        subprocess.run(
            [sys.executable, str(REPO / "scripts" / "emit-event.py"),
             "--event", f"plan.{status}",
             "--kernel", "planning",
             "--agent", plan.get("meta", {}).get("agent", "unknown"),
             "--subject-type", "plan",
             "--subject-id", PLAN_FILE.stem,
             "--subject-path", str(PLAN_FILE),
             "--payload", json.dumps({
                 "tasks": len(plan.get("tasks", [])),
                 "cost": plan.get("estimated_cost_tokens", 0),
                 "objective": plan.get("objective", "")[:100]
             })],
            capture_output=True, timeout=5
        )
    except Exception:
        pass


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Planning Gate — create and validate execution plans")
    parser.add_argument("objective", nargs="?", help="Task objective")
    parser.add_argument("--agent", default="mystic", help="Agent name")
    parser.add_argument("--validate", action="store_true", help="Validate existing plan without creating")
    parser.add_argument("--tasks", help="JSON file with task definitions")
    args = parser.parse_args()

    rules = load_truth_rules()
    print(f"Loaded {len(rules)} rules from truth/", file=sys.stderr)

    if args.validate:
        if not PLAN_FILE.exists():
            print("ERROR: No active plan found", file=sys.stderr)
            sys.exit(1)
        with open(PLAN_FILE) as f:
            plan = yaml.safe_load(f)
        violations = validate_plan(plan, rules)
        if violations:
            print(f"PLAN VALIDATION: {len(violations)} violations", file=sys.stderr)
            for v in violations:
                print(f"  [{v['severity']}] {v['rule']}: {v['detail']}", file=sys.stderr)
            sys.exit(1)
        else:
            print("PLAN VALIDATION: PASSED — no violations", file=sys.stderr)
        return

    if not args.objective:
        print("ERROR: objective is required", file=sys.stderr)
        sys.exit(1)

    tasks = []
    if args.tasks:
        tasks_path = Path(args.tasks)
        if tasks_path.exists():
            with open(tasks_path) as f:
                tasks = json.load(f)

    plan = create_plan(args.objective, args.agent, tasks)
    violations = validate_plan(plan, rules)

    if violations:
        print(f"PLAN REJECTED: {len(violations)} violations against truth/", file=sys.stderr)
        for v in violations:
            print(f"  [{v['severity']}] {v['rule']}: {v['detail']}", file=sys.stderr)
        emit_plan_event(plan, "rejected")
        sys.exit(1)

    save_plan(plan)
    emit_plan_event(plan, "created")
    print(f"Plan approved: {args.objective[:60]}...", file=sys.stderr)
    print(f"Tasks: {len(tasks)}, Est. cost: {plan['estimated_cost_tokens']} tokens", file=sys.stderr)


if __name__ == "__main__":
    main()
