"""TaskQueue — cola persistente SQLite con estados [FR1]"""
import json
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = REPO / "state" / "execution" / "queue.db"


class TaskQueue:
    STATUSES = ("queued", "running", "completed", "failed", "cancelled")

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                agent TEXT NOT NULL,
                operation TEXT NOT NULL,
                params TEXT DEFAULT '{}',
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'queued',
                retries INTEGER DEFAULT 0,
                max_retries INTEGER DEFAULT 3,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                error TEXT,
                result TEXT,
                checkpoint TEXT,
                spec_id TEXT
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)")
        conn.commit()
        conn.close()

    def submit(self, agent: str, operation: str, params: dict = None,
               priority: int = 0, max_retries: int = 3, spec_id: str = None) -> dict:
        import uuid
        task_id = f"exec_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "INSERT INTO tasks (id, agent, operation, params, priority, status, max_retries, created_at, spec_id) "
            "VALUES (?, ?, ?, ?, ?, 'queued', ?, ?, ?)",
            (task_id, agent, operation, json.dumps(params or {}), priority, max_retries, now, spec_id)
        )
        conn.commit()
        conn.close()
        return {"id": task_id, "agent": agent, "operation": operation, "priority": priority, "status": "queued"}

    def dequeue(self, agent: str = None) -> Optional[dict]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM tasks WHERE status = 'queued'"
        params = []
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        query += " ORDER BY priority DESC, created_at ASC LIMIT 1"
        row = conn.execute(query, params).fetchone()
        if row:
            task = dict(row)
            now = datetime.now(timezone.utc).isoformat()
            conn.execute("UPDATE tasks SET status = 'running', started_at = ? WHERE id = ?", (now, task["id"]))
            conn.commit()
            conn.close()
            task["status"] = "running"
            task["started_at"] = now
            task["params"] = json.loads(task.get("params", "{}"))
            return task
        conn.close()
        return None

    def complete(self, task_id: str, result: dict = None):
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            "UPDATE tasks SET status = 'completed', completed_at = ?, result = ? WHERE id = ?",
            (now, json.dumps(result or {}), task_id)
        )
        conn.commit()
        conn.close()

    def fail(self, task_id: str, error: str, retry: bool = True):
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute("SELECT retries, max_retries FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row:
            retries, max_retries = row
            if retry and retries < max_retries:
                now = datetime.now(timezone.utc).isoformat()
                conn.execute(
                    "UPDATE tasks SET status = 'queued', retries = retries + 1, error = ?, started_at = NULL WHERE id = ?",
                    (error, task_id)
                )
            else:
                conn.execute(
                    "UPDATE tasks SET status = 'failed', error = ?, completed_at = ? WHERE id = ?",
                    (error, datetime.now(timezone.utc).isoformat(), task_id)
                )
        conn.commit()
        conn.close()

    def cancel(self, task_id: str):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("UPDATE tasks SET status = 'cancelled', completed_at = ? WHERE id = ? AND status IN ('queued', 'running')",
                     (datetime.now(timezone.utc).isoformat(), task_id))
        conn.commit()
        conn.close()

    def status(self, task_id: str) -> Optional[dict]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if row:
            task = dict(row)
            task["params"] = json.loads(task.get("params", "{}"))
            task["result"] = json.loads(task.get("result", "{}")) if task.get("result") else None
            return task
        return None

    def list_tasks(self, status: str = None, agent: str = None, limit: int = 50) -> list[dict]:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        if agent:
            query += " AND agent = ?"
            params.append(agent)
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        rows = conn.execute(query, params).fetchall()
        conn.close()
        tasks = []
        for r in rows:
            t = dict(r)
            t["params"] = json.loads(t.get("params", "{}"))
            t["result"] = json.loads(t.get("result", "{}")) if t.get("result") else None
            tasks.append(t)
        return tasks

    def stats(self) -> dict:
        conn = sqlite3.connect(str(self.db_path))
        rows = conn.execute(
            "SELECT status, COUNT(*) as count FROM tasks GROUP BY status"
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        conn.close()
        statuses = {r[0]: r[1] for r in rows}
        return {
            "total": total,
            "by_status": statuses,
            "queued": statuses.get("queued", 0),
            "running": statuses.get("running", 0),
            "completed": statuses.get("completed", 0),
            "failed": statuses.get("failed", 0),
            "cancelled": statuses.get("cancelled", 0),
        }

    def save_checkpoint(self, task_id: str, data: dict):
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("UPDATE tasks SET checkpoint = ? WHERE id = ?", (json.dumps(data), task_id))
        conn.commit()
        conn.close()

    def get_checkpoint(self, task_id: str) -> Optional[dict]:
        conn = sqlite3.connect(str(self.db_path))
        row = conn.execute("SELECT checkpoint FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        if row and row[0]:
            data = json.loads(row[0])
            if data:
                return data
        return None

    def clean_old(self, hours: int = 72):
        conn = sqlite3.connect(str(self.db_path))
        from datetime import datetime, timedelta
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        conn.execute("DELETE FROM tasks WHERE completed_at IS NOT NULL AND completed_at < ?", (cutoff,))
        conn.commit()
        conn.close()
