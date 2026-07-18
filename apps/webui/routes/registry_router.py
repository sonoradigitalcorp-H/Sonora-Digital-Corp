"""Registry API — GET /api/v1/registry/{type}[/{id}]"""
from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1/registry", tags=["registry"])

BASE = Path(__file__).resolve().parent.parent.parent.parent
REGISTRY_FILE = BASE / "state" / "registry" / "unified.yaml"


def _load():
    if not REGISTRY_FILE.exists():
        return []
    with open(REGISTRY_FILE) as f:
        data = yaml.safe_load(f)
    return data.get("entries", []) if data else []


@router.get("")
def list_all():
    entries = _load()
    types = {}
    for e in entries:
        t = e.get("type", "unknown")
        types[t] = types.get(t, 0) + 1
    return {
        "total": len(entries),
        "types": types,
        "endpoints": {
            "/api/v1/registry/{type}": "List by type",
            "/api/v1/registry/{type}/{id}": "Get specific entity",
        },
    }


@router.get("/{entity_type}")
def list_by_type(entity_type: str):
    entries = _load()
    filtered = [e for e in entries if e.get("type") == entity_type]
    if not filtered:
        raise HTTPException(404, f"No entries of type '{entity_type}'")
    return {"type": entity_type, "count": len(filtered), "entries": filtered}


@router.get("/{entity_type}/{entity_id}")
def get_by_id(entity_type: str, entity_id: str):
    entries = _load()
    for e in entries:
        if e.get("type") == entity_type and e.get("id") == entity_id:
            return e
    raise HTTPException(404, f"'{entity_id}' not found in '{entity_type}'")
