"""CRM Unified API — FastAPI service for leads, interactions, calls, deals."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

DB_PATH = Path(__file__).parent.parent.parent / "ops" / "state" / "crm.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="SDC CRM", version="1.0.0")

# ── Database ──────────────────────────────────────────────────────────────

@contextmanager
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def init_db():
    schema = (Path(__file__).parent / "schema.sql").read_text()
    with get_db() as conn:
        conn.executescript(schema)

init_db()

# ── Models ────────────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    source: str = "manual"
    lead_type: str = "cold"
    tags: list[str] = []
    notes: Optional[str] = None

class InteractionCreate(BaseModel):
    contact_id: int
    channel: str
    direction: str = "inbound"
    content: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    sentiment: Optional[str] = None
    agent: Optional[str] = None
    raw_data: Optional[dict] = None

class CallCreate(BaseModel):
    contact_id: int
    direction: str = "inbound"
    duration_seconds: Optional[float] = None
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    sentiment: Optional[str] = None
    outcome: Optional[str] = None
    agent: Optional[str] = None
    started_at: Optional[str] = None
    ended_at: Optional[str] = None

class DealCreate(BaseModel):
    contact_id: int
    title: str
    value: float = 0.0
    currency: str = "USD"
    stage: str = "prospecting"
    probability: float = 0.0
    expected_close: Optional[str] = None
    notes: Optional[str] = None

# ── Contacts ──────────────────────────────────────────────────────────────

@app.get("/api/contacts")
def list_contacts(
    lead_type: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    with get_db() as conn:
        where, params = [], []
        if lead_type:
            where.append("lead_type = ?")
            params.append(lead_type)
        if source:
            where.append("source = ?")
            params.append(source)
        if search:
            where.append("(name LIKE ? OR phone LIKE ? OR company LIKE ?)")
            params.extend([f"%{search}%"] * 3)
        clause = " WHERE " + " AND ".join(where) if where else ""
        rows = conn.execute(
            f"SELECT * FROM contacts{clause} ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset]
        ).fetchall()
        total = conn.execute(f"SELECT COUNT(*) FROM contacts{clause}", params).fetchone()[0]
        return {"contacts": [dict(r) for r in rows], "total": total}

@app.post("/api/contacts")
def create_contact(c: ContactCreate):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO contacts (name, phone, email, company, role, source, lead_type, tags, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (c.name, c.phone, c.email, c.company, c.role, c.source, c.lead_type, json.dumps(c.tags), c.notes)
        )
        contact_id = cur.lastrowid
        conn.execute(
            "INSERT INTO activity_log (contact_id, action, description) VALUES (?, 'created', ?)",
            (contact_id, f"Contact {c.name} created from {c.source}")
        )
        return {"id": contact_id, "status": "created"}

@app.get("/api/contacts/{contact_id}")
def get_contact(contact_id: int):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM contacts WHERE id = ?", (contact_id,)).fetchone()
        if not row:
            raise HTTPException(404, "Contact not found")
        contact = dict(row)
        # Get interactions
        interactions = conn.execute(
            "SELECT * FROM interactions WHERE contact_id = ? ORDER BY created_at DESC LIMIT 50",
            (contact_id,)
        ).fetchall()
        contact["interactions"] = [dict(i) for i in interactions]
        # Get calls
        calls = conn.execute(
            "SELECT * FROM calls WHERE contact_id = ? ORDER BY created_at DESC LIMIT 20",
            (contact_id,)
        ).fetchall()
        contact["calls"] = [dict(c) for c in calls]
        # Get deals
        deals = conn.execute(
            "SELECT * FROM deals WHERE contact_id = ? ORDER BY updated_at DESC",
            (contact_id,)
        ).fetchall()
        contact["deals"] = [dict(d) for d in deals]
        # Get activity
        activity = conn.execute(
            "SELECT * FROM activity_log WHERE contact_id = ? ORDER BY created_at DESC LIMIT 30",
            (contact_id,)
        ).fetchall()
        contact["activity"] = [dict(a) for a in activity]
        return contact

@app.put("/api/contacts/{contact_id}")
def update_contact(contact_id: int, c: ContactCreate):
    with get_db() as conn:
        conn.execute(
            """UPDATE contacts SET name=?, phone=?, email=?, company=?, role=?, source=?,
               lead_type=?, tags=?, notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?""",
            (c.name, c.phone, c.email, c.company, c.role, c.source, c.lead_type, json.dumps(c.tags), c.notes, contact_id)
        )
        return {"status": "updated"}

# ── Interactions ──────────────────────────────────────────────────────────

@app.get("/api/interactions")
def list_interactions(contact_id: Optional[int] = None, channel: Optional[str] = None, limit: int = 50):
    with get_db() as conn:
        where, params = [], []
        if contact_id:
            where.append("contact_id = ?")
            params.append(contact_id)
        if channel:
            where.append("channel = ?")
            params.append(channel)
        clause = " WHERE " + " AND ".join(where) if where else ""
        rows = conn.execute(
            f"SELECT i.*, c.name as contact_name FROM interactions i LEFT JOIN contacts c ON i.contact_id = c.id{clause} ORDER BY i.created_at DESC LIMIT ?",
            params + [limit]
        ).fetchall()
        return {"interactions": [dict(r) for r in rows]}

@app.post("/api/interactions")
def create_interaction(i: InteractionCreate):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO interactions (contact_id, channel, direction, content, media_type, media_url, duration_seconds, sentiment, agent, raw_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (i.contact_id, i.channel, i.direction, i.content, i.media_type, i.media_url,
             i.duration_seconds, i.sentiment, i.agent, json.dumps(i.raw_data) if i.raw_data else None)
        )
        conn.execute(
            "INSERT INTO activity_log (contact_id, action, description) VALUES (?, 'interacted', ?)",
            (i.contact_id, f"{i.channel} {i.direction}: {(i.content or '')[:100]}")
        )
        return {"id": cur.lastrowid, "status": "created"}

# ── Calls ─────────────────────────────────────────────────────────────────

@app.get("/api/calls")
def list_calls(contact_id: Optional[int] = None, limit: int = 20):
    with get_db() as conn:
        if contact_id:
            rows = conn.execute(
                "SELECT cl.*, c.name as contact_name FROM calls cl LEFT JOIN contacts c ON cl.contact_id = c.id WHERE cl.contact_id = ? ORDER BY cl.created_at DESC LIMIT ?",
                (contact_id, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT cl.*, c.name as contact_name FROM calls cl LEFT JOIN contacts c ON cl.contact_id = c.id ORDER BY cl.created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return {"calls": [dict(r) for r in rows]}

@app.post("/api/calls")
def create_call(c: CallCreate):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO calls (contact_id, direction, duration_seconds, recording_url, transcript, summary, sentiment, outcome, agent, started_at, ended_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (c.contact_id, c.direction, c.duration_seconds, c.recording_url, c.transcript,
             c.summary, c.sentiment, c.outcome, c.agent, c.started_at, c.ended_at)
        )
        conn.execute(
            "INSERT INTO activity_log (contact_id, action, description) VALUES (?, 'called', ?)",
            (c.contact_id, f"Call {c.direction} ({c.duration_seconds or 0}s) - {c.outcome or 'unknown'}")
        )
        return {"id": cur.lastrowid, "status": "created"}

# ── Deals ─────────────────────────────────────────────────────────────────

@app.get("/api/deals")
def list_deals(stage: Optional[str] = None, contact_id: Optional[int] = None):
    with get_db() as conn:
        where, params = [], []
        if stage:
            where.append("stage = ?")
            params.append(stage)
        if contact_id:
            where.append("contact_id = ?")
            params.append(contact_id)
        clause = " WHERE " + " AND ".join(where) if where else ""
        rows = conn.execute(
            f"SELECT d.*, c.name as contact_name FROM deals d LEFT JOIN contacts c ON d.contact_id = c.id{clause} ORDER BY d.updated_at DESC",
            params
        ).fetchall()
        return {"deals": [dict(r) for r in rows]}

@app.post("/api/deals")
def create_deal(d: DealCreate):
    with get_db() as conn:
        cur = conn.execute(
            """INSERT INTO deals (contact_id, title, value, currency, stage, probability, expected_close, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (d.contact_id, d.title, d.value, d.currency, d.stage, d.probability, d.expected_close, d.notes)
        )
        conn.execute(
            "INSERT INTO activity_log (contact_id, deal_id, action, description) VALUES (?, ?, 'created', ?)",
            (d.contact_id, cur.lastrowid, f"Deal '{d.title}' created (${d.value})")
        )
        return {"id": cur.lastrowid, "status": "created"}

