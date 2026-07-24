import os
import sys
import json
import logging
import asyncio
import re
from pathlib import Path
from datetime import datetime, timezone, timedelta

import httpx

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE.parent.parent))

from tenants.aztrotech.skills.rag.retriever import retrieve
from tenants.aztrotech.skills.whatsapp.wacli_mcp import send_whatsapp, get_messages, check_status
from tenants.aztrotech.skills.calendar.availability import get_available_slots, get_available_days

LOG_DIR = BASE / "bot"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "whatsapp_bot.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(str(LOG_FILE), encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("aztrotech-whatsapp")

ENV_FILE = BASE / "bot" / ".env"
PERSONA_FILE = BASE / "prompt-cesar.md"

MEXICO_TZ = timezone(timedelta(hours=-6))

def load_env():
    if not ENV_FILE.exists():
        return
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def load_secret(key: str) -> str:
    return os.environ.get(key, "")

def load_prompt() -> str:
    if not PERSONA_FILE.exists():
        return ""
    with open(PERSONA_FILE) as f:
        return f.read()

load_env()
LLM_API_KEY = load_secret("LLM_API_KEY")
CESAR_JID = load_secret("CESAR_WHATSAPP_JID") or "5216621072254@s.whatsapp.net"
CESAR_PHONE = load_secret("CESAR_PHONE") or "526621072254"
POLL_INTERVAL = int(load_secret("POLL_INTERVAL") or "10")

PERSONA = load_prompt()
CESAR_PROMPT = PERSONA
PROSPECT_PROMPT = PERSONA

day_names = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]

LEAK_PATTERNS = [
    r"---BOOKING---.*?---END---", r"INSTRUCCIONES IMPORTANTES",
    r"FLUJO DE CONVERSACIÓN", r"Paso \d+\.", r"NUNCA\s+(revele|hables|digas|menciones)",
    r"NO incluyas", r"Sé natural", r"Puedes saltarte", r"como una asesora real",
    r"Siempre dirige hacia", r"CONTEXTO ACTUAL", r"Horarios disponibles",
    r"HERRAMIENTAS", r"---BOOKING---", r"El sistema procesará",
]

def sanitize_reply(text: str) -> str:
    for pat in LEAK_PATTERNS:
        text = re.sub(pat, "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    text = re.sub(r'\s{2,}', ' ', text)
    return text

BOOKING_KEYWORDS = [
    r"\bagendar?\b", r"\breservar\b", r"\bcita\b", r"\breunión\b",
    r"\bhorario\b", r"\bdisponible\b", r"\bcuándo\b", r"\bpuedo\b.*\bver\b.*\bcesar\b",
    r"\bconocer\b.*\bcesar\b", r"\bhablar\b.*\bcesar\b", r"\bschedule\b",
]

def detect_booking_intent(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in BOOKING_KEYWORDS)

def build_system_prompt(is_cesar: bool) -> str:
    now = datetime.now(MEXICO_TZ)
    weekday = day_names[now.weekday()]
    date_str = f"Hoy es {weekday} {now.day}/{now.month}/{now.year}."
    base = CESAR_PROMPT if is_cesar else PROSPECT_PROMPT
    return f"{base}\n\n{date_str}\n\nIMPORTANTE: Responde SOLO con el mensaje para el usuario. No incluyas etiquetas, marcadores, formatos, ni explicaciones internas."

def get_slots_context() -> str:
    days = get_available_days(days_ahead=7)
    lines = []
    for d in days[:5]:
        slots = get_available_slots(d)
        if slots:
            name = day_names[d.weekday()]
            times = ", ".join(s.start_time.strftime("%H:%M") for s in slots[:3])
            extra = f" y {len(slots)-3} más" if len(slots) > 3 else ""
            lines.append(f"{name} {d.day}/{d.month}: {times}{extra}")
    return "\n".join(lines) if lines else "No hay horarios esta semana"

async def ask_llm(messages: list[dict], retry: int = 1) -> str | None:
    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-v4-flash",
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.7,
    }
    for attempt in range(retry + 1):
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                r = await client.post("https://opencode.ai/zen/go/v1/chat/completions", headers=headers, json=payload)
                if r.status_code == 200:
                    return r.json()["choices"][0]["message"]["content"]
                logger.warning(f"LLM {r.status_code}: {r.text[:200]}")
                if attempt < retry:
                    await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"LLM error (attempt {attempt+1}): {e}")
            if attempt < retry:
                await asyncio.sleep(2)
    return None

def get_jid_from_message(msg: dict) -> str:
    chat = msg.get("chat", {}) if isinstance(msg.get("chat"), dict) else {}
    return chat.get("jid", "") or msg.get("from", "")

def get_text_from_message(msg: dict) -> str:
    content = msg.get("content", {}) if isinstance(msg.get("content"), dict) else {}
    return content.get("text", "") or msg.get("text", "")

async def process_message(msg: dict):
    msg_id = msg.get("id", "")
    jid = get_jid_from_message(msg)
    text = get_text_from_message(msg)

    if not text or not jid:
        return

    is_cesar = jid == CESAR_JID
    logger.info(f"{'CÉSAR' if is_cesar else 'PROSPECT'} [{jid[:15]}]: {text[:60]}")

    rag_context = await retrieve(text)
    slots_context = get_slots_context()
    system = build_system_prompt(is_cesar)
    enriched = f"{system}\n\nHorarios disponibles:\n{slots_context}"
    if rag_context:
        enriched += f"\n\nInformación de contexto:\n{rag_context}"

    messages = [
        {"role": "system", "content": enriched},
        {"role": "user", "content": text},
    ]

    reply = await ask_llm(messages)
    if not reply:
        reply = "Perdón, ¿puedes repetirlo?" if not is_cesar else "Disculpa, no pude procesar eso. ¿Puedes repetirlo?"

    reply = sanitize_reply(reply)

    if is_cesar:
        await send_whatsapp(CESAR_PHONE, reply)
    else:
        phone = jid.replace("@s.whatsapp.net", "").replace("521", "52")
        await send_whatsapp(phone, reply)
        if detect_booking_intent(text) or detect_booking_intent(reply):
            await send_whatsapp(
                CESAR_PHONE,
                f"🔔 *Nuevo lead desde WhatsApp:*\n\n{text}\n\n— Mystic AI"
            )

    logger.info(f"Responded to {jid[:15]}")

async def poll_loop():
    logger.info("WhatsApp assistant starting...")
    status = await check_status()
    if not status.get("authenticated"):
        logger.error(f"wacli not authenticated: {status.get('error')}")
        return

    logger.info(f"wacli authenticated as {status.get('phone', '?')}")
    logger.info(f"César JID: {CESAR_JID}")
    logger.info(f"Polling every {POLL_INTERVAL}s")

    processed = set()

    while True:
        try:
            msgs = await get_messages(limit=10)
            for msg in msgs:
                msg_id = msg.get("id", "")
                if not msg_id or msg_id in processed:
                    continue
                jid = get_jid_from_message(msg)
                if not jid:
                    continue
                if jid != CESAR_JID and not jid.endswith("@s.whatsapp.net"):
                    continue
                processed.add(msg_id)
                await process_message(msg)
        except Exception as e:
            logger.error(f"Poll error: {e}")

        await asyncio.sleep(POLL_INTERVAL)

async def main():
    await poll_loop()

if __name__ == "__main__":
    asyncio.run(main())
