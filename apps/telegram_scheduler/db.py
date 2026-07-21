"""Database layer for Telegram Scheduler — SQLite CRUD."""

import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

DB_DIR = Path(__file__).parent
DB_PATH = DB_DIR / "telegram_scheduler.db"

_lock = threading.Lock()


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock:
        conn = _get_conn()
        try:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL UNIQUE,
                    telegram_id TEXT NULL,
                    whatsapp_jid TEXT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );

                CREATE TABLE IF NOT EXISTS mensajes_programados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    contenido TEXT NOT NULL,
                    programado_para TEXT NOT NULL,
                    estado TEXT NOT NULL DEFAULT 'pendiente',
                    canal TEXT NOT NULL DEFAULT 'auto',
                    enviado_en TEXT NULL,
                    error_msg TEXT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                );

                CREATE TABLE IF NOT EXISTS historial (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id INTEGER NOT NULL,
                    contenido TEXT NOT NULL,
                    canal TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    error_msg TEXT NULL,
                    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
                );
            """)
            conn.commit()
        finally:
            conn.close()


def add_cliente(nombre: str, telegram_id: Optional[str] = None, whatsapp_jid: Optional[str] = None) -> int:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO clientes (nombre, telegram_id, whatsapp_jid) VALUES (?, ?, ?)",
                (nombre.strip(), telegram_id, whatsapp_jid)
            )
            conn.commit()
            return cur.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Ya existe un cliente llamado '{nombre}'")
        finally:
            conn.close()


def get_cliente(nombre: str) -> Optional[dict]:
    with _lock:
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT id, nombre, telegram_id, whatsapp_jid, created_at FROM clientes WHERE nombre = ?",
                (nombre.strip(),)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def get_cliente_by_id(id: int) -> Optional[dict]:
    with _lock:
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT id, nombre, telegram_id, whatsapp_jid, created_at FROM clientes WHERE id = ?",
                (id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def list_clientes() -> list[dict]:
    with _lock:
        conn = _get_conn()
        try:
            rows = conn.execute(
                "SELECT id, nombre, telegram_id, whatsapp_jid, created_at FROM clientes ORDER BY nombre"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def delete_cliente(nombre: str) -> bool:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.execute("DELETE FROM clientes WHERE nombre = ?", (nombre.strip(),))
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


def add_mensaje(cliente_id: int, contenido: str, programado_para: str, canal: str = "auto") -> int:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "INSERT INTO mensajes_programados (cliente_id, contenido, programado_para, canal) VALUES (?, ?, ?, ?)",
                (cliente_id, contenido, programado_para, canal)
            )
            conn.commit()
            return cur.lastrowid
        finally:
            conn.close()


def get_mensaje(id: int) -> Optional[dict]:
    with _lock:
        conn = _get_conn()
        try:
            row = conn.execute(
                "SELECT * FROM mensajes_programados WHERE id = ?",
                (id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()


def get_pendientes() -> list[dict]:
    with _lock:
        conn = _get_conn()
        try:
            rows = conn.execute("""
                SELECT m.id, m.cliente_id, m.contenido, m.programado_para, m.canal,
                       c.nombre, c.telegram_id, c.whatsapp_jid
                FROM mensajes_programados m
                JOIN clientes c ON m.cliente_id = c.id
                WHERE m.estado = 'pendiente'
                ORDER BY m.programado_para
            """).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()


def update_mensaje_estado(id: int, estado: str, error_msg: Optional[str] = None, enviado_en: Optional[str] = None) -> None:
    with _lock:
        conn = _get_conn()
        try:
            if estado == "enviado" and enviado_en:
                conn.execute(
                    "UPDATE mensajes_programados SET estado = ?, enviado_en = ?, error_msg = ? WHERE id = ?",
                    (estado, enviado_en, error_msg, id)
                )
            else:
                conn.execute(
                    "UPDATE mensajes_programados SET estado = ?, error_msg = ?, enviado_en = COALESCE(enviado_en, enviado_en) WHERE id = ?",
                    (estado, error_msg, id)
                )
            conn.commit()
        finally:
            conn.close()


def cancel_mensaje(id: int) -> bool:
    with _lock:
        conn = _get_conn()
        try:
            cur = conn.execute(
                "UPDATE mensajes_programados SET estado = 'cancelado' WHERE id = ? AND estado = 'pendiente'",
                (id,)
            )
            conn.commit()
            return cur.rowcount > 0
        finally:
            conn.close()


def add_historial(cliente_id: int, contenido: str, canal: str, estado: str, sent_at: Optional[str] = None, error_msg: Optional[str] = None) -> None:
    with _lock:
        conn = _get_conn()
        try:
            conn.execute(
                "INSERT INTO historial (cliente_id, contenido, canal, estado, sent_at, error_msg) VALUES (?, ?, ?, ?, ?, ?)",
                (cliente_id, contenido, canal, estado, sent_at or datetime.now().isoformat(), error_msg)
            )
            conn.commit()
        finally:
            conn.close()


def get_historial(cliente_id: int, limit: int = 10) -> list[dict]:
    with _lock:
        conn = _get_conn()
        try:
            rows = conn.execute(
                "SELECT id, cliente_id, contenido, canal, estado, sent_at, error_msg FROM historial WHERE cliente_id = ? ORDER BY sent_at DESC LIMIT ?",
                (cliente_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
