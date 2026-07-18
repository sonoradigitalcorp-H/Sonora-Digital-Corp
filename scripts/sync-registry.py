#!/usr/bin/env python3
"""sync-registry.py — Meta-registry sync engine.
Reads all 8 registries, unifies into state/registry/unified.yaml.
Usage: python scripts/sync-registry.py [--watch]
"""
import json
import os
import sys
import time
import yaml
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
STATE = BASE / "state" / "registry"
STATE.mkdir(parents=True, exist_ok=True)

OUTPUT = STATE / "unified.yaml"
DRIFT_LOG = STATE / "drift.log"
PREVIOUS_HASH = STATE / ".previous_hash"


def _hash_of(path):
    import hashlib
    return hashlib.md5(path.read_bytes() if path.exists() else b"").hexdigest()


def _read_yaml(path):
    if not path.exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f)
    return data or []


def _read_json(path):
    if not path.exists():
        return []
    with open(path) as f:
        data = json.load(f)
    return data or []


def _safe_id(name):
    return name.lower().replace(" ", "-").replace("_", "-")


def _sync_agents():
    """agents/registry.yaml"""
    raw = _read_yaml(BASE / "agents" / "registry.yaml")
    entries = []
    for a in raw.get("agents", []):
        entries.append({
            "id": _safe_id(a["name"]),
            "type": "agent",
            "name": a["name"],
            "role": a.get("role", ""),
            "tenant": a.get("tenant", ""),
            "tools": a.get("tools", []),
            "emits": a.get("emits", []),
            "triggers": a.get("triggers", []),
            "channel": a.get("channel", ""),
            "memory": a.get("memory", ""),
            "source": "agents/registry.yaml",
            "status": "active",
        })
    return entries


def _sync_capabilities():
    """capabilities/index.yaml (CapabilityBus) + config/registry.json (Planner)"""
    seen = set()
    entries = []

    for cap in _read_yaml(BASE / "capabilities" / "index.yaml").get("capabilities", []):
        eid = _safe_id(cap["id"])
        seen.add(eid)
        entries.append({
            "id": eid,
            "type": "capability",
            "name": cap.get("id", ""),
            "domain": cap.get("domain", ""),
            "agent": cap.get("agent", ""),
            "status": cap.get("status", "active"),
            "cost_tier": cap.get("cost_tier", 1),
            "source": "capabilities/index.yaml",
        })

    cfg = _read_json(BASE / "config" / "registry.json")
    for cap_name, cap_data in cfg.get("capabilities", {}).items():
        eid = _safe_id(cap_name)
        if eid in seen:
            continue
        seen.add(eid)
        entries.append({
            "id": eid,
            "type": "capability",
            "name": cap_name,
            "domain": cap_data.get("domain", ""),
            "providers": cap_data.get("providers", []),
            "status": "active",
            "source": "config/registry.json",
        })

    return entries


def _sync_tools():
    """tools/registry.json"""
    entries = []
    registry = _read_json(BASE / "tools" / "registry.json")
    for tool in registry.get("tools", []):
        entries.append({
            "id": _safe_id(tool.get("name", "")),
            "type": "tool",
            "name": tool.get("name", ""),
            "server": tool.get("server", ""),
            "has_doc": tool.get("has_doc", False),
            "source": "tools/registry.json",
            "status": "active",
        })
    return entries


def _sync_collectors():
    """collectors/registry.yaml"""
    raw = _read_yaml(BASE / "collectors" / "registry.yaml") or {}
    entries = []
    for p_name, p_data in raw.get("platforms", {}).items():
        entries.append({
            "id": _safe_id(p_name),
            "type": "collector",
            "name": p_name,
            "enabled": p_data.get("enabled", False),
            "schedule": p_data.get("schedule", ""),
            "priority": p_data.get("priority", 5),
            "source": "collectors/registry.yaml",
            "status": "active" if p_data.get("enabled") else "inactive",
        })
    return entries


def _sync_packs():
    """core/registries/pack-registry.yaml"""
    raw = _read_yaml(BASE / "core" / "registries" / "pack-registry.yaml") or {}
    entries = []
    for pk in raw.get("packs", []):
        if not isinstance(pk, dict):
            continue
        entries.append({
            "id": _safe_id(pk.get("id", "")),
            "type": "pack",
            "name": pk.get("name", pk.get("id", "")),
            "tier": pk.get("tier", ""),
            "price": pk.get("price", ""),
            "status": pk.get("status", "active"),
            "source": "core/registries/pack-registry.yaml",
        })
    return entries


