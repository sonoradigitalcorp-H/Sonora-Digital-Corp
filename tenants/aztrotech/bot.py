import os
import sys
import json
import logging
import tempfile
import asyncio
import re
from pathlib import Path
from datetime import datetime, time, timezone, timedelta

import yaml
import httpx
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE.parent.parent))
from tenants.aztrotech.skills.calendar.availability import get_available_slots, get_available_days
from tenants.aztrotech.skills.calendar.store import create_booking
from tenants.aztrotech.skills.calendar.models import Booking, BookingSlot
from tenants.aztrotech.skills.voice.tts import TTS
from tenants.aztrotech.skills.whatsapp.wacli_mcp import send_whatsapp
from tenants.aztrotech.skills.rag.retriever import retrieve
from tenants.aztrotech.skills.storage.minio_store import save_photo, save_audio, save_document, save_file

MEXICO_TZ = timezone(timedelta(hours=-6))
_tts = None

LOG_DIR = BASE / "bot"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

PERSONA_FILE = BASE / "prompt-cesar.md"
ENV_FILE = BASE / "bot" / ".env"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(str(LOG_FILE), encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("aztrotech-bot")

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

def load_prompt() -> str:
    if not PERSONA_FILE.exists():
        return ""
    with open(PERSONA_FILE) as f:
        return f.read()

def load_secret(key: str) -> str:
    return os.environ.get(key, "")

load_env()
TOKEN = load_secret("TELEGRAM_BOT_TOKEN")
LLM_API_KEY = load_secret("LLM_API_KEY")

PERSONA = load_prompt()

def build_system_prompt() -> str:
    now = datetime.now(MEXICO_TZ)
    weekday = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"][now.weekday()]
    date_str = f"Hoy es {weekday} {now.day}/{now.month}/{now.year}."
    return f"{PERSONA}\n\n{date_str}\n\nIMPORTANTE: Responde como César, en primera persona, como si estuvieras platicando. Máximo 4 oraciones. No digas que eres IA ni bot."

history: dict[int, list[dict]] = {}
day_names = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]

# ─── Anti-leak: patrón de cosas que NUNCA debe responder el bot ───────────
LEAK_PATTERNS = [
    r"---BOOKING---.*?---END---",
    r"INSTRUCCIONES IMPORTANTES",
    r"FLUJO DE CONVERSACIÓN",
    r"Paso \d+\.",
    r"NUNCA\s+(revele|hables|digas|menciones)",
    r"NO incluyas",
    r"Sé natural",
    r"Puedes saltarte",
    r"como una asesora real",
    r"Siempre dirige hacia",
    r"CONTEXTO ACTUAL",
    r"Horarios disponibles",
    r"HERRAMIENTAS",
    r"---BOOKING---",
    r"El sistema procesará",
]

def sanitize_reply(text: str) -> str:
    for pat in LEAK_PATTERNS:
        text = re.sub(pat, "", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    text = re.sub(r'\s{2,}', ' ', text)
    return text


# ─── Detección de intención de agendar (en código, NO en prompt) ───────────
BOOKING_KEYWORDS = [
    r"\bagendar?\b", r"\breservar\b", r"\bcita\b", r"\breunión\b",
    r"\bhorario\b", r"\bdisponible\b", r"\bcuándo\b", r"\bpuedo\b.*\bver\b.*\bcesar\b",
    r"\bconocer\b.*\bcesar\b", r"\bhablar\b.*\bcesar\b", r"\bschedule\b",
]

def detect_booking_intent(text: str) -> bool:
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in BOOKING_KEYWORDS)


async def tts_safe(text: str) -> bytes | None:
    global _tts
    if _tts is None:
        _tts = TTS()
    try:
        return await _tts.synthesize(text)
    except Exception as e:
        logger.error(f"TTS error: {e}")
        return None

