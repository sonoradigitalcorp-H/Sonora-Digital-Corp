"""Voice Assistant API — MCP + Memory + Calendar + WhatsApp."""
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
from typing import Optional
import httpx
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-assistant")

app = FastAPI(title="Aztrotech Voice")

BASE_DIR = os.path.dirname(__file__)
SKILLS_DIR = os.path.join(BASE_DIR, "..", "..", "skills", "calendar")
sys.path.insert(0, SKILLS_DIR)

CONFIG_PATH = os.path.join(BASE_DIR, "..", "..", "config.yaml")
ENGRAM_PATH = os.getenv("ENGRAM_PATH", "/home/mystic/Documentos/Sonora Digital Corp/sonora-digital-corp/ops/state/engram_aztrotech.db")

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
CESAR_PHONE = "5216621072254"
CESAR_WA_LINK = "https://wa.me/5216621072254"


# ===== MEMORY =====
def load_engram_memory(query: str = "", limit: int = 5) -> str:
    try:
        conn = sqlite3.connect(ENGRAM_PATH)
        cursor = conn.cursor()
        if query:
            cursor.execute("""
                SELECT key, value, importance FROM memories 
                WHERE key LIKE ? OR tags LIKE ? OR value LIKE ?
                ORDER BY importance DESC LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit))
        else:
            cursor.execute("SELECT key, value, importance FROM memories ORDER BY importance DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        if not rows:
            return ""
        return "\n".join([f"[{k}] {v[:200]}..." if len(v) > 200 else f"[{k}] {v}" for k, v, i in rows])
    except Exception as e:
        logger.error(f"Engram error: {e}")
        return ""


def load_user_memory(user_id: str) -> str:
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            return ""
        pool = loop.run_until_complete(asyncpg.create_pool(DB_URL, min_size=1, max_size=2))
        identity = loop.run_until_complete(pool.fetchrow(
            "SELECT display_name, platform FROM user_identities WHERE internal_id = $1", user_id
        ))
        if not identity:
            return ""
        return f"Usuario: {identity['display_name']} ({identity['platform']})"
    except:
        return ""


# ===== SYSTEM PROMPT =====
def build_system_prompt(memory: str = "", user_ctx: str = "") -> str:
    prompt = """Eres el asistente de Aztrotech. Guias al usuario para agendar una llamada con César Holguín.

FLUJO OBLIGATORIO:
1. Saluda: "Hola, soy el asistente de César Holguín de Aztrotech"
2. Pregunta: "¿Te gustaría agendar una llamada gratuita con César para conocer cómo automatizar tu negocio?"
3. Si dice sí, pregunta: "¿Mañana o tarde te queda mejor?"
4. Muestra horarios disponibles
5. Pide nombre: "¿Cómo te llamas?"
6. Pide email: "¿Tu email para enviarte la confirmación?"
7. Confirma: "¿Confirmas para las [hora]?"
8. Al confirmar, di: "Listo, tu llamada está confirmada. Te envío un mensaje de WhatsApp con los detalles"

REGLAS:
- Sé breve, máximo 2 oraciones
- NUNCA digas asteriscos, paréntesis, signos
- NUNCA des precios, solo "César te da cotización"
- NUNCA menciones Sonora Digital Corp
- Si preguntan por servicios, di "César te explica todo en la llamada"
- Responde en español
- SIEMPRE guía hacia agendar

Servicios: Empleado Digital, Automatizaciones, Software a Medida
WhatsApp de César: wa.me/5216621072254"""

    if memory:
        prompt += f"\n\nMEMORIA:\n{memory}"
    if user_ctx:
        prompt += f"\n\nUSUARIO:\n{user_ctx}"
    return prompt


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
    
    memory = load_engram_memory(req.memory_query or "", 5)
    user_ctx = load_user_memory(req.user_id) if req.user_id else ""
    
    messages = [{"role": "system", "content": build_system_prompt(memory, user_ctx)}]
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
            "model": req.model, "messages": messages, "max_tokens": 100, "temperature": 0.4
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
    except:
        target = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now() + timedelta(days=1)
        slots = []
        for h in range(8, 18):
            for m in [0, 30]:
                t = target.replace(hour=h, minute=m)
                slots.append({"time": t.strftime("%I:%M %p"), "period": "morning" if h < 12 else "afternoon"})
        return {"slots": slots, "date": target.strftime("%Y-%m-%d"), "fallback": True}


@app.post("/api/schedule")
async def schedule(req: ScheduleRequest):
    logger.info(f"Booking: {req.name} - {req.date} - {req.time} - {req.email}")
    
    # Create calendar event
    try:
        from calendar_skill import create_event
        create_event(req.date, req.time, req.name, req.phone)
    except Exception as e:
        logger.error(f"Calendar error: {e}")
    
    # Send WhatsApp to César
    try:
        wa_msg = (
            f"📅 *NUEVA CITA AGENDADA*\n\n"
            f"👤 *{req.name}*\n"
            f"📱 {req.phone or 'Sin teléfono'}\n"
            f"📧 {req.email or 'Sin email'}\n"
            f"🕐 *{req.time}*\n"
            f"📅 *{req.date}*\n\n"
            f"📲 Contacta: {CESAR_WA_LINK}"
        )
        async with httpx.AsyncClient(timeout=10) as client:
            # Notify César via Telegram bot
            if NOTIF_BOT_TOKEN:
                await client.post(
                    f"https://api.telegram.org/bot{NOTIF_BOT_TOKEN}/sendMessage",
                    json={"chat_id": NOTIF_OWNER_CHAT_ID, "text": wa_msg, "parse_mode": "Markdown"}
                )
    except Exception as e:
        logger.error(f"Notify error: {e}")
    
    return {"status": "ok", "message": f"Cita confirmada para {req.name}"}


@app.get("/api/memory")
async def get_memory(query: Optional[str] = None):
    return {"memory": load_engram_memory(query, 10), "query": query}


@app.get("/api/users")
async def get_users():
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        users = await pool.fetch("SELECT internal_id, display_name, platform, created_at FROM user_identities ORDER BY created_at DESC LIMIT 20")
        await pool.close()
        return {"users": [dict(u) for u in users]}
    except Exception as e:
        return {"users": [], "error": str(e)}


@app.get("/api/health")
async def health():
    return {"status": "ok", "api_key": bool(OPENROUTER_KEY), "engram": os.path.exists(ENGRAM_PATH)}


DIST_DIR = os.path.join(BASE_DIR, "dist")

@app.get("/{full_path:path}")
async def serve(full_path: str):
    file_path = os.path.join(DIST_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(DIST_DIR, "index.html"))
