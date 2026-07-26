import asyncio
import json
import logging
import os
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger("voice-realtime.session_db")

_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="session_db")


def _run_sync(fn):
    """Ejecuta una función síncrona en un executor para compatibilidad async."""

    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, fn, *args, **kwargs)

    return wrapper


class SessionDB:
    """Persistencia SQLite para sesiones de Mystic Voice.

    Thread-safe mediante reentrant lock. Tolerante a corrupción de DB
    (borra y recrea automáticamente).
    """

    def __init__(self, db_path: str = "state/mystic_sessions.db") -> None:
        self.db_path = db_path
        self._lock = threading.RLock()
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _try_recover(self) -> None:
        logger.warning("Intentando recuperar DB corrupta: borrando y recreando")
        with self._lock:
            try:
                conn = self._connect()
                conn.close()
            except Exception:
                pass
            try:
                os.remove(self.db_path)
                logger.info("DB corrupta eliminada, recreando desde cero")
            except Exception as exc:
                logger.error("No se pudo eliminar DB corrupta: %s", exc)
            self.init_db()

    def init_db(self) -> None:
        """Crea tablas si no existen."""
        try:
            with self._lock:
                conn = self._connect()
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS sessions (
                        id TEXT PRIMARY KEY,
                        user_id TEXT DEFAULT '',
                        history TEXT NOT NULL DEFAULT '[]',
                        context TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT (datetime('now')),
                        updated_at TEXT DEFAULT (datetime('now'))
                    );
                    CREATE TABLE IF NOT EXISTS interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        intent_id TEXT,
                        latency_ms INTEGER,
                        created_at TEXT DEFAULT (datetime('now')),
                        FOREIGN KEY (session_id) REFERENCES sessions(id)
                    );
                    CREATE INDEX IF NOT EXISTS idx_interactions_session
                        ON interactions(session_id, created_at);
                    """
                )
                # Migracion: agregar user_id si no existe
                try:
                    conn.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT DEFAULT ''")
                except:
                    pass  # ya existe
                # Indice sobre user_id (despues de la migracion)
                try:
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id, updated_at)")
                except:
                    pass
                conn.commit()
                conn.close()
        except Exception as exc:
            logger.error("init_db falló: %s", exc)
            self._try_recover()

    def get_session(self, session_id: str) -> dict | None:
        """Devuelve un dict con la sesión o None si no existe.

        El campo ``history`` se parsea de JSON a lista.
        ``context`` se parsea de JSON a dict.
        """
        try:
            with self._lock:
                conn = self._connect()
                row = conn.execute(
                    "SELECT * FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                conn.close()
                if row is None:
                    return None
                result = dict(row)
                result["history"] = json.loads(result.get("history", "[]"))
                result["context"] = json.loads(result.get("context", "{}"))
                return result
        except Exception as exc:
            logger.error("get_session(%s) falló: %s", session_id, exc)
            self._try_recover()
            return None

    def save_session(
        self, session_id: str, history: list, context: dict | None = None,
        user_id: str | None = None
    ) -> None:
        """Crea o actualiza una sesión (upsert)."""
        try:
            with self._lock:
                conn = self._connect()
                existing = conn.execute(
                    "SELECT 1 FROM sessions WHERE id = ?", (session_id,)
                ).fetchone()
                history_json = json.dumps(history, ensure_ascii=False)
                context_json = json.dumps(context or {}, ensure_ascii=False)
                if existing:
                    conn.execute(
                        """UPDATE sessions
                           SET history = ?, context = ?, updated_at = datetime('now')
                           WHERE id = ?""",
                        (history_json, context_json, session_id),
                    )
                else:
                    conn.execute(
                        """INSERT INTO sessions (id, history, context, user_id)
                           VALUES (?, ?, ?, ?)""",
                        (session_id, history_json, context_json, user_id or ""),
                    )
                conn.commit()
                conn.close()
        except Exception as exc:
            logger.error("save_session(%s) falló: %s", session_id, exc)
            self._try_recover()

    def add_interaction(
        self,
        session_id: str,
        role: str,
        content: str,
        intent_id: str | None = None,
        latency_ms: int | None = None,
    ) -> None:
        """Registra una interacción (turno) en la sesión."""
        try:
            with self._lock:
                conn = self._connect()
                conn.execute(
                    """INSERT INTO interactions (session_id, role, content, intent_id, latency_ms)
                       VALUES (?, ?, ?, ?, ?)""",
                    (session_id, role, content, intent_id, latency_ms),
                )
                conn.commit()
                conn.close()
        except Exception as exc:
            logger.error(
                "add_interaction(session=%s, role=%s) falló: %s",
                session_id,
                role,
                exc,
            )
            self._try_recover()

    def get_recent_interactions(
        self, session_id: str, limit: int = 20
    ) -> list[dict]:
        """Devuelve las últimas N interacciones de una sesión."""
        try:
            with self._lock:
                conn = self._connect()
                rows = conn.execute(
                    """SELECT * FROM interactions
                       WHERE session_id = ?
                       ORDER BY created_at DESC
                       LIMIT ?""",
                    (session_id, limit),
                ).fetchall()
                conn.close()
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.error(
                "get_recent_interactions(%s) falló: %s", session_id, exc
            )
            self._try_recover()
            return []

    def get_user_interactions(self, user_id: str, limit: int = 20) -> list[dict]:
        """Devuelve las últimas interacciones de todas las sesiones de un usuario."""
        try:
            with self._lock:
                conn = self._connect()
                # Buscar sesiones de este usuario
                session_ids = conn.execute(
                    "SELECT id FROM sessions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 10",
                    (user_id,),
                ).fetchall()
                if not session_ids:
                    return []
                ids = [s["id"] for s in session_ids]
                placeholders = ",".join("?" * len(ids))
                rows = conn.execute(
                    f"""SELECT role, content FROM interactions
                       WHERE session_id IN ({placeholders})
                       ORDER BY created_at ASC
                       LIMIT ?""",
                    (*ids, limit),
                ).fetchall()
                conn.close()
                return [dict(r) for r in rows]
        except Exception as exc:
            logger.error("get_user_interactions(%s) falló: %s", user_id, exc)
            return []

    def delete_session(self, session_id: str) -> None:
        """Elimina una sesión y todas sus interacciones."""
        try:
            with self._lock:
                conn = self._connect()
                conn.execute("PRAGMA foreign_keys=ON")
                conn.execute(
                    "DELETE FROM interactions WHERE session_id = ?",
                    (session_id,),
                )
                conn.execute(
                    "DELETE FROM sessions WHERE id = ?", (session_id,)
                )
                conn.commit()
                conn.close()
        except Exception as exc:
            logger.error(
                "delete_session(%s) falló: %s", session_id, exc
            )
            self._try_recover()

    def cleanup_old_sessions(self, days: int = 30) -> int:
        """Borra sesiones más viejas que N días. Retorna cuántas eliminó."""
        try:
            with self._lock:
                conn = self._connect()
                cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
                old = conn.execute(
                    "SELECT id FROM sessions WHERE updated_at < ?",
                    (cutoff,),
                ).fetchall()
                for row in old:
                    sid = row["id"]
                    conn.execute(
                        "DELETE FROM interactions WHERE session_id = ?",
                        (sid,),
                    )
                deleted = conn.execute(
                    "DELETE FROM sessions WHERE updated_at < ?", (cutoff,)
                ).rowcount
                conn.commit()
                conn.close()
                if deleted:
                    logger.info(
                        "cleanup: eliminadas %s sesiones antiguas", deleted
                    )
                return deleted
        except Exception as exc:
            logger.error("cleanup_old_sessions falló: %s", exc)
            self._try_recover()
            return 0

    def load_and_format_history(
        self, session_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Carga el historial reciente y lo devuelve como lista de turnos
        lista para inyectar en el contexto LLM.

        Cada turno tiene la forma ``{"role": ..., "content": ...}``.
        """
        session = self.get_session(session_id)
        if session is None:
            return []
        history: list = session.get("history", [])
        if limit and len(history) > limit:
            history = history[-limit:]
        interactions = self.get_recent_interactions(session_id, limit=limit)
        for ix in reversed(interactions):
            history.append(
                {
                    "role": ix.get("role", "user"),
                    "content": ix.get("content", ""),
                }
            )
            if limit and len(history) > limit:
                history = history[-limit:]
        return history


# ── Wrappers async ──────────────────────────────────────────────────────────

get_session_async = _run_sync(SessionDB.get_session)
save_session_async = _run_sync(SessionDB.save_session)
add_interaction_async = _run_sync(SessionDB.add_interaction)
get_recent_interactions_async = _run_sync(SessionDB.get_recent_interactions)
delete_session_async = _run_sync(SessionDB.delete_session)
cleanup_old_sessions_async = _run_sync(SessionDB.cleanup_old_sessions)
load_and_format_history_async = _run_sync(SessionDB.load_and_format_history)
