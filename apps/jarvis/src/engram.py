import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class Engram:
    """
    Persistent Context Memory for AI Agents.
    Uses SQLite with FTS5 for full-text search of technical lessons learned.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            home_engram = Path.home() / ".engram" / "engram.db"
            db_path = str(home_engram if home_engram.exists() else Path(__file__).parent.parent.parent / "engram.db")
        self.db_path = db_path
        self._init_db()
        self._ensure_tables()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spec_id TEXT,
                    tag TEXT,
                    summary TEXT,
                    context TEXT,
                    timestamp DATETIME
                )
            """)
            conn.commit()

    def _ensure_tables(self):
        """Ensure JARVIS-specific tables exist in the unified DB."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    spec_id TEXT,
                    tag TEXT,
                    summary TEXT,
                    context TEXT,
                    timestamp DATETIME
                )
            """)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts 
                USING fts5(summary, context, content='memories', content_rowid='id')
            """)
            conn.commit()

    def store_learning(self, spec_id: str, tag: str, summary: str, context: str):
        """Stores a technical lesson learned during a spec's completion."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO memories (spec_id, tag, summary, context, timestamp) VALUES (?, ?, ?, ?, ?)",
                (spec_id, tag, summary, context, datetime.now().isoformat()),
            )
            rowid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO memory_fts(rowid, summary, context) VALUES (?, ?, ?)",
                (rowid, summary, context),
            )
            conn.commit()

    def query_context(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Returns the most relevant previous solutions to a problem."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Full-text search for the query
            cursor.execute(
                "SELECT m.* FROM memories m JOIN memory_fts f ON m.id = f.rowid WHERE memory_fts MATCH ? ORDER BY rank LIMIT ?",
                (query, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_by_spec(self, spec_id: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM memories WHERE spec_id = ?", (spec_id,))
            return [dict(row) for row in cursor.fetchall()]


engram = Engram()
