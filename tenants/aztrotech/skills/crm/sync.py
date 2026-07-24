import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .models import Contact, gen_id
from .store import CRMStore

BASE = Path(__file__).resolve().parent.parent.parent.parent
EVENTS_FILE = BASE / "state" / "events" / "events.jsonl"
ENGRAM_DIR = BASE / "state" / "engram"


class CRMSync:
    def __init__(self, store: CRMStore, tenant: str = "aztrotech"):
        self.store = store
        self.tenant = tenant

    def _log_event(self, event_type: str, contact: Contact, detail: str = ""):
        EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "event": event_type,
            "id": gen_id("EVT"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tenant": self.tenant,
            "payload": {
                "crm_id": contact.crm_id,
                "name": contact.name,
                "phone": contact.phone,
                "company": contact.company,
                "detail": detail,
            },
            "source": {"agent": "crm-sync", "module": "clients.aztrotech.crm"},
        }
        with open(EVENTS_FILE, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _sync_engram(self, contact: Contact):
        engram_file = ENGRAM_DIR / f"engram_{self.tenant}.db"
        engram_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            import sqlite3
            conn = sqlite3.connect(str(engram_file))
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    layer INTEGER DEFAULT 3,
                    importance INTEGER DEFAULT 2,
                    tags TEXT DEFAULT '',
                    user_id TEXT DEFAULT '',
                    access_count INTEGER DEFAULT 0,
                    created_at REAL NOT NULL,
                    accessed_at REAL NOT NULL
                )
            """)
            now = time.time()
            conn.execute("""
                INSERT OR REPLACE INTO memories (key, value, layer, importance, tags, user_id, created_at, accessed_at)
                VALUES (?, ?, 3, 2, ?, ?, ?, ?)
            """, (
                f"contact:{contact.crm_id}",
                json.dumps(contact.to_dict(), ensure_ascii=False),
                f"crm,client,{contact.tags}",
                contact.phone,
                now, now,
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[crm-sync] Engram error: {e}")

    def _sync_qdrant(self, contact: Contact):
        try:
            import httpx
            vector = [0.0] * 384
            payload = {
                "name": contact.name,
                "phone": contact.phone,
                "company": contact.company,
                "email": contact.email,
                "tags": contact.tags,
                "notes": contact.notes[:200],
                "crm_id": contact.crm_id,
                "tenant": self.tenant,
            }
            collection = f"kb_{self.tenant}"
            point = {
                "id": hash(contact.crm_id) % (2**63),
                "vector": vector,
                "payload": payload,
            }
            with httpx.Client(timeout=5) as client:
                client.put(
                    f"http://localhost:6333/collections/{collection}/points",
                    json={"points": [point]},
                )
        except Exception as e:
            print(f"[crm-sync] Qdrant error: {e}")

    def _sync_neo4j(self, contact: Contact):
        try:
            import httpx
            query = (
                "MERGE (c:Contact {crm_id: $crm_id}) "
                "ON CREATE SET c.name = $name, c.phone = $phone, c.company = $company, "
                "c.email = $email, c.source = $source, c.created_at = $created "
                "ON MATCH SET c.name = $name, c.phone = $phone, c.company = $company, c.updated_at = $updated "
                "WITH c "
                "MERGE (t:Tenant {name: $tenant}) "
                "MERGE (c)-[:BELONGS_TO]->(t)"
            )
            params = {
                "crm_id": contact.crm_id,
                "name": contact.name,
                "phone": contact.phone,
                "company": contact.company,
                "email": contact.email,
                "source": contact.source,
                "tenant": self.tenant,
                "created": datetime.fromtimestamp(contact.created_at, tz=timezone.utc).isoformat(),
                "updated": datetime.fromtimestamp(contact.updated_at, tz=timezone.utc).isoformat(),
            }
            with httpx.Client(timeout=5) as client:
                client.post(
                    "http://localhost:7687/db/neo4j/tx/commit",
                    json={"statements": [{"statement": query, "parameters": params}]},
                    auth=("neo4j", "sdc2026"),
                )
        except Exception as e:
            print(f"[crm-sync] Neo4j error: {e}")

    def sync_all(self, contact: Contact):
        self._log_event("crm:contact:upserted", contact)
        self._sync_engram(contact)
        self._sync_qdrant(contact)
        self._sync_neo4j(contact)
        return contact

    def sync_existing(self, crm_id: str):
        contact = self.store.get(crm_id)
        if contact:
            self.sync_all(contact)
