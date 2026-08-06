#!/usr/bin/env python3
"""Verifica si un agente tiene capability para una operación [FR8]"""
import json
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
POLICIES_DIR = REPO / "agents" / "policies"
CAPABILITIES_DIR = REPO / "agents" / "capabilities"

DEFAULT_POLICY = POLICIES_DIR / "10-default.yaml"


def load_yaml(path):
    if path.exists():
        with open(path) as f:
            return yaml.safe_load(f)
    return None


def check(agent, capability):
    """Verifica si agent tiene capability específica"""
    # Buscar policy del agente (recorre agents/policies/*.yaml buscando agent: name)
    policy = None
    policy_file = None
    for f in sorted(POLICIES_DIR.glob("*.yaml")):
        d = load_yaml(f)
        if d and d.get("agent") == agent:
            policy = d
            policy_file = f
            break

    if not policy:
        default = load_yaml(DEFAULT_POLICY)
        return {
            "allowed": False,
            "reason": f"No policy found for agent '{agent}' — default deny-all",
            "policy": "10-default.yaml"
        }

    # Allow-all policy
    if policy.get("policy") == "allow-all":
        return {"allowed": True, "agent": agent, "capability": capability, "policy": policy_file.name}

    # Never list
    never = policy.get("never", [])
    for n in never:
        if capability == n or (n.endswith(".*") and capability.startswith(n[:-1])):
            return {
                "allowed": False,
                "reason": f"Agent '{agent}' explicitly denied: {capability} (never: {n})",
                "policy": policy_file.name
            }

    # Allow-specific
    allowed = policy.get("capabilities", [])
    for a in allowed:
        if capability == a or a == "*" or (a.endswith(".*") and capability.startswith(a[:-1])):
            return {"allowed": True, "agent": agent, "capability": capability, "policy": policy_file.name}

    return {
        "allowed": False,
        "reason": f"Agent '{agent}' does not have capability '{capability}'",
        "policy": policy_file.name
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check agent capability")
    parser.add_argument("agent", help="Agent name")
    parser.add_argument("capability", help="Capability to check (e.g., git.push)")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = check(args.agent, args.capability)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        status = "✓ ALLOWED" if result["allowed"] else "✗ DENIED"
        print(f"{status} — {args.agent}/{args.capability}")
        print(f"  Reason: {result.get('reason', 'allowed by policy')}")
        print(f"  Policy: {result.get('policy', 'unknown')}")

    sys.exit(0 if result["allowed"] else 1)


if __name__ == "__main__":
    main()
