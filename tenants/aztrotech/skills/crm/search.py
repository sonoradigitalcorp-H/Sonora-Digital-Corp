from typing import Optional

from .models import Contact
from .store import CRMStore


class CRMSearch:
    def __init__(self, store: CRMStore):
        self.store = store

    def by_name(self, name: str, exact: bool = False) -> list[Contact]:
        if exact:
            rows = self.store.conn.execute(
                "SELECT * FROM contacts WHERE name = ? ORDER BY updated_at DESC", (name,)
            ).fetchall()
        else:
            rows = self.store.conn.execute(
                "SELECT * FROM contacts WHERE name LIKE ? ORDER BY updated_at DESC",
                (f"%{name}%",)
            ).fetchall()
        return [self.store._row_to_contact(r) for r in rows]

    def by_phone(self, phone: str) -> list[Contact]:
        rows = self.store.conn.execute(
            "SELECT * FROM contacts WHERE phone LIKE ? ORDER BY updated_at DESC",
            (f"%{phone}%",)
        ).fetchall()
        return [self.store._row_to_contact(r) for r in rows]

    def by_company(self, company: str) -> list[Contact]:
        rows = self.store.conn.execute(
            "SELECT * FROM contacts WHERE company LIKE ? ORDER BY updated_at DESC",
            (f"%{company}%",)
        ).fetchall()
        return [self.store._row_to_contact(r) for r in rows]

    def by_tag(self, tag: str) -> list[Contact]:
        rows = self.store.conn.execute(
            "SELECT * FROM contacts WHERE tags LIKE ? ORDER BY updated_at DESC",
            (f"%{tag}%",)
        ).fetchall()
        return [self.store._row_to_contact(r) for r in rows]

    def search(self, query: str, limit: int = 20) -> list[Contact]:
        q = f"%{query}%"
        rows = self.store.conn.execute("""
            SELECT * FROM contacts
            WHERE name LIKE ? OR phone LIKE ? OR company LIKE ? OR email LIKE ? OR tags LIKE ? OR notes LIKE ?
            ORDER BY
                CASE
                    WHEN name LIKE ? THEN 0
                    WHEN phone LIKE ? THEN 1
                    WHEN company LIKE ? THEN 2
                    ELSE 3
                END,
                updated_at DESC
            LIMIT ?
        """, (q, q, q, q, q, q, q, q, q, limit)).fetchall()
        return [self.store._row_to_contact(r) for r in rows]
