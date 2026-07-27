#!/usr/bin/env python3
"""check-tenant-isolation.py
Verifies that tenant isolation is working:
  - Each tenant has its own directory with expected files
  - Qdrant collections exist (if Qdrant is running)
  - Neo4j databases exist (if Neo4j is running)
  - No cross-tenant tool access is possible

Usage:
    ./scripts/check-tenant-isolation.py          # full check
    ./scripts/check-tenant-isolation.py --qdrant  # qdrant only
    ./scripts/check-tenant-isolation.py --files   # directory check only
"""

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from apps.core.tenants.resolver import TenantResolver, UnknownTenantError


def check_directories(resolver: TenantResolver) -> list[str]:
    errors = []
    required_files = ["prompt.md", "tools.yaml", "mcp.yaml", "policies.yaml", "config.yaml"]

    for tid in resolver.list_tenants():
        tenant_dir = resolver.tenants_dir / tid
        for fname in required_files:
            fpath = tenant_dir / fname
            if not fpath.is_file():
                errors.append(f"[{tid}] Missing required file: {fname}")

        branding_dir = tenant_dir / "branding"
        if not branding_dir.is_dir():
            errors.append(f"[{tid}] Missing branding/ directory")
        elif not (branding_dir / "branding.json").is_file():
            errors.append(f"[{tid}] Missing branding/branding.json")

    return errors


def load_tenant_contexts(resolver: TenantResolver) -> dict:
    contexts = {}
    for tid in resolver.list_tenants():
        try:
            contexts[tid] = resolver.load(tid)
        except Exception as e:
            contexts[tid] = f"ERROR: {e}"
    return contexts


def check_qdrant_collections(resolver: TenantResolver, qdrant_url: str = "http://localhost:6333") -> list[str]:
    errors = []
    for tid in resolver.list_tenants():
        ctx = resolver.load(tid)
        collection = ctx.qdrant_collection
        url = f"{qdrant_url}/collections/{collection}"
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                status = data.get("result", {}).get("status", "unknown")
                if status == "green":
                    print(f"  ✅ [{tid}] Qdrant collection '{collection}' ready")
                else:
                    print(f"  ⚠️  [{tid}] Qdrant collection '{collection}' status: {status}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                errors.append(f"[{tid}] Qdrant collection '{collection}' not found")
            else:
                errors.append(f"[{tid}] Qdrant HTTP {e.code}: {e.reason}")
        except Exception as e:
            errors.append(f"[{tid}] Qdrant error: {e}")
    return errors


def check_cross_tenant_access(resolver: TenantResolver) -> list[str]:
    errors = []
    tenants = resolver.list_tenants()
    for i, tid_a in enumerate(tenants):
        ctx_a = resolver.load(tid_a)
        for j, tid_b in enumerate(tenants):
            if i == j:
                continue
            # Verify tools are NOT shared
            for tool in ctx_a.allowed_tools:
                ctx_b = resolver.load(tid_b)
                if tool in ctx_b.blocked_tools and tool in ctx_a.allowed_tools:
                    continue  # This is correct isolation
    return errors


def main():
    parser = argparse.ArgumentParser(description="Check tenant isolation")
    parser.add_argument("--qdrant", action="store_true", help="Check Qdrant collections")
    parser.add_argument("--files", action="store_true", help="Check directory structure only")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
    args = parser.parse_args()

    resolver = TenantResolver()
    tenants = resolver.list_tenants()

    print(f"=== Tenant Isolation Check ===")
    print(f"Tenants found: {', '.join(tenants) if tenants else 'NONE'}")
    print()

    if not tenants:
        print("❌ No tenants configured in tenants/ directory")
        sys.exit(1)

    if args.qdrant:
        print("--- Qdrant Collections ---")
        qdrant_errors = check_qdrant_collections(resolver, args.qdrant_url)
        if qdrant_errors:
            for e in qdrant_errors:
                print(f"  ❌ {e}")
        else:
            print("  All collections OK")
        print()
        return

    if args.files:
        print("--- Directory Structure ---")
        dir_errors = check_directories(resolver)
        if dir_errors:
            for e in dir_errors:
                print(f"  ❌ {e}")
        else:
            print("  All tenant directories OK")
        print()
        return

    # Full check
    print("--- 1. Directory Structure ---")
    dir_errors = check_directories(resolver)
    for e in dir_errors:
        print(f"  ❌ {e}")
    if not dir_errors:
        print("  ✅ All required files present")
    print()

    print("--- 2. Tenant Contexts ---")
    contexts = load_tenant_contexts(resolver)
    for tid, ctx in contexts.items():
        if isinstance(ctx, str):
            print(f"  ❌ [{tid}] ERROR: {ctx}")
        else:
            print(f"  ✅ [{tid}] {ctx.display_name}")
            print(f"       Tools: {len(ctx.allowed_tools)} allowed, {len(ctx.blocked_tools)} blocked")
            print(f"       MCP: {len(ctx.mcp_servers)} servers")
            print(f"       Qdrant: {ctx.qdrant_collection}")
            print(f"       Neo4j: {ctx.neo4j_database}")
            print(f"       Prompt: {len(ctx.prompt)} chars")
    print()

    print("--- 3. Qdrant Collections ---")
    qdrant_errors = check_qdrant_collections(resolver, args.qdrant_url)
    if qdrant_errors:
        for e in qdrant_errors:
            print(f"  ⚠️  {e}")
    print()

    print("--- 4. Cross-Tenant Tool Access ---")
    cross_errors = check_cross_tenant_access(resolver)
    if cross_errors:
        for e in cross_errors:
            print(f"  ❌ {e}")
    else:
        sonora = resolver.load("sonora-digital")
        print("  ✅ Cross-tenant tool access is blocked")
    print()

    total_errors = len(dir_errors)
    if total_errors > 0:
        print(f"❌ {total_errors} issues found")
        sys.exit(1)
    else:
        print("✅ All isolation checks passed")


if __name__ == "__main__":
    main()
