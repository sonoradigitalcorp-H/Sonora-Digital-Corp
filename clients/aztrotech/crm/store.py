import json
import sqlite3
import time
from pathlib import Path
from typing import Optional

from .models import Contact, ContactID

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "crm.db"


class CRMStore:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._init_schema()
        return self._conn

    def _init_schema(self):
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS contacts (
                crm_id TEXT PRIMARY KEY,
                name TEXT NOT NULL DEFAULT '',
                phone TEXT NOT NULL DEFAULT '',
                company TEXT NOT NULL DEFAULT '',
                email TEXT NOT NULL DEFAULT '',
                instagram TEXT NOT NULL DEFAULT '',
                source TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '',
                notes TEXT NOT NULL DEFAULT '',
                first_contact REAL NOT NULL DEFAULT 0,
                last_contact REAL NOT NULL DEFAULT 0,
                created_at REAL NOT NULL DEFAULT 0,
                updated_at REAL NOT NULL DEFAULT 0,
                metadata TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_contacts_name ON contacts(name);
            CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
            CREATE INDEX IF NOT EXISTS idx_contacts_company ON contacts(company);
            CREATE INDEX IF NOT EXISTS idx_contacts_tags ON contacts(tags);
        """)
        self._conn.commit()

    def upsert(self, contact: Contact) -> Contact:
        contact.updated_at = time.time()
        data = contact.to_dict()
        md = data.pop("metadata", {}) or {}
        data["metadata"] = json.dumps(md) if isinstance(md, dict) else str(md)
        self.conn.execute("""
            INSERT INTO contacts (crm_id, name, phone, company, email, instagram,
                source, tags, notes, first_contact, last_contact, created_at, updated_at, metadata)
            VALUES (:crm_id, :name, :phone, :company, :email, :instagram,
                :source, :tags, :notes, :first_contact, :last_contact, :created_at, :updated_at, :metadata)
            ON CONFLICT(crm_id) DO UPDATE SET
                name=excluded.name, phone=excluded.phone, company=excluded.company,
                email=excluded.email, instagram=excluded.instagram,
                source=excluded.source, tags=excluded.tags, notes=excluded.notes,
                first_contact=excluded.first_contact, last_contact=excluded.last_contact,
                updated_at=excluded.updated_at, metadata=excluded.metadata
        """, data)
        self.conn.commit()
        return contact

    def get(self, crm_id: str) -> Optional[Contact]:
        row = self.conn.execute("SELECT * FROM contacts WHERE crm_id = ?", (crm_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_contact(row)

    def delete(self, crm_id: str) -> bool:
        cur = self.conn.execute("DELETE FROM contacts WHERE crm_id = ?", (crm_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def list_all(self, limit: int = 100, offset: int = 0) -> list[Contact]:
        rows = self.conn.execute(
            "SELECT * FROM contacts ORDER BY updated_at DESC LIMIT ? OFFSET ?", (limit, offset)
        ).fetchall()
        return [self._row_to_contact(r) for r in rows]

    def count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM contacts").fetchone()
        return row["cnt"]

    def _row_to_contact(self, row: sqlite3.Row) -> Contact:
        data = dict(row)
        return Contact.from_dict(data)

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None
