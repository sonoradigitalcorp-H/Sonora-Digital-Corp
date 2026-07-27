"""Marketplace — Listado de agentes y paquetes disponibles"""

import json
from pathlib import Path
from fastapi import APIRouter

REPO = Path(__file__).resolve().parent.parent.parent.parent.parent
PACKAGES_DIR = REPO / "products" / "agent-marketplace" / "packages"
AGENTS_DIR = REPO / "products" / "agent-marketplace" / "agents"

router = APIRouter(tags=["marketplace"])


@router.get("/packages")
async def list_packages():
    packages = []
    for f in sorted(PACKAGES_DIR.glob("*.json")):
        data = json.loads(f.read_text())
        packages.append({
            "id": data["id"],
            "name": data["name"],
            "price": data["price"],
            "setup_fee": data["setup_fee"],
            "description": data["description"],
            "features": data["features"],
            "agents_count": len(data["agents"]),
        })
    return {"packages": packages}


@router.get("/packages/{package_id}")
async def get_package(package_id: str):
    f = PACKAGES_DIR / f"{package_id}.json"
    if not f.exists():
        return {"error": "Package not found"}
    return json.loads(f.read_text())


@router.get("/agents")
async def list_agents():
    agents = []
    for agent_dir in sorted(AGENTS_DIR.iterdir()):
        def_file = agent_dir / "definition.json"
        if def_file.exists():
            data = json.loads(def_file.read_text())
            mcp_file = agent_dir / "mcp.json"
            mcps = json.loads(mcp_file.read_text())["required_mcp_servers"] if mcp_file.exists() else []
            agents.append({
                "id": data["id"],
                "name": data["name"],
                "description": data["description"],
                "capabilities": data["capabilities"],
                "mcps": [m["name"] for m in mcps],
            })
    return {"agents": agents}
