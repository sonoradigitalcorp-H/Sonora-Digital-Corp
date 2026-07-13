#!/usr/bin/env python3
"""Validate all agent definitions and their cross-references."""

import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
AGENTS_DIR = BASE / "agents"
TOOLS_DIR = BASE / "tools"
ORCH_DIR = BASE / "orchestrator"

errors = []
warnings = []


def check_agent_file(path: Path):
    """Validate a single agent .md file."""
    if not path.exists():
        errors.append(f"MISSING: {path}")
        return None

    content = path.read_text()
    # Check frontmatter
    if not content.startswith("---"):
        errors.append(f"{path.name}: Missing YAML frontmatter (must start with ---)")
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append(f"{path.name}: Malformed frontmatter")
        return None

    # Parse frontmatter
    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            frontmatter[key.strip()] = val.strip()

    # Required fields
    required = ["name", "tenant", "role"]
    for field in required:
        if field not in frontmatter:
            errors.append(f"{path.name}: Missing required frontmatter field: {field}")

    # Check body has required sections
    body = parts[2]
    body_required = ["## Rol", "## Tools", "## Memoria", "## Comunicación"]
    for section in body_required:
        if section not in body:
            warnings.append(f"{path.name}: Missing recommended section: {section}")

    return frontmatter


def check_tools_exist(agent_name: str, tools_text: str):
    """Check that tools referenced by an agent exist in the tool registry."""
    import re
    # Find tool names in the body (e.g., `rag_search`, `hasura_query`)
    tools_found = re.findall(r'`([a-z_]+)`', tools_text)
    registry_path = TOOLS_DIR / "registry.json"
    if not registry_path.exists():
        warnings.append(f"Tool registry not found, skipping tool validation")
        return
    with open(registry_path) as f:
        registry = json.load(f)

    registry_tools = {t["name"] for t in registry["tools"]}
    for tool in tools_found:
        if tool not in registry_tools:
            warnings.append(f"{agent_name}: references tool '{tool}' which is not in registry")


def main():
    print("=" * 50)
    print("SDC Agent Validation")
    print("=" * 50)

    # Validate registry.yaml
    registry_path = AGENTS_DIR / "registry.yaml"
    if not registry_path.exists():
        errors.append("MISSING: agents/registry.yaml")
    else:
        print(f"\n✅ agents/registry.yaml exists")

    # Validate TEMPLATE
    template_path = AGENTS_DIR / "TEMPLATE-agent.md"
    if not template_path.exists():
        errors.append("MISSING: agents/TEMPLATE-agent.md")
    else:
        print(f"✅ agents/TEMPLATE-agent.md exists")

    # Validate per-tenant agent files
    tenants = sorted(d for d in AGENTS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    print(f"\nTenants found: {[t.name for t in tenants]}")

    for tenant_dir in tenants:
        agent_files = sorted(tenant_dir.glob("*.md"))
        print(f"\n  {tenant_dir.name}: {len(agent_files)} agents")

        for af in agent_files:
            fm = check_agent_file(af)
            if fm:
                print(f"    ✅ {af.name} ({fm.get('role', '?')[:40]}...)")
                # Check tools cross-reference
                check_tools_exist(af.stem, af.read_text())
            else:
                print(f"    ❌ {af.name} — INVALID")

    # Validate tool registry.json
    reg_path = TOOLS_DIR / "registry.json"
    if reg_path.exists():
        with open(reg_path) as f:
            reg = json.load(f)
        print(f"\n✅ Tool registry: {len(reg['tools'])} tools, {len(reg['servers'])} servers")
    else:
        errors.append("MISSING: tools/registry.json")

    # Summary
    print("\n" + "=" * 50)
    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   - {e}")
    else:
        print("✅ ERRORS: 0")

    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   - {w}")
    else:
        print("✅ WARNINGS: 0")

    print("=" * 50)
    return len(errors)


if __name__ == "__main__":
    sys.exit(main())
