"""Cost Intelligence MCP Server — Track every operation cost per tenant in real time.

FR-01: Registrar cada operación con su costo real por tenant.
FR-02: Reportes agregados de costo por tenant/período.
FR-03: Alertas cuando un cliente cuesta más de lo que paga.
"""

import json
import os
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def _get_db_path() -> Path:
    return Path(os.environ.get("COST_DB_PATH", str(REPO / "data" / "cost_tracker.db")))


def _get_db() -> sqlite3.Connection:
    db_path = _get_db_path()
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS cost_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            operation TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT,
            tokens_in INTEGER DEFAULT 0,
            tokens_out INTEGER DEFAULT 0,
            cost_usd REAL NOT NULL,
            duration_ms INTEGER DEFAULT 0,
            meta TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_cost_tenant ON cost_log(tenant_id);
        CREATE INDEX IF NOT EXISTS idx_cost_created ON cost_log(created_at);
    """)
    conn.commit()
    conn.close()


def _get_rates() -> dict:
    import yaml
    rates_path = REPO / "config" / "cost-rates.yaml"
    if rates_path.exists():
        with open(rates_path) as f:
            return yaml.safe_load(f)
    return {}


async def log_cost(
    tenant_id: str,
    operation: str,
    provider: str,
    cost_usd: float,
    model: str = "",
    tokens_in: int = 0,
    tokens_out: int = 0,
    duration_ms: int = 0,
    meta: str = "",
) -> str:
    if not tenant_id:
        return json.dumps({"error": "tenant_id is required"})
    if cost_usd < 0:
        return json.dumps({"error": "cost_usd cannot be negative"})

    _init_db()
    conn = _get_db()
    conn.execute(
        """INSERT INTO cost_log
           (tenant_id, operation, provider, model, tokens_in, tokens_out, cost_usd, duration_ms, meta)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (tenant_id, operation, provider, model, tokens_in, tokens_out, cost_usd, duration_ms, meta),
    )
    conn.commit()
    log_id = conn.execute("SELECT last_insert_rowid() as rid").fetchone()["rid"]
    conn.close()
    return json.dumps({"logged": True, "id": log_id, "cost_usd": cost_usd, "tenant_id": tenant_id})


async def get_tenant_costs(tenant_id: str, days: int = 30) -> str:
    if not tenant_id:
        return json.dumps({"error": "tenant_id is required"})
    _init_db()
    conn = _get_db()
    rows = conn.execute(
        """SELECT operation, provider, model, COUNT(*) as count,
                  SUM(cost_usd) as total_cost, SUM(duration_ms) as total_duration
           FROM cost_log
           WHERE tenant_id = ? AND created_at >= datetime('now', ?)
           GROUP BY operation, provider, model
           ORDER BY total_cost DESC""",
        (tenant_id, f"-{days} days"),
    ).fetchall()

    total = sum(r["total_cost"] for r in rows)
    result = {
        "tenant_id": tenant_id,
        "period_days": days,
        "total_cost_usd": round(total, 6),
        "breakdown": [dict(r) for r in rows],
        "by_provider": {},
    }
    for r in rows:
        p = r["provider"]
        if p not in result["by_provider"]:
            result["by_provider"][p] = 0
        result["by_provider"][p] += r["total_cost"]
    result["by_provider"] = {k: round(v, 6) for k, v in result["by_provider"].items()}
    conn.close()
    return json.dumps(result)


async def get_all_tenants_summary(days: int = 30) -> str:
    _init_db()
    conn = _get_db()
    rows = conn.execute(
        """SELECT tenant_id, SUM(cost_usd) as total_cost, COUNT(*) as operations
           FROM cost_log
           WHERE created_at >= datetime('now', ?)
           GROUP BY tenant_id
           ORDER BY total_cost DESC""",
        (f"-{days} days",),
    ).fetchall()

    total = sum(r["total_cost"] for r in rows)
    conn.close()
    return json.dumps({
        "period_days": days,
        "total_cost_usd": round(total, 6),
        "tenants": [dict(r) for r in rows],
        "tenant_count": len(rows),
    })