@app.put("/api/deals/{deal_id}/stage")
def update_deal_stage(deal_id: int, stage: str):
    with get_db() as conn:
        deal = conn.execute("SELECT * FROM deals WHERE id = ?", (deal_id,)).fetchone()
        if not deal:
            raise HTTPException(404, "Deal not found")
        old_stage = deal["stage"]
        conn.execute("UPDATE deals SET stage=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (stage, deal_id))
        conn.execute(
            "INSERT INTO activity_log (contact_id, deal_id, action, description) VALUES (?, ?, 'deal_stage_changed', ?)",
            (deal["contact_id"], deal_id, f"Stage: {old_stage} → {stage}")
        )
        return {"status": "updated", "from": old_stage, "to": stage}

# ── Dashboard ─────────────────────────────────────────────────────────────

@app.get("/")
def dashboard():
    return FileResponse(Path(__file__).parent / "dashboard.html")

# ── Stats ─────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats():
    with get_db() as conn:
        return {
            "contacts": conn.execute("SELECT COUNT(*) FROM contacts").fetchone()[0],
            "hot_leads": conn.execute("SELECT COUNT(*) FROM contacts WHERE lead_type='hot'").fetchone()[0],
            "warm_leads": conn.execute("SELECT COUNT(*) FROM contacts WHERE lead_type='warm'").fetchone()[0],
            "cold_leads": conn.execute("SELECT COUNT(*) FROM contacts WHERE lead_type='cold'").fetchone()[0],
            "interactions": conn.execute("SELECT COUNT(*) FROM interactions").fetchone()[0],
            "calls": conn.execute("SELECT COUNT(*) FROM calls").fetchone()[0],
            "deals": conn.execute("SELECT COUNT(*) FROM deals").fetchone()[0],
            "pipeline_value": conn.execute("SELECT COALESCE(SUM(value), 0) FROM deals WHERE stage NOT IN ('closed_won','closed_lost')").fetchone()[0],
            "deals_won": conn.execute("SELECT COUNT(*) FROM deals WHERE stage='closed_won'").fetchone()[0],
        }

# ── Import from existing sources ──────────────────────────────────────────

@app.post("/api/import/whatsapp-leads")
def import_whatsapp_leads():
    """Import leads from existing state/whatsapp/leads.jsonl"""
    leads_file = Path(__file__).parent.parent.parent / "state" / "whatsapp" / "leads.jsonl"
    if not leads_file.exists():
        return {"imported": 0, "error": "leads.jsonl not found"}
    imported = 0
    with get_db() as conn:
        for line in leads_file.read_text().strip().split("\n"):
            if not line.strip():
                continue
            try:
                lead = json.loads(line)
                phone = lead.get("phone", "")
                name = lead.get("name", lead.get("contact_name", "Unknown"))
                # Check if already exists
                existing = conn.execute("SELECT id FROM contacts WHERE phone = ?", (phone,)).fetchone()
                if existing:
                    continue
                cur = conn.execute(
                    """INSERT INTO contacts (name, phone, source, lead_type, lead_score, tags, notes)
                       VALUES (?, ?, 'whatsapp', ?, ?, ?, ?)""",
                    (name, phone, lead.get("classification", "cold").lower(),
                     lead.get("score", 0), json.dumps(lead.get("tags", [])),
                     lead.get("message", "")[:500])
                )
                imported += 1
            except (json.JSONDecodeError, KeyError):
                continue
    return {"imported": imported}

@app.post("/api/import/telegram-interactions")
def import_telegram_interactions():
    """Import interactions from engram memory"""
    imported = 0
    with get_db() as conn:
        # Check if we have any contacts to link to
        contacts = conn.execute("SELECT id, phone FROM contacts").fetchall()
        if not contacts:
            return {"imported": 0, "note": "No contacts to link interactions to"}
        # Import from engram search results would go here
        return {"imported": imported, "note": "Telegram import requires engram MCP bridge"}
