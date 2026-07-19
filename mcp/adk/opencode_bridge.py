"""
ADK Bridge — Expone los 36 agentes del ADK como tools MCP.

Lee agentes de mcp/adk/agents/*.yaml y los expone via API REST
para que opencode y otros servicios puedan listarlos, consultarlos
y ejecutarlos.

Endpoints:
  GET  /adk/agents        — Listar todos los agentes
  GET  /adk/agents/{name} — Ver detalle de un agente
  POST /adk/agents/{name}/execute — Ejecutar un agente
  GET  /adk/health        — Health check
"""

import os
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent

app = FastAPI(
    title="Sonora ADK Bridge",
    version="1.0.0",
    docs_url="/adk/docs",
    redoc_url="/adk/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENTS_DIR = REPO / "mcp" / "adk" / "agents"


class ExecuteRequest(BaseModel):
    task: str = ""
    params: dict = {}


def _load_agents() -> dict:
    """Load all ADK agent YAMLs into a dict."""
    agents = {}
    if not AGENTS_DIR.exists():
        return agents
    for yaml_file in sorted(AGENTS_DIR.glob("*.yaml")):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)
            if data and data.get("name"):
                agents[data["name"]] = data
        except Exception as e:
            print(f"[adk] Error loading {yaml_file.name}: {e}")
    return agents


@app.get("/adk/agents")
def list_agents():
    agents = _load_agents()
    summary = []
    for name, data in agents.items():
        summary.append({
            "name": name,
            "version": data.get("version", "?"),
            "capability": data.get("capability", "?"),
            "maturity": data.get("maturity", "?"),
            "model": data.get("model", "?"),
            "provider": data.get("provider", "?"),
            "tools": len(data.get("tools", [])),
        })
    return {"agents": summary, "total": len(summary)}


@app.get("/adk/agents/{agent_name}")
def get_agent(agent_name: str):
    agents = _load_agents()
    agent = agents.get(agent_name)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_name}' not found. Available: {list(agents.keys())}")
    return {"agent": agent}


@app.post("/adk/agents/{agent_name}/execute")
async def execute_agent(agent_name: str, req: ExecuteRequest):
    agents = _load_agents()
    agent = agents.get(agent_name)
    if not agent:
        raise HTTPException(404, f"Agent '{agent_name}' not found")

    tools = agent.get("tools", [])
    capability = agent.get("capability", "unknown")
    policies = agent.get("policies", {})

    return {
        "agent": agent_name,
        "capability": capability,
        "task": req.task or f"execute_{capability}",
        "tools_available": tools,
        "policies": policies,
        "status": "routed",
        "note": "Agent execution requires LLM orchestration via the MCP gateway",
    }


@app.get("/adk/health")
def health():
    agents = _load_agents()
    return {
        "status": "ok",
        "agents_dir": str(AGENTS_DIR),
        "agents_loaded": len(agents),
        "agents": list(agents.keys()),
    }


@app.get("/adk/stats")
def stats():
    agents = _load_agents()
    capabilities = {}
    providers = {}
    maturities = {}
    for data in agents.values():
        cap = data.get("capability", "unknown")
        capabilities[cap] = capabilities.get(cap, 0) + 1
        prov = data.get("provider", "unknown")
        providers[prov] = providers.get(prov, 0) + 1
        mat = data.get("maturity", "unknown")
        maturities[mat] = maturities.get(mat, 0) + 1
    return {
        "total": len(agents),
        "by_capability": capabilities,
        "by_provider": providers,
        "by_maturity": maturities,
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("ADK_BRIDGE_PORT", "6401"))
    uvicorn.run("mcp.adk.opencode_bridge:app", host="0.0.0.0", port=port, reload=False)
