#!/usr/bin/env python3
"""Skill Registry — Índice unificado de skills de OpenCode, Hermes, y SDCLas skills de Hermes son docs de referencia. Este registry las indexa para que el bot las use on-demand via LLM.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional

REGISTRY_PATH = Path(__file__).parent.parent.parent / "ops" / "state" / "skill-registry.json"

HERMES_SKILLS = Path.home() / ".hermes" / "hermes-agent" / "skills"
OPENCODE_SKILLS = Path(__file__).parent.parent.parent / "skills"
LOCAL_SKILLS = Path(__file__).parent.parent.parent / "tenants" / "Aztrotech" / "skills"


def scan_hermes_skills() -> Dict[str, dict]:
    """Scan Hermes reference skills."""
    skills = {}
    if not HERMES_SKILLS.exists():
        return skills
    for skill_dir in HERMES_SKILLS.iterdir():
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        desc_file = skill_dir / "DESCRIPTION.md"
        desc = ""
        if desc_file.exists():
            desc = desc_file.read_text()[:200]
        
        skill_files = list(skill_dir.rglob("SKILL.md"))
        skills[f"hermes:{name}"] = {
            "name": name,
            "source": "hermes",
            "description": desc,
            "skill_files": [str(f) for f in skill_files[:3]],
            "type": "reference",
        }
    return skills


def scan_opencode_skills() -> Dict[str, dict]:
    """Scan OpenCode skills (MCP servers, tools)."""
    skills = {}
    if not OPENCODE_SKILLS.exists():
        return skills
    for skill_dir in OPENCODE_SKILLS.iterdir():
        if not skill_dir.is_dir():
            continue
        name = skill_dir.name
        readme = skill_dir / "README.md"
        desc = ""
        if readme.exists():
            desc = readme.read_text()[:200]
        
        py_files = list(skill_dir.rglob("*.py"))
        skills[f"opencode:{name}"] = {
            "name": name,
            "source": "opencode",
            "description": desc,
            "type": "executable" if py_files else "reference",
            "files": [str(f) for f in py_files[:3]],
        }
    return skills


def scan_local_skills() -> Dict[str, dict]:
    """Scan local Aztrotech skills."""
    skills = {}
    if not LOCAL_SKILLS.exists():
        return skills
    for f in LOCAL_SKILLS.iterdir():
        if f.suffix in (".yaml", ".yml"):
            try:
                data = yaml.safe_load(f.read_text())
                skills[f"local:{f.stem}"] = {
                    "name": f.stem,
                    "source": "aztrotech",
                    "description": str(data.get("description", ""))[:200],
                    "type": "config",
                }
            except Exception:
                pass
    return skills


def build_registry() -> dict:
    """Build unified skill registry."""
    registry = {
        "version": "1.0",
        "updated": "",
        "skills": {},
    }
    registry["skills"].update(scan_hermes_skills())
    registry["skills"].update(scan_opencode_skills())
    registry["skills"].update(scan_local_skills())
    return registry


def save_registry():
    """Save registry to JSON."""
    import datetime
    registry = build_registry()
    registry["updated"] = datetime.datetime.now().isoformat()
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
    print(f"Registry saved: {len(registry['skills'])} skills")
    for source in ["hermes", "opencode", "aztrotech"]:
        count = sum(1 for s in registry["skills"].values() if s["source"] == source)
        if count:
            print(f"  {source}: {count} skills")


def search_skills(query: str) -> List[dict]:
    """Search skills by query."""
    if not REGISTRY_PATH.exists():
        save_registry()
    registry = json.loads(REGISTRY_PATH.read_text())
    results = []
    q = query.lower()
    for key, skill in registry["skills"].items():
        if q in skill["name"].lower() or q in skill.get("description", "").lower():
            results.append(skill)
    return results


if __name__ == "__main__":
    save_registry()
    print("\n--- Search examples ---")
    for q in ["email", "autonomous", "github", "voice", "sales"]:
        results = search_skills(q)
        print(f"  '{q}': {len(results)} skills")