async def calculate_llm_cost(model: str, tokens_in: int, tokens_out: int) -> str:
    rates = _get_rates()
    llm_rates = rates.get("llm", {}).get("openrouter", {})
    model_rate = llm_rates.get(model, {"input_per_1k": 0.001, "output_per_1k": 0.002})

    cost = (tokens_in / 1000) * model_rate["input_per_1k"] + (tokens_out / 1000) * model_rate["output_per_1k"]
    return json.dumps({
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": round(cost, 6),
        "rate_input_per_1k": model_rate["input_per_1k"],
        "rate_output_per_1k": model_rate["output_per_1k"],
    })


async def calculate_fal_cost(operation: str, quantity: int = 1) -> str:
    rates = _get_rates()
    fal_rates = rates.get("fal_ai", {})
    rate = fal_rates.get(operation, {})

    if isinstance(rate, dict):
        keys = ["per_image", "per_training", "per_video_5s", "per_sync", "per_clone", "per_char"]
        unit_cost = next((rate[k] for k in keys if rate.get(k)), 0)
    else:
        unit_cost = rate

    total = unit_cost * quantity
    return json.dumps({
        "operation": operation,
        "quantity": quantity,
        "unit_cost_usd": unit_cost,
        "total_cost_usd": round(total, 6),
    })


MCP_TOOLS = {
    "log_cost": {
        "description": "Register a cost operation for a tenant in the cost tracker",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant identifier"},
                "operation": {"type": "string", "description": "Operation type (llm_chat, gen_image, gen_video, train_lora, etc)"},
                "provider": {"type": "string", "description": "Provider (openrouter, fal_ai, supabase, infra)"},
                "cost_usd": {"type": "number", "description": "Cost in USD"},
                "model": {"type": "string", "description": "Model name (optional)"},
                "tokens_in": {"type": "number", "description": "Input tokens (optional)"},
                "tokens_out": {"type": "number", "description": "Output tokens (optional)"},
                "duration_ms": {"type": "number", "description": "Duration in ms (optional)"},
            },
            "required": ["tenant_id", "operation", "provider", "cost_usd"],
        },
        "handler": lambda args: log_cost(
            args["tenant_id"], args["operation"], args["provider"], args["cost_usd"],
            args.get("model", ""), args.get("tokens_in", 0), args.get("tokens_out", 0),
            args.get("duration_ms", 0), args.get("meta", ""),
        ),
    },
    "get_tenant_costs": {
        "description": "Get cost breakdown for a specific tenant",
        "input_schema": {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string", "description": "Tenant identifier"},
                "days": {"type": "number", "description": "Lookback period in days", "default": 30},
            },
            "required": ["tenant_id"],
        },
        "handler": lambda args: get_tenant_costs(args["tenant_id"], args.get("days", 30)),
    },
    "get_all_tenants_summary": {
        "description": "Get cost summary across all tenants",
        "input_schema": {
            "type": "object",
            "properties": {
                "days": {"type": "number", "description": "Lookback period in days", "default": 30},
            },
            "required": [],
        },
        "handler": lambda args: get_all_tenants_summary(args.get("days", 30)),
    },
    "calculate_llm_cost": {
        "description": "Calculate LLM call cost based on model and tokens",
        "input_schema": {
            "type": "object",
            "properties": {
                "model": {"type": "string", "description": "Model name (gpt-4o-mini, claude-3.5-sonnet, etc)"},
                "tokens_in": {"type": "number", "description": "Input tokens"},
                "tokens_out": {"type": "number", "description": "Output tokens"},
            },
            "required": ["model", "tokens_in", "tokens_out"],
        },
        "handler": lambda args: calculate_llm_cost(args["model"], args["tokens_in"], args["tokens_out"]),
    },
    "calculate_fal_cost": {
        "description": "Calculate FAL.ai operation cost based on current rates",
        "input_schema": {
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Operation (flux_lora_train, flux_lora_inference, kling_video_pro, etc)"},
                "quantity": {"type": "number", "description": "Quantity", "default": 1},
            },
            "required": ["operation"],
        },
        "handler": lambda args: calculate_fal_cost(args["operation"], args.get("quantity", 1)),
    },
}
