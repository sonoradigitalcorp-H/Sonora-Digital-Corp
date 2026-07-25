"""Engram — Persistent memory with SQLite FTS5, 7 layers, automatic promotion/decay."""

import json
import logging
import os
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

LAYER_NAMES: dict[int, str] = {
    0: "working",
    1: "task",
    2: "project",
    3: "customer",
    4: "business",
    5: "historical",
    6: "strategic",
}

IMPORTANCE_LEVELS: dict[str, int] = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

MAX_PROMOTION_LEVEL: int = 3
DECAY_DAYS: int = 30


class Engram:
    """SQLite-backed persistent memory with FTS5, promotion, decay, and automatic migration."""

    def __init__(self, db_path: str = "", write_lock_timeout: float = 5.0):
        self.db_path = db_path or os.getenv("ENGRAM_DB_PATH", str(Path.home() / ".engram" / "engram.db"))
        self._lock = threading.Lock()
        self._lock_timeout = write_lock_timeout
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = self._get_conn()
        self._migrate_schema()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=self._lock_timeout, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _reconnect(self) -> None:
        try:
            self._conn.close()
        except Exception:
            pass
        self._conn = self._get_conn()

    def _migrate_schema(self) -> None:
        c = self._conn
        c.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                spec_id TEXT NOT NULL DEFAULT '',
                tag TEXT NOT NULL DEFAULT '',
                summary TEXT NOT NULL,
                context TEXT NOT NULL DEFAULT '',
                layer INTEGER NOT NULL DEFAULT 2,
                importance INTEGER NOT NULL DEFAULT 1,
                access_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT '',
                last_accessed TEXT
            )
        """)
        existing = {row[1] for row in c.execute("PRAGMA table_info(memories)")}
        migrations = {
            "importance": "INTEGER NOT NULL DEFAULT 1",
            "access_count": "INTEGER NOT NULL DEFAULT 0",
            "layer": "INTEGER NOT NULL DEFAULT 2",
            "last_accessed": "TEXT",
            "created_at": "TEXT NOT NULL DEFAULT ''",
        }
        for col, col_type in migrations.items():
            if col not in existing:
                c.execute(f"ALTER TABLE memories ADD COLUMN {col} {col_type}")
        c.execute("CREATE INDEX IF NOT EXISTS idx_memories_spec ON memories(spec_id)")
        if "layer" in existing or "layer" in migrations:
            c.execute("CREATE INDEX IF NOT EXISTS idx_memories_layer ON memories(layer)")
        if "importance" in existing or "importance" in migrations:
            c.execute("CREATE INDEX IF NOT EXISTS idx_memories_importance ON memories(importance)")
        try:
            c.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts "
                "USING fts5(summary, context, tag, content='memories', content_rowid='id')"
            )
        except sqlite3.OperationalError:
            log.warning("FTS5 not available — falling back to LIKE queries")
        c.commit()

    def _with_lock(self, func):
        acquired = self._lock.acquire(timeout=self._lock_timeout)
        if not acquired:
            raise TimeoutError(f"Could not acquire Engram write lock within {self._lock_timeout}s")
        try:
            try:
                return func()
            except sqlite3.ProgrammingError:
                self._reconnect()
                return func()
        finally:
            self._lock.release()

    def store_learning(
        self,
        spec_id: str,
        tag: str,
        summary: str,
        context: str = "",
        importance: str = "medium",
        layer: str = "project",
    ) -> int:
        def _store():
            now = datetime.now(timezone.utc).isoformat()
            imp = IMPORTANCE_LEVELS.get(importance, 1)
            lay = {v: k for k, v in LAYER_NAMES.items()}.get(layer, 2)
            cur = self._conn.execute(
                "INSERT INTO memories (spec_id, tag, summary, context, layer, importance, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (spec_id, tag, summary, context, lay, imp, now),
            )
            mem_id = cur.lastrowid
            try:
                self._conn.execute(
                    "INSERT INTO memories_fts(rowid, summary, context, tag) VALUES (?, ?, ?, ?)",
                    (mem_id, summary, context, tag),
                )
            except sqlite3.OperationalError:
                pass
            self._conn.commit()
            return mem_id
        return self._with_lock(_store)

    def query_context(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        try:
            rows = self._conn.execute(
                "SELECT m.* FROM memories m "
                "JOIN memories_fts fts ON m.id = fts.rowid "
                "WHERE memories_fts MATCH ? "
                "ORDER BY m.importance DESC, m.last_accessed DESC LIMIT ?",
                (query, limit),
            ).fetchall()
        except sqlite3.OperationalError:
            rows = self._conn.execute(
                "SELECT * FROM memories "
                "WHERE summary LIKE ? OR context LIKE ? OR tag LIKE ? "
                "ORDER BY importance DESC, last_accessed DESC LIMIT ?",
                (f"%{query}%", f"%{query}%", f"%{query}%", limit),
            ).fetchall()
        if query.strip() and rows:
            now = datetime.now(timezone.utc).isoformat()
            ids = [r["id"] for r in rows]
            placeholders = ",".join("?" for _ in ids)
            self._conn.execute(
                f"UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id IN ({placeholders})",
                (now, *ids),
            )
            self._conn.commit()
        return [dict(r) for r in rows]

    def get_by_spec(self, spec_id: str) -> list[dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM memories WHERE spec_id=? ORDER BY created_at DESC",
            (spec_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def promote(self, memory_id: int) -> bool:
        def _promote():
            row = self._conn.execute(
                "SELECT importance FROM memories WHERE id=?", (memory_id,)
            ).fetchone()
            if not row or row["importance"] >= MAX_PROMOTION_LEVEL:
                return False
            self._conn.execute(
                "UPDATE memories SET importance=importance+1 WHERE id=?",
                (memory_id,),
            )
            self._conn.commit()
            return True
        return self._with_lock(_promote)

    def demote(self, memory_id: int) -> bool:
        def _demote():
            row = self._conn.execute(
                "SELECT importance FROM memories WHERE id=?", (memory_id,)
            ).fetchone()
            if not row or row["importance"] <= 0:
                return False
            self._conn.execute(
                "UPDATE memories SET importance=importance-1 WHERE id=?",
                (memory_id,),
            )
            self._conn.commit()
            return True
        return self._with_lock(_demote)

    def apply_decay(self) -> int:
        def _decay():
            cutoff = (datetime.now(timezone.utc) - timedelta(days=DECAY_DAYS)).isoformat()
            count = self._conn.execute(
                "UPDATE memories SET importance = CASE WHEN importance > 0 THEN importance - 1 ELSE 0 END "
                "WHERE last_accessed IS NOT NULL AND last_accessed < ?",
                (cutoff,),
            ).rowcount
            self._conn.commit()
            return count
        return self._with_lock(_decay)

    def consolidate(self) -> int:
        def _consolidate():
            dups = self._conn.execute(
                "SELECT spec_id, summary, COUNT(*) as cnt, MIN(id) as keep_id "
                "FROM memories GROUP BY spec_id, summary HAVING cnt > 1"
            ).fetchall()
            removed = 0
            for dup in dups:
                self._conn.execute(
                    "DELETE FROM memories WHERE spec_id=? AND summary=? AND id!=?",
                    (dup["spec_id"], dup["summary"], dup["keep_id"]),
                )
                removed += dup["cnt"] - 1
            self._conn.commit()
            return removed
        return self._with_lock(_consolidate)

    def get_stats(self) -> dict[str, Any]:
        total = self._conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
        by_importance: dict[str, int] = {}
        for row in self._conn.execute(
            "SELECT CAST(importance AS TEXT) as imp, COUNT(*) as cnt FROM memories GROUP BY importance"
        ):
            by_importance[row["imp"]] = row["cnt"]
        by_layer: dict[str, int] = {}
        for lid, lname in LAYER_NAMES.items():
            cnt = self._conn.execute(
                "SELECT COUNT(*) FROM memories WHERE layer=?", (lid,)
            ).fetchone()[0]
            if cnt:
                by_layer[lname] = cnt
        return {
            "total": total,
            "by_importance": by_importance,
            "by_layer": by_layer,
            "decay_days": DECAY_DAYS,
        }


engram = Engram()
