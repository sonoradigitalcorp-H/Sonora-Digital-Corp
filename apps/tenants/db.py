"""SQLite database layer for the Multi-Tenant System."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .models import (
    Agent,
    AgentType,
    EnvVar,
    HealthCheck,
    HealthStatus,
    Tenant,
    TenantPlan,
    TenantStatus,
)

DB_PATH = Path("/home/ubuntu/sonora-digital-corp/state/tenants.db")


def _ensure_dir():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _conn():
    _ensure_dir()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _conn() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS tenants (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'trial',
                status TEXT NOT NULL DEFAULT 'trial',
                created_at TEXT NOT NULL,
                last_active TEXT NOT NULL,
                api_key TEXT NOT NULL DEFAULT '',
                webhook_token TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS env_vars (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                is_secret INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            );
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                agent_type TEXT NOT NULL DEFAULT 'voice',
                status TEXT NOT NULL DEFAULT 'active',
                config TEXT NOT NULL DEFAULT '{}',
                clients_count INTEGER NOT NULL DEFAULT 0,
                hours_worked REAL NOT NULL DEFAULT 0.0,
                clients_helped INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            );
            CREATE TABLE IF NOT EXISTS health_checks (
                id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ok',
                message TEXT NOT NULL DEFAULT '',
                metrics TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (tenant_id) REFERENCES tenants(id)
            );
            CREATE INDEX IF NOT EXISTS idx_env_vars_tenant ON env_vars(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_agents_tenant ON agents(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_health_checks_tenant ON health_checks(tenant_id);
            CREATE INDEX IF NOT EXISTS idx_health_checks_ts ON health_checks(timestamp);
        """)


def _gen_id() -> str:
    return uuid.uuid4().hex[:12]


# ── Tenant CRUD ──


def create_tenant(name: str, email: str, plan: str = "trial") -> Tenant:
    tid = _gen_id()
    api_key = uuid.uuid4().hex
    webhook_token = uuid.uuid4().hex
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as c:
        c.execute(
            """INSERT INTO tenants (id, name, email, plan, status, created_at, last_active, api_key, webhook_token)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tid, name, email, plan, "trial", now, now, api_key, webhook_token),
        )
    return get_tenant(tid)


def get_tenant(tid: str) -> Tenant | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM tenants WHERE id = ?", (tid,)).fetchone()
    if not row:
        return None
    return Tenant(**dict(row))


def get_all_tenants() -> list[Tenant]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM tenants ORDER BY created_at DESC").fetchall()
    return [Tenant(**dict(r)) for r in rows]


def update_tenant_status(tid: str, status: str):
    now = datetime.now(timezone.utc).isoformat()
    with _conn() as c:
        c.execute("UPDATE tenants SET status = ?, last_active = ? WHERE id = ?", (status, now, tid))


# ── Env Vars ──


def set_env_vars(tenant_id: str, vars: list[tuple[str, str, bool]]):
    with _conn() as c:
        for key, value, is_secret in vars:
            eid = _gen_id()
            c.execute(
                "INSERT INTO env_vars (id, tenant_id, key, value, is_secret) VALUES (?, ?, ?, ?, ?)",
                (eid, tenant_id, key, value, int(is_secret)),
            )


def get_env_vars(tenant_id: str) -> list[EnvVar]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM env_vars WHERE tenant_id = ?", (tenant_id,)
        ).fetchall()
    return [EnvVar(id=r["id"], tenant_id=r["tenant_id"], key=r["key"], value=r["value"], is_secret=bool(r["is_secret"])) for r in rows]


# ── Agents ──


def create_agent(tenant_id: str, agent_type: str = "voice", config: dict | None = None) -> Agent:
    aid = _gen_id()
    cfg = json.dumps(config or {})
    with _conn() as c:
        c.execute(
            """INSERT INTO agents (id, tenant_id, agent_type, status, config)
               VALUES (?, ?, ?, 'active', ?)""",
            (aid, tenant_id, agent_type, cfg),
        )
    return get_agent(aid)


def get_agent(aid: str) -> Agent | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM agents WHERE id = ?", (aid,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["config"] = json.loads(d["config"])
    return Agent(**d)


def get_agents(tenant_id: str) -> list[Agent]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM agents WHERE tenant_id = ?", (tenant_id,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["config"] = json.loads(d["config"])
        result.append(Agent(**d))
    return result


# ── Health Checks ──


def create_health_check(tenant_id: str, status: str = "ok", message: str = "", metrics: dict | None = None) -> HealthCheck:
    hid = _gen_id()
    now = datetime.now(timezone.utc).isoformat()
    m = json.dumps(metrics or {})
    with _conn() as c:
        c.execute(
            """INSERT INTO health_checks (id, tenant_id, timestamp, status, message, metrics)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (hid, tenant_id, now, status, message, m),
        )
    return get_health_check(hid)


def get_health_check(hid: str) -> HealthCheck | None:
    with _conn() as c:
        row = c.execute("SELECT * FROM health_checks WHERE id = ?", (hid,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["metrics"] = json.loads(d["metrics"])
    return HealthCheck(**d)


def get_latest_health(tenant_id: str) -> HealthCheck | None:
    with _conn() as c:
        row = c.execute(
            "SELECT * FROM health_checks WHERE tenant_id = ? ORDER BY timestamp DESC LIMIT 1",
            (tenant_id,),
        ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["metrics"] = json.loads(d["metrics"])
    return HealthCheck(**d)


def get_all_health_checks(tenant_id: str) -> list[HealthCheck]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM health_checks WHERE tenant_id = ? ORDER BY timestamp DESC",
            (tenant_id,),
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["metrics"] = json.loads(d["metrics"])
        result.append(HealthCheck(**d))
    return result
