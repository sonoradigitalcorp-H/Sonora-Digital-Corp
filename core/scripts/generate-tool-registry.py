#!/usr/bin/env python3
"""Generate tools/registry.json from MCP server definitions."""

import json
import os
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
MCP_DIR = BASE / "core" / "mcp" / "servers"
TOOLS_DIR = BASE / "tools"

if not MCP_DIR.exists():
    MCP_DIR = BASE / "mcp" / "servers"  # fallback to old location

import importlib.util
import ast


def extract_tools_from_file(filepath):
    """Parse a Python file and extract MCP_TOOLS dict."""
    with open(filepath) as f:
        tree = ast.parse(f.read())
    tools = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "MCP_TOOLS":
                    # Extract tool names from the dict literal
                    if isinstance(node.value, ast.Dict):
                        for key in node.value.keys:
                            if isinstance(key, ast.Constant):
                                tools[key.value] = {
                                    "source": filepath.name,
                                }
    return tools


def main():
    registry = {"tools": [], "servers": [], "generated_at": None}
    from datetime import datetime
    registry["generated_at"] = datetime.utcnow().isoformat()

    servers_dir = BASE / "mcp" / "servers"
    if not servers_dir.exists():
        print(f"ERROR: MCP servers directory not found: {servers_dir}")
        sys.exit(1)

    missing_docs = []
    total_tools = 0

    for f in sorted(servers_dir.glob("*_mcp.py")):
        if f.name == "__init__.py":
            continue
        server_name = f.stem
        tools = extract_tools_from_file(f)
        if not tools:
            print(f"  ⚠️  {server_name}: no MCP_TOOLS found")
            continue

        server_entry = {
            "name": server_name,
            "file": f.name,
            "tool_count": len(tools),
            "tools": list(tools.keys()),
        }
        registry["servers"].append(server_entry)
        total_tools += len(tools)

        for tool_name in tools:
            doc_path = TOOLS_DIR / f"{tool_name}.md"
            alt_doc = TOOLS_DIR / f"{tool_name.split('_')[0]}.md"
            has_doc = doc_path.exists() or alt_doc.exists()
            if not has_doc:
                missing_docs.append(tool_name)

            registry["tools"].append({
                "name": tool_name,
                "server": server_name,
                "has_doc": has_doc,
                "doc_file": f"{tool_name}.md" if doc_path.exists() else (f"{tool_name.split('_')[0]}.md" if alt_doc.exists() else None),
            })

    # Write registry
    with open(TOOLS_DIR / "registry.json", "w") as f:
        json.dump(registry, f, indent=2)

    print(f"\n📦 Registry generated: {total_tools} tools across {len(registry['servers'])} servers")
    if missing_docs:
        print(f"\n⚠️  Missing docs ({len(missing_docs)}):")
        for t in sorted(missing_docs):
            print(f"     - tools/{t}.md")
    else:
        print("\n✅ All tools have documentation!")

    return len(missing_docs)


if __name__ == "__main__":
    sys.exit(main())
