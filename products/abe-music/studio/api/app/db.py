import sqlite3, json, os
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = os.environ.get("STUDIO_DB_PATH", "/data/studio.db")

def get_db():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_db():
    schema_path = os.environ.get("STUDIO_SCHEMA_PATH")
    if schema_path:
        schema = Path(schema_path)
    else:
        schema = Path(__file__).parent.parent.parent.parent / "schema.sql"
    if schema.exists():
        conn = get_db()
        conn.executescript(schema.read_text())
        conn.commit()
        conn.close()

def dict_from_row(row):
    if row is None:
        return None
    return dict(row)

def create_task(data: dict) -> str:
    import uuid
    task_id = uuid.uuid4().hex[:24]
    conn = get_db()
    conn.execute(
        """INSERT INTO studio_tasks
           (id, artist_id, task_type, model, prompt, duration, aspect_ratio,
            resolution, generate_audio, callback_url, image_urls, audio_urls)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (task_id, data.get("artist_id"), data.get("generation_type", "text-to-video"),
         data.get("model", "seedance-2-0"), data.get("prompt"),
         data.get("duration", 5), data.get("aspect_ratio", "9:16"),
         data.get("resolution", "720p"),
         1 if data.get("generate_audio", True) else 0,
         data.get("callback_url"),
         json.dumps(data.get("image_urls", [])),
         json.dumps(data.get("audio_urls", [])))
    )
    conn.commit()
    conn.close()
    return task_id

def update_task(task_id: str, updates: dict):
    safe = {}
    for k, v in updates.items():
        if v == "datetime('now')":
            from datetime import datetime
            safe[k] = datetime.utcnow().isoformat()
        else:
            safe[k] = v
    sets = ", ".join(f"{k}=?" for k in safe)
    vals = list(safe.values()) + [task_id]
    conn = get_db()
    conn.execute(f"UPDATE studio_tasks SET {sets} WHERE id=?", vals)
    conn.commit()
    conn.close()

def get_task(task_id: str) -> dict | None:
    conn = get_db()
    row = conn.execute("SELECT * FROM studio_tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return dict_from_row(row)

def get_tasks_by_status(status: str, limit: int = 20) -> list[dict]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM studio_tasks WHERE status=? ORDER BY created_at ASC LIMIT ?",
        (status, limit)
    ).fetchall()
    conn.close()
    return [dict_from_row(r) for r in rows]

def get_usage(user_id: int, month: str) -> dict | None:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM studio_usage WHERE user_id=? AND month=?",
        (user_id, month)
    ).fetchone()
    conn.close()
    return dict_from_row(row)

def increment_usage(user_id: int, month: str, reels: int = 1, credits: int = 0):
    conn = get_db()
    conn.execute(
        """INSERT INTO studio_usage (user_id, month, reels_generated, credits_consumed)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(user_id, month) DO UPDATE SET
               reels_generated = reels_generated + ?,
               credits_consumed = credits_consumed + ?""",
        (user_id, month, reels, credits, reels, credits)
    )
    conn.commit()
    conn.close()
