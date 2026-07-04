"""Economics Kernel — rastrea costo por operación [FR1-FR4]"""
import json
import os
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO / "state" / "economics.db"
EVENT_SCRIPT = REPO / "scripts" / "emit-event.py"

MODEL_COSTS = {
    "ollama/qwen3:4b-64k": {"input": 0.0, "output": 0.0, "per_1k": True},
    "ollama/deepseek-r1:7b-64k": {"input": 0.0, "output": 0.0, "per_1k": True},
    "ollama/llama3.2:3b-64k": {"input": 0.0, "output": 0.0, "per_1k": True},
    "ollama/qwen3:1.7b-32k": {"input": 0.0, "output": 0.0, "per_1k": True},
    "ollama/qwen2.5:1.5b-32k": {"input": 0.0, "output": 0.0, "per_1k": True},
    "ollama/nomic-embed-text": {"input": 0.0, "output": 0.0, "per_1k": True},
}


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            operation TEXT NOT NULL,
            model TEXT,
            tokens_input INTEGER DEFAULT 0,
            tokens_output INTEGER DEFAULT 0,
            latency_ms INTEGER DEFAULT 0,
            cost_usd REAL DEFAULT 0.0,
            spec_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent TEXT NOT NULL,
            budget_tokens INTEGER DEFAULT 50000,
            period_hours INTEGER DEFAULT 24,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def track(agent, operation, model=None, tokens_input=0, tokens_output=0, latency_ms=0, spec_id=None):
    """Registra una operación con su costo"""
    cost = 0.0
    if model and model in MODEL_COSTS:
        rates = MODEL_COSTS[model]
        divisor = 1000 if rates["per_1k"] else 1
        cost = ((tokens_input * rates["input"]) + (tokens_output * rates["output"])) / divisor

    conn = init_db()
    conn.execute(
        "INSERT INTO operations (agent, operation, model, tokens_input, tokens_output, latency_ms, cost_usd, spec_id) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (agent, operation, model, tokens_input, tokens_output, latency_ms, cost, spec_id)
    )
    conn.commit()
    op_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()

    # Emit event with cost
    try:
        subprocess.run(
            [sys.executable, str(EVENT_SCRIPT),
             "--event", "cost.incurred",
             "--kernel", "economics",
             "--agent", agent,
             "--subject-type", "operation",
             "--subject-id", str(op_id),
             "--payload", json.dumps({
                 "operation": operation, "model": model,
                 "tokens_input": tokens_input, "tokens_output": tokens_output
             }),
             "--cost", json.dumps({
                 "tokens": tokens_input + tokens_output,
                 "model": model or "unknown",
                 "latency_ms": latency_ms,
                 "cost_usd": round(cost, 6)
             })],
            capture_output=True, timeout=5
        )
    except Exception:
        pass

    return {"id": op_id, "cost_usd": round(cost, 6)}


def report(agent=None, since=None, limit=20):
    """Genera reporte de costos"""
    conn = init_db()
    where = []
    params = []
    if agent:
        where.append("agent = ?")
        params.append(agent)
    if since:
        where.append("timestamp >= ?")
        params.append(since)

    query = "SELECT agent, operation, model, tokens_input, tokens_output, latency_ms, cost_usd, timestamp FROM operations"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    conn.close()

    totals = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "ops": 0, "latency": 0})
    for r in rows:
        a = r[0]
        totals[a]["tokens"] += r[3] + r[4]
        totals[a]["cost"] += r[6]
        totals[a]["ops"] += 1
        totals[a]["latency"] += r[5]

    return {
        "operations": [dict(zip(["agent", "operation", "model", "tokens_input", "tokens_output", "latency_ms", "cost_usd", "timestamp"], r)) for r in rows],
        "totals": {k: {**v, "cost": round(v["cost"], 4)} for k, v in totals.items()}
    }


def check_budget(agent, cost_tokens):
    """Verifica si el agente está dentro del budget"""
    conn = init_db()
    budget = conn.execute(
        "SELECT budget_tokens, period_hours FROM budgets WHERE agent = ? ORDER BY id DESC LIMIT 1",
        (agent,)
    ).fetchone()

    if not budget:
        return {"allowed": True, "budget": None}

    budget_tokens, period_hours = budget

    # Sum tokens in period
    used = conn.execute(
        "SELECT COALESCE(SUM(tokens_input + tokens_output), 0) FROM operations "
        "WHERE agent = ? AND timestamp >= datetime('now', ?)",
        (agent, f"-{period_hours} hours")
    ).fetchone()[0]

    conn.close()
    remaining = budget_tokens - used

    return {
        "allowed": remaining >= cost_tokens,
        "budget": budget_tokens,
        "used": used,
        "remaining": remaining,
        "cost_requested": cost_tokens
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Economics Kernel")
    parser.add_argument("action", choices=["track", "report", "budget"])
    parser.add_argument("--agent", help="Agent name")
    parser.add_argument("--operation", help="Operation name")
    parser.add_argument("--model", help="Model used")
    parser.add_argument("--tokens-input", type=int, default=0)
    parser.add_argument("--tokens-output", type=int, default=0)
    parser.add_argument("--latency-ms", type=int, default=0)
    parser.add_argument("--spec-id", help="Spec ID")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if args.action == "track":
        result = track(args.agent, args.operation, args.model, args.tokens_input, args.tokens_output, args.latency_ms, args.spec_id)
        print(json.dumps(result))
    elif args.action == "report":
        result = report(args.agent, limit=args.limit)
        print(json.dumps(result, indent=2))
    elif args.action == "budget":
        result = check_budget(args.agent, args.tokens_input + args.tokens_output)
        print(json.dumps(result, indent=2))