def _sync_infra_tools():
    """core/registries/tool-registry.yaml"""
    raw = _read_yaml(BASE / "core" / "registries" / "tool-registry.yaml") or {}
    entries = []
    for tool in raw.get("tools", []):
        if not isinstance(tool, dict):
            continue
        entries.append({
            "id": _safe_id(tool.get("name", "")),
            "type": "infra_service",
            "name": tool.get("name", ""),
            "category": tool.get("category", ""),
            "source": "core/registries/tool-registry.yaml",
            "status": "active",
        })
    return entries


def _sync_hermes_skills():
    """~/.hermes/skills/ — category directories"""
    entries = []
    hermes_dir = Path.home() / ".hermes" / "skills"
    if hermes_dir.exists():
        for d in hermes_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                entries.append({
                    "id": f"hermes:{d.name}",
                    "type": "skill",
                    "name": d.name,
                    "ecosystem": "hermes",
                    "file_path": str(d.relative_to(Path.home()) if d.is_relative_to(Path.home()) else d),
                    "source": "~/.hermes/skills/",
                    "status": "active",
                })
    return entries


def _sync_openclaw_skills():
    """~/.openclaw/plugin-skills/"""
    entries = []
    oc_dir = Path.home() / ".openclaw" / "plugin-skills"
    if oc_dir.exists():
        for d in oc_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                entries.append({
                    "id": f"openclaw:{d.name}",
                    "type": "skill",
                    "name": d.name,
                    "ecosystem": "openclaw",
                    "file_path": str(d.relative_to(Path.home()) if d.is_relative_to(Path.home()) else d),
                    "source": "~/.openclaw/plugin-skills/",
                    "status": "active",
                })
    return entries


def _sync_skills():
    """skills/ directory (SDC skills)"""
    entries = []
    skills_dir = BASE / "skills"
    if skills_dir.exists():
        for f in skills_dir.iterdir():
            if f.suffix == ".skill.md":
                entries.append({
                    "id": _safe_id(f.stem.replace(".skill", "")),
                    "type": "skill",
                    "name": f.stem.replace(".skill", ""),
                    "ecosystem": "sdc",
                    "file_path": str(f.relative_to(BASE)),
                    "source": "skills/",
                    "status": "active",
                })
            elif f.is_dir() and (f / "SKILL.md").exists():
                entries.append({
                    "id": _safe_id(f.name),
                    "type": "skill",
                    "name": f.name,
                    "ecosystem": "sdc",
                    "file_path": str((f / "SKILL.md").relative_to(BASE)),
                    "source": "skills/",
                    "status": "active",
                })

    return entries


def _detect_drift(new_entries):
    """Compare with previous run and log changes."""
    old = []
    if OUTPUT.exists():
        data = _read_yaml(OUTPUT)
        if isinstance(data, dict):
            old = data.get("entries", [])
        elif isinstance(data, list):
            old = data

    old_map = {}
    for e in old:
        if isinstance(e, dict) and "id" in e and "type" in e:
            old_map[(e["id"], e["type"])] = e
    new_map = {(e["id"], e["type"]): e for e in new_entries}

    drifts = []
    for key in new_map:
        if key not in old_map:
            drifts.append(f"[NEW] {key[1]}/{key[0]}")
    for key in old_map:
        if key not in new_map:
            drifts.append(f"[DEL] {key[1]}/{key[0]}")

    if drifts:
        with open(DRIFT_LOG, "a") as f:
            ts = datetime.now(timezone.utc).isoformat()
            for d in drifts:
                f.write(f"{ts} {d}\n")
        print(f"Drifts detected: {len(drifts)}")
        for d in drifts[:10]:
            print(f"  {d}")
    else:
        print("No drift detected.")

    return drifts


def sync():
    print("Syncing registries...")
    all_entries = []
    all_entries.extend(_sync_agents())
    all_entries.extend(_sync_capabilities())
    all_entries.extend(_sync_tools())
    all_entries.extend(_sync_collectors())
    all_entries.extend(_sync_packs())
    all_entries.extend(_sync_infra_tools())
    all_entries.extend(_sync_skills())
    all_entries.extend(_sync_hermes_skills())
    all_entries.extend(_sync_openclaw_skills())

    summary = {}
    for e in all_entries:
        t = e["type"]
        summary[t] = summary.get(t, 0) + 1

    print(f"Total: {len(all_entries)} entities")
    for t, c in sorted(summary.items()):
        print(f"  {t}: {c}")

    _detect_drift(all_entries)
    with open(OUTPUT, "w") as f:
        yaml.dump({"meta": {"synced_at": datetime.now(timezone.utc).isoformat(), "total": len(all_entries)}, "entries": all_entries}, f, sort_keys=False)

    print(f"Written to {OUTPUT}")

    return all_entries


if __name__ == "__main__":
    sync()
    if "--watch" in sys.argv:
        print("Watching for changes (Ctrl+C to stop)...")
        while True:
            time.sleep(60)
            sync()
