"""Voice Assistant API — MCP + Memory + Calendar + Email."""
import os
import sys
import yaml
import sqlite3
import logging
import time
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import httpx
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-assistant")

app = FastAPI(title="Aztrotech Voice")

# Paths
BASE_DIR = os.path.dirname(__file__)
SKILLS_DIR = os.path.join(BASE_DIR, "..", "..", "skills", "calendar")
sys.path.insert(0, SKILLS_DIR)

CONFIG_PATH = os.path.join(BASE_DIR, "..", "..", "config.yaml")
ENGRAM_PATH = os.getenv("ENGRAM_PATH", "/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/engram_aztrotech.db")

# Config
try:
    with open(CONFIG_PATH) as f:
        CONFIG = yaml.safe_load(f)
except:
    CONFIG = {}

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY") or CONFIG.get("openrouter", {}).get("api_key", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN", "")
NOTIF_OWNER_CHAT_ID = os.getenv("NOTIF_OWNER_CHAT_ID", "5738935134")
DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
HERMES_URL = os.getenv("HERMES_URL", "http://localhost:8643")
CESAR_PHONE = "5216621072254"


# ===== MEMORY SYSTEM =====
def load_engram_memory(query: str = "", limit: int = 5) -> str:
    """Load relevant memories from engram database."""
    try:
        conn = sqlite3.connect(ENGRAM_PATH)
        cursor = conn.cursor()
        
        if query:
            # Search by tags or key
            cursor.execute("""
                SELECT key, value, importance FROM memories 
                WHERE key LIKE ? OR tags LIKE ? OR value LIKE ?
                ORDER BY importance DESC, access_count DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        else:
            # Get most important memories
            cursor.execute("""
                SELECT key, value, importance FROM memories 
                ORDER BY importance DESC, access_count DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return ""
        
        memories = []
        for key, value, importance in rows:
            # Truncate long values
            short_value = value[:300] + "..." if len(value) > 300 else value
            memories.append(f"[{key}] {short_value}")
        
        return "\n".join(memories)
    except Exception as e:
        logger.error(f"Engram error: {e}")
        return ""


def load_user_memory(user_id: str) -> str:
    """Load user-specific memory from Postgres."""
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return ""
        
        pool = loop.run_until_complete(asyncpg.create_pool(DB_URL, min_size=1, max_size=2))
        
        # Get user identity
        identity = loop.run_until_complete(pool.fetchrow(
            "SELECT display_name, platform, created_at FROM user_identities WHERE internal_id = $1",
            user_id
        ))
        
        if not identity:
            return ""
        
        # Get recent conversations
        convos = loop.run_until_complete(pool.fetch("""
            SELECT c.lead_type, c.lead_confidence, c.language, c.started_at
            FROM conversations c
            WHERE c.internal_user_id = $1
            ORDER BY c.started_at DESC LIMIT 3
        """, user_id))
        
        result = f"Usuario: {identity['display_name']} ({identity['platform']})\n"
        for c in convos:
            result += f"  Conversación {c['started_at'].strftime('%d/%m')}: lead={c['lead_type']}, idioma={c['language']}\n"
        
        return result
    except Exception as e:
        logger.error(f"User memory error: {e}")
        return ""


# ===== SYSTEM PROMPT =====
def build_system_prompt(memory_context: str = "", user_context: str = "") -> str:
    """Build system prompt with memory context."""
    base = """Eres el asistente de Aztrotech. Hablas por teléfono. Sé breve y directo.

REGLAS:
- Máximo 2 oraciones
- NUNCA digas asteriscos, paréntesis, signos
- NUNCA des precios, solo "César te da cotización"
- NUNCA menciones Sonora Digital Corp
- Responde en español
- Si dicen nombre, confirma
- Si dicen "sí" o "confirmo", confirma la cita

Servicios:
- Empleado Digital: agente IA 24/7 WhatsApp, Instagram, Facebook
- Automatizaciones: flujos automáticos
- Software a Medida: CRM, ERP, apps

Links:
- WhatsApp: wa.me/5216621072254
- Instagram: instagram.com/cesarholguin
- LinkedIn: linkedin.com/in/cesarholguin
- Web: aztrotech.mx"""
    
    if memory_context:
        base += f"\n\nMEMORIA DEL SISTEMA:\n{memory_context}"
    
    if user_context:
        base += f"\n\nCONTEXTO DEL USUARIO:\n{user_context}"
    
    return base


# ===== MODELS =====
class ChatRequest(BaseModel):
    messages: list
    model: Optional[str] = "deepseek/deepseek-chat"
    user_id: Optional[str] = None
    memory_query: Optional[str] = None

class ScheduleRequest(BaseModel):
    name: str
    email: Optional[str] = ""
    phone: Optional[str] = ""
    date: str
    time: str


# ===== ROUTES =====
@app.post("/api/chat")
async def chat(req: ChatRequest):
    if not OPENROUTER_KEY:
        return {"error": "API key not configured"}
    
    # Load memory
    memory_context = load_engram_memory(req.memory_query or "", 5)
    user_context = load_user_memory(req.user_id) if req.user_id else ""
    
    # Build messages
    system_prompt = build_system_prompt(memory_context, user_context)
    messages = [{"role": "system", "content": system_prompt}]
    
    for m in req.messages[-8:]:
        if m.get("role") != "system":
            messages.append(m)
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://aztrotech.mx",
        "X-Title": "Aztrotech Voice",
    }
    
    t0 = time.time()
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(OPENROUTER_URL, json={
            "model": req.model, "messages": messages, "max_tokens": 80, "temperature": 0.4
        }, headers=headers)
        logger.info(f"LLM: {time.time()-t0:.1f}s")
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"Error {resp.status_code}"}


