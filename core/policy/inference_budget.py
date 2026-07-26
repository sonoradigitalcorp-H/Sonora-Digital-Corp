"""
Inference Budget — Control de gasto por tenant en SQLite.

Registra cada llamada costosa (API, GPU, TTS) y enforce límites:
- Daily cap por tenant
- Per-call max cost
- Auto-rechazo si excede
"""

import json
import logging
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger("policy.budget")

DB_PATH = Path(__file__).resolve().parent.parent.parent / "state" / "budget.db"


@dataclass
class BudgetResult:
    allowed: bool
    reason: str = ""
    daily_used: float = 0.0
    daily_limit: float = 0.0

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "daily_used": self.daily_used,
            "daily_limit": self.daily_limit,
        }


class InferenceBudget:
    """Rastrea y controla gastos de inferencia por tenant."""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DB_PATH
        self._ensure_db()

    def _ensure_db(self):
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant TEXT NOT NULL,
                action TEXT NOT NULL,
                cost REAL NOT NULL,
                model TEXT DEFAULT '',
                timestamp INTEGER NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS limits (
                tenant TEXT PRIMARY KEY,
                daily_cap REAL DEFAULT 10.0,
                max_per_call REAL DEFAULT 2.0
            )
        """)
        conn.commit()
        conn.close()

    def set_limits(self, tenant: str, daily_cap: float = 10.0, max_per_call: float = 2.0):
        conn = sqlite3.connect(str(self._db_path))
        conn.execute(
            "INSERT OR REPLACE INTO limits (tenant, daily_cap, max_per_call) VALUES (?, ?, ?)",
            (tenant, daily_cap, max_per_call),
        )
        conn.commit()
        conn.close()

    def get_limits(self, tenant: str) -> dict:
        conn = sqlite3.connect(str(self._db_path))
        row = conn.execute("SELECT daily_cap, max_per_call FROM limits WHERE tenant = ?", (tenant,)).fetchone()
        conn.close()
        if row:
            return {"daily_cap": row[0], "max_per_call": row[1]}
        return {"daily_cap": 10.0, "max_per_call": 2.0}

    def today_usage(self, tenant: str) -> float:
        """Suma de gastos del tenant hoy."""
        today_start = int(time.time()) - (int(time.time()) % 86400)
        conn = sqlite3.connect(str(self._db_path))
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM usage WHERE tenant = ? AND timestamp >= ?",
            (tenant, today_start),
        ).fetchone()
        conn.close()
        return row[0] if row else 0.0

    def last_n_calls(self, tenant: str, n: int = 10) -> list[dict]:
        conn = sqlite3.connect(str(self._db_path))
        rows = conn.execute(
            "SELECT action, cost, model, timestamp FROM usage WHERE tenant = ? ORDER BY id DESC LIMIT ?",
            (tenant, n),
        ).fetchall()
        conn.close()
        return [{"action": r[0], "cost": r[1], "model": r[2], "timestamp": r[3]} for r in rows]

    def can_execute(self, tenant: str, cost: float, action: str = "") -> BudgetResult:
        """Verifica si una acción puede ejecutarse según el presupuesto."""
        limits = self.get_limits(tenant)

        # 1. Per-call limit
        if cost > limits["max_per_call"]:
            return BudgetResult(
                allowed=False,
                reason=f"Costo ${cost:.2f} excede el máximo por llamada (${limits['max_per_call']:.2f})",
                daily_limit=limits["daily_cap"],
            )

        # 2. Daily cap
        used = self.today_usage(tenant)
        if used + cost > limits["daily_cap"]:
            remaining = max(0, limits["daily_cap"] - used)
            return BudgetResult(
                allowed=False,
                reason=f"Límite diario de ${limits['daily_cap']:.2f} alcanzado. "
                       f"Usado: ${used:.2f}, restante: ${remaining:.2f}",
                daily_used=used,
                daily_limit=limits["daily_cap"],
            )

        return BudgetResult(
            allowed=True,
            reason="OK",
            daily_used=used,
            daily_limit=limits["daily_cap"],
        )

    def record_usage(self, tenant: str, action: str, cost: float, model: str = ""):
        """Registra una llamada costosa."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute(
            "INSERT INTO usage (tenant, action, cost, model, timestamp) VALUES (?, ?, ?, ?, ?)",
            (tenant, action, cost, model, int(time.time())),
        )
        conn.commit()
        conn.close()
        logger.info(f"[{tenant}] ${cost:.3f} — {action} ({model})")

    def daily_report(self, tenant: str) -> dict:
        used = self.today_usage(tenant)
        limits = self.get_limits(tenant)
        calls = self.last_n_calls(tenant, 5)
        return {
            "tenant": tenant,
            "daily_used": round(used, 4),
            "daily_limit": limits["daily_cap"],
            "remaining": round(max(0, limits["daily_cap"] - used), 4),
            "recent_calls": calls,
        }
