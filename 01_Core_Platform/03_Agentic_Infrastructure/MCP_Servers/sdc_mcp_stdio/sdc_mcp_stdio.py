"""SDC MCP Server — stdio MCP server exposing core SDC tools to agents.

Provides tools:
  - okf_query: Query OKF knowledge base for verified business data
  - log_task: Log a task execution to the experience store
  - get_insights: Retrieve pending self-improvement insights
  - list_skills: List registered skills from self-improvement engine
  - call_sdc_sdk: Execute sdc_sdk utilities (hash, env check, etc.)

Protocol: MCP over stdio (JSON-RPC). Compatible with OpenClaw gateway.
"""

import json
import sys
import os
import time
import hashlib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENGINE_DIR = PROJECT_ROOT / "01_Core_Platform/05_SelfImprovement"
sys.path.insert(0, str(ENGINE_DIR))


def load_sdk():
    try:
        from experience_store import ExperienceStore
        from failure_miner import FailureMiner
        from sdc_sdk import get_env
        return ExperienceStore, FailureMiner, get_env
    except Exception:
        return None, None, None


def okf_query(query: str, tenant_id: str = "sdc") -> str:
    """Query the SDC OKF knowledge base."""
    okf_dir = PROJECT_ROOT / "01_Core_Platform/03_Agentic_Infrastructure/Databases/OKF_Knowledge"
    if not okf_dir.exists():
        return json.dumps({"error": "OKF directory not found", "path": str(okf_dir)})

    results = []
    for concept_file in okf_dir.rglob("*.json"):
        try:
            content = concept_file.read_text(encoding="utf-8")
            data = json.loads(content)
            data["_source"] = str(concept_file.relative_to(PROJECT_ROOT))
            results.append(data)
        except Exception:
            continue

    tenant_data = [r for r in results if tenant_id in str(r.get("_source", ""))]
    matches = tenant_data if tenant_data else results

    return json.dumps({
        "query": query,
        "tenant_id": tenant_id,
        "results": matches[:5],
        "total": len(results),
    }, ensure_ascii=False, indent=2)


def log_task(task_type: str, input_text: str, output: str, status: str = "success",
             duration_ms: int = 0, tenant_id: str = "sdc", agent_id: str = "") -> str:
    ExperienceStore, _, _ = load_sdk()
    if ExperienceStore is None:
        return json.dumps({"error": "ExperienceStore unavailable"})

    store = ExperienceStore()
    task_id = store.log_task_simple(
        task_type=task_type,
        input_text=input_text,
        output=output,
        status=status,
        duration_ms=duration_ms,
        tenant_id=tenant_id,
        agent_id=agent_id,
    )
    return json.dumps({"task_id": task_id, "status": "logged"})


def get_insights(limit: int = 10) -> str:
    from sdc_sdk import get_db
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, description, recommendation, impact_score FROM insights WHERE applied = 0 ORDER BY impact_score DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return json.dumps({
        "insights": [dict(r) for r in rows],
        "total": len(rows),
    }, ensure_ascii=False, indent=2)


def list_skills() -> str:
    skills_dir = ENGINE_DIR / "skills"
    if not skills_dir.exists():
        return json.dumps({"skills": [], "count": 0})

    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            metrics_path = skill_dir / "metrics.json"
            metrics = {}
            if metrics_path.exists():
                try:
                    metrics = json.loads(metrics_path.read_text())
                except Exception:
                    pass
            skills.append({
                "name": skill_dir.name,
                "version": metrics.get("version", 1.0),
                "avg_score": metrics.get("avg_score", 0),
                "last_evaluated": metrics.get("last_evaluated", 0),
                "failure_count": metrics.get("failure_count", 0),
            })

    return json.dumps({"skills": skills, "count": len(skills)}, ensure_ascii=False, indent=2)


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def check_env(key: str) -> str:
    from sdc_sdk import get_env
    val = get_env(key)
    if val:
        return json.dumps({"key": key, "set": True, "preview": val[:10] + "..."})
    return json.dumps({"key": key, "set": False})


# MCP protocol handler
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "okf_query",
            "description": "Query the SDC OKF knowledge base for verified business data (pricing, services, policies)",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The query to search for"},
                    "tenant_id": {"type": "string", "description": "Tenant ID (aztrotech, rye, sdc)", "default": "sdc"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "log_task",
            "description": "Log a task execution to the experience store for self-improvement tracking",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_type": {"type": "string"},
                    "input_text": {"type": "string"},
                    "output": {"type": "string"},
                    "status": {"type": "string", "enum": ["success", "failure", "partial"]},
                    "duration_ms": {"type": "integer", "default": 0},
                    "tenant_id": {"type": "string", "default": "sdc"},
                    "agent_id": {"type": "string"},
                },
                "required": ["task_type", "input_text", "output", "status"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_insights",
            "description": "Retrieve pending self-improvement insights from the failure miner",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 10},
                },
            },
        },
    },
    {
        "type": "function",
        "name": "list_skills",
        "description": "List registered skills from the self-improvement engine with metrics",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "function": {
            "name": "hash_text",
            "description": "Hash a text string for deduplication",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_env",
            "description": "Check if an environment variable is set",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    },
]


def handle_request(method: str, params: dict) -> dict:
    """Dispatch MCP request to tool handler."""
    handlers = {
        "okf_query": lambda: okf_query(params["query"], params.get("tenant_id", "sdc")),
        "log_task": lambda: log_task(
            params["task_type"], params["input_text"], params["output"],
            params["status"], params.get("duration_ms", 0),
            params.get("tenant_id", "sdc"), params.get("agent_id", ""),
        ),
        "get_insights": lambda: get_insights(params.get("limit", 10)),
        "list_skills": lambda: list_skills(),
        "hash_text": lambda: hash_text(params["text"]),
        "check_env": lambda: check_env(params["key"]),
    }
    handler = handlers.get(method)
    if handler:
        try:
            return {"content": [{"type": "text", "text": handler()}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": json.dumps({"error": str(e)})}], "isError": True}
    return {"content": [{"type": "text", "text": f"Unknown tool: {method}"}], "isError": True}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            if req.get("jsonrpc") != "2.0":
                continue

            method = req.get("method")
            req_id = req.get("id")
            params = req.get("params", {})

            if method == "initialize":
                resp = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "sdc-mcp-server", "version": "0.1.0"},
                    },
                }
            elif method == "tools/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"tools": TOOLS}}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                tool_params = params.get("arguments", {})
                result = handle_request(tool_name, tool_params)
                resp = {"jsonrpc": "2.0", "id": req_id, "result": result}
            elif method == "prompts/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"prompts": []}}
            elif method == "resources/list":
                resp = {"jsonrpc": "2.0", "id": req_id, "result": {"resources": []}}
            else:
                resp = {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method not found: {method}"}}

            print(json.dumps(resp), flush=True)
        except Exception as e:
            resp = {"jsonrpc": "2.0", "id": "error", "error": {"code": -32603, "message": str(e)}}
            print(json.dumps(resp), flush=True)


if __name__ == "__main__":
    main()