@app.get("/api/availability")
async def get_availability(date: Optional[str] = None):
    try:
        from calendar_skill import get_available_slots
        slots = get_available_slots(date)
        return {"slots": slots, "date": date or (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")}
    except Exception as e:
        target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now() + timedelta(days=1)
        slots = []
        for h in range(8, 18):
            for m in [0, 30]:
                t = target.replace(hour=h, minute=m)
                slots.append({"time": t.strftime("%I:%M %p"), "period": "morning" if h < 12 else "afternoon"})
        return {"slots": slots, "date": target.strftime("%Y-%m-%d"), "fallback": True}


@app.post("/api/schedule")
async def schedule(req: ScheduleRequest):
    logger.info(f"Booking: {req.name} - {req.date} {req.time} - {req.email}")
    
    try:
        from calendar_skill import create_event
        cal_result = create_event(req.date, req.time, req.name, req.phone)
        logger.info(f"Calendar: {cal_result}")
    except Exception as e:
        logger.error(f"Calendar error: {e}")
    
    try:
        from email_service import send_booking_confirmation, send_welcome_email
        if req.email:
            send_booking_confirmation(req.email, req.name, req.date, req.time, req.phone)
            send_welcome_email(req.email, req.name)
    except Exception as e:
        logger.error(f"Email error: {e}")
    
    if NOTIF_BOT_TOKEN:
        try:
            msg = f"NUEVA CITA\n\nNombre: {req.name}\nTelefono: {req.phone}\nEmail: {req.email}\nHora: {req.time}\nFecha: {req.date}"
            async with httpx.AsyncClient(timeout=10) as client:
                await client.post(f"https://api.telegram.org/bot{NOTIF_BOT_TOKEN}/sendMessage",
                    json={"chat_id": NOTIF_OWNER_CHAT_ID, "text": msg})
        except Exception as e:
            logger.error(f"Telegram notify error: {e}")
    
    return {"status": "ok", "message": f"Cita confirmada para {req.name} el {req.date} a las {req.time}"}


@app.get("/api/memory")
async def get_memory(query: Optional[str] = None):
    """Get memory from engram."""
    memory = load_engram_memory(query, 10)
    return {"memory": memory, "query": query}


@app.get("/api/users")
async def get_users():
    """Get user identities."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        users = await pool.fetch("""
            SELECT internal_id, display_name, platform, created_at 
            FROM user_identities ORDER BY created_at DESC LIMIT 20
        """)
        await pool.close()
        return {"users": [dict(u) for u in users]}
    except Exception as e:
        return {"users": [], "error": str(e)}


@app.get("/api/hermes")
async def hermes_status():
    """Check Hermes MCP status."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{HERMES_URL}/api/health")
            return resp.json()
    except:
        return {"status": "offline"}


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "api_key": bool(OPENROUTER_KEY),
        "engram": os.path.exists(ENGRAM_PATH),
        "hermes": HERMES_URL,
        "db": DB_URL
    }


DIST_DIR = os.path.join(BASE_DIR, "dist")

@app.get("/{full_path:path}")
async def serve(full_path: str):
    file_path = os.path.join(DIST_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
