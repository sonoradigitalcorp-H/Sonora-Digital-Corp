"""Multi-tenant management for Agent Galaxy backend.

SQLite-backed tenant storage (preview mode).
Plans determine which agents are assigned:
  - explorador: 3 agents (mercurio, venus, tauro)
  - conquistador: 6 agents (+ marte, jupiter, saturno)
  - imperio: all 9 agents (+ urano, neptuno, pluton)
"""

import json
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from models import Tenant, VoiceConfig

log = logging.getLogger("galaxy.tenant")

DEFAULT_DB_PATH = os.getenv(
    "GALAXY_DB_PATH",
    str(Path(__file__).resolve().parent.parent / "state" / "galaxy_tenants.db"),
)

PLAN_AGENTS = {
    "explorador": ["mercurio", "venus", "tauro"],
    "conquistador": ["mercurio", "venus", "tauro", "marte", "jupiter", "saturno"],
    "imperio": ["mercurio", "venus", "tauro", "marte", "jupiter", "saturno", "urano", "neptuno", "pluton"],
}


class TenantStore:
    """SQLite-backed tenant storage with connection pooling."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def _conn(self):
        conn = self._get_conn()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tenants (
                    id TEXT PRIMARY KEY,
                    phone TEXT UNIQUE NOT NULL,
                    name TEXT DEFAULT '',
                    plan TEXT DEFAULT 'explorador',
                    agents TEXT DEFAULT '[]',
                    voice_config TEXT DEFAULT '{}',
                    channels TEXT DEFAULT '["whatsapp"]',
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tenants_phone ON tenants(phone)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tenants_status ON tenants(status)")
        log.info(f"Tenant store initialized at {self.db_path}")

    def create(self, phone: str, plan: str = "explorador", name: str = "") -> Tenant:
        """Create a new tenant with agents assigned by plan.

        Args:
            phone: WhatsApp phone number (unique identifier).
            plan: Plan tier (explorador, conquistador, imperio).
            name: Optional display name.

        Returns:
            Created Tenant model.

        Raises:
            ValueError: If plan is invalid or phone already exists.
        """
        if plan not in PLAN_AGENTS:
            raise ValueError(f"Invalid plan: {plan}. Must be one of {list(PLAN_AGENTS.keys())}")

        tenant_id = str(uuid.uuid4())
        agents = PLAN_AGENTS.get(plan, [])
        voice_config = VoiceConfig()
        channels = ["whatsapp"]
        created_at = datetime.utcnow().isoformat()

        with self._conn() as conn:
            conn.execute(
                """INSERT INTO tenants (id, phone, name, plan, agents, voice_config, channels, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    tenant_id,
                    phone,
                    name,
                    plan,
                    json.dumps(agents),
                    voice_config.model_dump_json(),
                    json.dumps(channels),
                    "active",
                    created_at,
                ),
            )

        tenant = Tenant(
            id=tenant_id,
            phone=phone,
            name=name,
            plan=plan,
            agents=agents,
            voice_config=voice_config,
            channels=channels,
            status="active",
            created_at=created_at,
        )
        log.info(f"Tenant created: id={tenant_id} phone={phone} plan={plan}")
        return tenant

    def get_by_id(self, tenant_id: str) -> Optional[Tenant]:
        """Retrieve a tenant by UUID."""
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM tenants WHERE id = ?", (tenant_id,)).fetchone()
        if not row:
            return None
        return self._row_to_tenant(row)

    def get_by_phone(self, phone: str) -> Optional[Tenant]:
        """Retrieve a tenant by phone number."""
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM tenants WHERE phone = ?", (phone,)).fetchone()
        if not row:
            return None
        return self._row_to_tenant(row)

    def list_all(self, status: Optional[str] = None) -> list[Tenant]:
        """List all tenants, optionally filtered by status."""
        with self._conn() as conn:
            if status:
                rows = conn.execute("SELECT * FROM tenants WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT * FROM tenants ORDER BY created_at DESC").fetchall()
        return [self._row_to_tenant(r) for r in rows]

    def update_status(self, tenant_id: str, status: str) -> Optional[Tenant]:
        """Update tenant status (active, trial, suspended)."""
        with self._conn() as conn:
            conn.execute("UPDATE tenants SET status = ? WHERE id = ?", (status, tenant_id))
        return self.get_by_id(tenant_id)

    def delete(self, tenant_id: str) -> bool:
        """Delete a tenant by ID."""
        with self._conn() as conn:
            cursor = conn.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
        return cursor.rowcount > 0

    def _row_to_tenant(self, row: sqlite3.Row) -> Tenant:
        """Convert a database row to a Tenant model."""
        return Tenant(
            id=row["id"],
            phone=row["phone"],
            name=row["name"],
            plan=row["plan"],
            agents=json.loads(row["agents"]),
            voice_config=VoiceConfig(**json.loads(row["voice_config"])) if row["voice_config"] and row["voice_config"] != "{}" else VoiceConfig(),
            channels=json.loads(row["channels"]),
            status=row["status"],
            created_at=row["created_at"],
        )


tenant_store = TenantStore()
