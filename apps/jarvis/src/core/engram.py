import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

IMPORTANCE_LEVELS = {
    "critical": 3,
    "high": 2,
    "medium": 1,
    "low": 0,
}
MAX_PROMOTION_LEVEL = 3
DECAY_DAYS = 30

MEMORY_LAYERS = {
    "working": 0,
    "task": 1,
    "project": 2,
    "customer": 3,
    "business": 4,
    "historical": 5,
    "strategic": 6,
}

WRITE_LOCK_TIMEOUT_MS = 5000


class Engram:
    def __init__(self, db_path: str = None):
        if db_path is None:
            home_engram = Path.home() / ".engram" / "engram.db"
            db_path = str(home_engram if home_engram.exists() else Path(__file__).parent.parent.parent / "engram.db")
        self.db_path = db_path
        self._init_db()
        self._ensure_tables()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spec_id TEXT,
                    tag TEXT,
                    summary TEXT,
                    context TEXT,
                    importance INTEGER DEFAULT 1,
                    layer INTEGER DEFAULT 0,
                    access_count INTEGER DEFAULT 0,
                    last_accessed DATETIME,
                    timestamp DATETIME
                )
            """)
            self._migrate_schema(c)
            conn.commit()

    def _ensure_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            self._migrate_schema(c)
            c.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts
                USING fts5(summary, context, content='memories', content_rowid='id')
            """)
            conn.commit()

    def _migrate_schema(self, c):
        for col, col_type in [
            ("importance", "INTEGER DEFAULT 1"),
            ("layer", "INTEGER DEFAULT 0"),
            ("access_count", "INTEGER DEFAULT 0"),
            ("last_accessed", "DATETIME"),
        ]:
            try:
                c.execute(f"ALTER TABLE memories ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                pass

    def store_learning(
        self,
        spec_id: str,
        tag: str,
        summary: str,
        context: str,
        importance: str = "medium",
        layer: str = "project",
    ):
        level = IMPORTANCE_LEVELS.get(importance, 1)
        layer_num = MEMORY_LAYERS.get(layer, 2)
        with sqlite3.connect(self.db_path, timeout=WRITE_LOCK_TIMEOUT_MS / 1000) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO memories (spec_id, tag, summary, context, importance, layer, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (spec_id, tag, summary, context, level, layer_num, datetime.now().isoformat()),
            )
            rowid = c.lastrowid
            c.execute(
                "INSERT INTO memory_fts(rowid, summary, context) VALUES (?, ?, ?)",
                (rowid, summary, context),
            )
            conn.commit()

    def query_context(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        now = datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            try:
                c.execute(
                    """SELECT m.* FROM memories m
                       JOIN memory_fts f ON m.id = f.rowid
                       WHERE memory_fts MATCH ?
                       ORDER BY m.importance DESC, m.access_count DESC, rank
                       LIMIT ?""",
                    (query, limit),
                )
            except sqlite3.OperationalError:
                return []
            rows = [dict(row) for row in c.fetchall()]

            for row in rows:
                c.execute(
                    "UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id = ?",
                    (now.isoformat(), row["id"]),
                )
            conn.commit()
            return rows

    def get_by_spec(self, spec_id: str) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM memories WHERE spec_id = ?", (spec_id,))
            return [dict(row) for row in c.fetchall()]

    def promote(self, memory_id: int):
        with sqlite3.connect(self.db_path, timeout=WRITE_LOCK_TIMEOUT_MS / 1000) as conn:
            c = conn.cursor()
            c.execute("SELECT importance FROM memories WHERE id = ?", (memory_id,))
            row = c.fetchone()
            if row and row[0] < MAX_PROMOTION_LEVEL:
                c.execute(
                    "UPDATE memories SET importance = importance + 1 WHERE id = ?",
                    (memory_id,),
                )
                conn.commit()
                return True
            return False

    def demote(self, memory_id: int):
        with sqlite3.connect(self.db_path, timeout=WRITE_LOCK_TIMEOUT_MS / 1000) as conn:
            c = conn.cursor()
            c.execute("SELECT importance FROM memories WHERE id = ?", (memory_id,))
            row = c.fetchone()
            if row and row[0] > 0:
                c.execute(
                    "UPDATE memories SET importance = importance - 1 WHERE id = ?",
                    (memory_id,),
                )
                conn.commit()
                return True
            return False

    def apply_decay(self):
        now = datetime.now()
        with sqlite3.connect(self.db_path, timeout=WRITE_LOCK_TIMEOUT_MS / 1000) as conn:
            c = conn.cursor()
            c.execute(
                """UPDATE memories SET importance = MAX(0, importance - 1)
                   WHERE last_accessed IS NOT NULL
                   AND datetime(last_accessed) < datetime(?, ?)
                   AND importance > 0""",
                (now.isoformat(), f"-{DECAY_DAYS} days"),
            )
            conn.commit()

    def get_stats(self) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM memories")
            total = c.fetchone()[0]
            c.execute("SELECT importance, COUNT(*) FROM memories GROUP BY importance")
            by_level = {str(row[0]): row[1] for row in c.fetchall()}
            c.execute("SELECT layer, COUNT(*) FROM memories GROUP BY layer ORDER BY layer")
            by_layer = {str(row[0]): row[1] for row in c.fetchall()}
            c.execute("SELECT COUNT(*) FROM memories WHERE last_accessed IS NOT NULL")
            accessed = c.fetchone()[0]
            return {
                "total": total,
                "by_importance": by_level,
                "by_layer": by_layer,
                "accessed": accessed,
                "decay_days": DECAY_DAYS,
                "layers": MEMORY_LAYERS,
            }


engram = Engram()