async def send_voice(update: Update, text: str):
    audio_bytes = await tts_safe(text)
    if audio_bytes:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name
        with open(tmp_path, "rb") as f:
            await update.message.reply_voice(voice=InputFile(f, filename="msg.mp3"))
        os.unlink(tmp_path)
    else:
        await update.message.reply_text(text)

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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    slots_context = get_slots_context()
    rag_context = await retrieve(text)
    system = build_system_prompt()
    enriched = f"{system}\n\nHorarios disponibles:\n{slots_context}"
    if rag_context:
        enriched += f"\n\nInformación de contexto:\n{rag_context}"

    if user_id not in history:
        history[user_id] = [
            {"role": "system", "content": enriched},
        ]

    history[user_id].append({"role": "user", "content": text})

    reply = await ask_llm(history[user_id])
    if not reply:
        reply = "Perdón, ¿puedes repetirlo?"
        await update.message.reply_text(reply)
        return

    reply = sanitize_reply(reply)
    if not reply:
        reply = "Claro, cuéntame más sobre lo que necesitas."

    wants_booking = detect_booking_intent(text) or detect_booking_intent(reply)

    await send_voice(update, reply)

    if wants_booking:
        try:
            fresh_slots = get_slots_context()
            await update.message.reply_text(
                f"Estos son los horarios disponibles con César:\n\n{fresh_slots}\n\n"
                "¿Cuál te queda mejor? Confírmame día y hora y lo agendo."
            )
            cesar_phone = load_secret("CESAR_PHONE") or "526621072254"
            await send_whatsapp(
                cesar_phone,
                f"🔔 *Nuevo lead desde Telegram:*\n\n{text}\n\n— Mystic AI"
            )
            logger.info(f"WhatsApp notification sent to César for user {user_id}")
        except Exception as e:
            logger.error(f"Booking/notify error: {e}")

    history[user_id].append({"role": "assistant", "content": reply})
    history[user_id] = history[user_id][-10:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    slots_context = get_slots_context()
    rag_context = await retrieve("presentación de AztroTech servicios")
    system = build_system_prompt()
    enriched = f"{system}\n\nHorarios disponibles:\n{slots_context}"
    if rag_context:
        enriched += f"\n\nInformación de contexto:\n{rag_context}"
    history[user_id] = [
        {"role": "system", "content": enriched},
    ]
    msg = (
        "Qué onda, soy César Holguín de AztroTech. "
        "Aquí estoy al tiro para lo que necesites. Cuéntame, ¿qué traes?"
    )
    history[user_id].append({"role": "assistant", "content": msg})
    await send_voice(update, msg)


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    msg = update.message
    chat_id = msg.chat_id

    try:
        if msg.photo:
            file_id = msg.photo[-1].file_id
            file = await context.bot.get_file(file_id)
            photo_bytes = await file.download_as_bytearray()
            result = await save_photo(bytes(photo_bytes))
            logger.info(f"Photo saved from {chat_id}: {result['url']}")
            await msg.reply_text("📸 Foto guardada.")
            return

        if msg.voice or msg.audio:
            voice = msg.voice or msg.audio
            file = await context.bot.get_file(voice.file_id)
            audio_bytes = await file.download_as_bytearray()
            result = await save_audio(bytes(audio_bytes))
            logger.info(f"Audio saved from {chat_id}: {result['url']}")
            await msg.reply_text("🎤 Audio guardado.")
            return

        if msg.document:
            doc = msg.document
            file = await context.bot.get_file(doc.file_id)
            doc_bytes = await file.download_as_bytearray()
            result = await save_document(bytes(doc_bytes), doc.file_name or "document")
            logger.info(f"Document saved from {chat_id}: {result['url']}")
            await msg.reply_text(f"📄 {doc.file_name} guardado.")
            return

        if msg.video or msg.video_note:
            vid = msg.video or msg.video_note
            file = await context.bot.get_file(vid.file_id)
            vid_bytes = await file.download_as_bytearray()
            result = await save_file(bytes(vid_bytes), "video.mp4", "videos")
            logger.info(f"Video saved from {chat_id}: {result['url']}")
            await msg.reply_text("🎬 Video guardado.")
            return
    except Exception as e:
        logger.error(f"Media save error: {e}")
        await msg.reply_text("No pude guardar el archivo, intenta de nuevo.")


async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.VOICE | filters.AUDIO | filters.Document.ALL | filters.VIDEO | filters.VIDEO_NOTE,
        handle_media,
    ))
    logger.info("AztroTech Mystic Bot starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    try:
        await asyncio.Event().wait()
    except:
        pass

if __name__ == "__main__":
    asyncio.run(main())
