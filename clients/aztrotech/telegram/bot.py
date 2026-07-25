import os
import sys
import json
import logging
import tempfile
import asyncio
import re
from pathlib import Path
from datetime import date, datetime, time

import yaml
import httpx
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE.parent.parent))
from clients.aztrotech.calendar.availability import get_available_slots, get_available_days
from clients.aztrotech.calendar.store import create_booking
from clients.aztrotech.calendar.models import Booking, BookingSlot
from clients.aztrotech.voice.tts import TTS

_tts = TTS(engine="edge")

LOG_DIR = BASE / "telegram"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "bot.log"

SECRETS_FILE = BASE / "ai" / "secrets.yaml"
PERSONA_FILE = BASE / "ai" / "persona.md"
ENV_FILE = BASE / "telegram" / ".env"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(str(LOG_FILE), encoding="utf-8"), logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("aztrotech-bot")

def load_secret(key: str) -> str:
    if not SECRETS_FILE.exists():
        return ""
    with open(SECRETS_FILE) as f:
        secrets = yaml.safe_load(f)
    return secrets.get(key, "")

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

def load_persona() -> str:
    if not PERSONA_FILE.exists():
        return ""
    with open(PERSONA_FILE) as f:
        return f.read()

load_env()
TOKEN = load_secret("telegram_bot_token")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
PERSONA = load_persona()

history: dict[int, list[dict]] = {}

SYSTEM = PERSONA + """

ERES MYSTIC — asesora de ventas de AztroTech. 

Hablas como una asesora real en llamada: cálida, natural, profesional. NO eres un chatbot de menús. 

FLUJO DE CONVERSACIÓN (natural, no obligatorio):
1. Saluda y pregúntale cómo está
2. Preséntate: "Soy Mystic, la asistente de AztroTech"
3. Pregunta si está listo para dar el salto al cambio
4. Si muestra interés, pide su nombre
5. Pide WhatsApp
6. Pide Instagram (opcional)
7. Muestra horarios disponibles de César
8. Agenda cuando elijan
9. Da WhatsApp de César: wa.me/526621072254 e Instagram: @cesarholguin1
10. Redirige a aztrotech.mx

HERRAMIENTAS — cuando el cliente quiera agendar, responde con:
---BOOKING---
date: YYYY-MM-DD
time: HH:MM
name: nombre
whatsapp: número
instagram: @usuario
---END---

El sistema procesará eso automáticamente y agendará la cita.

INSTRUCCIONES IMPORTANTES:
- NO incluyas ---BOOKING--- si el cliente no ha confirmado
- Sé natural, no suenes a guion
- Puedes saltarte pasos si el cliente ya los dio
- Si el cliente no quiere dar Instagram, no insistas
- Siempre dirige hacia agendar sin ser agresiva
- Tus respuestas deben ser de 1 a 3 oraciones, como en una llamada real
"""
day_names = ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]

async def send_voice(update: Update, text: str):
    try:
        audio_bytes = await _tts.synthesize(text)
        if audio_bytes:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                f.write(audio_bytes)
                tmp_path = f.name
            with open(tmp_path, "rb") as f:
                await update.message.reply_voice(voice=InputFile(f, filename="msg.mp3"))
            os.unlink(tmp_path)
            return
    except Exception as e:
        logger.error(f"TTS error: {e}")
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

async def ask_openrouter(messages: list[dict]) -> str | None:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sonoradigitalcorp.com",
        "X-Title": "AztroTech Mystic",
    }
    payload = {"model": "nvidia/nemotron-3-nano-30b-a3b:free", "messages": messages, "max_tokens": 300}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"]
            logger.warning(f"OpenRouter {r.status_code}: {r.text[:100]}")
    except Exception as e:
        logger.error(f"OpenRouter error: {e}")
    return None

def process_booking(text: str) -> dict | None:
    m = re.search(r"---BOOKING---\n(.*?)---END---", text, re.DOTALL)
    if not m:
        return None
    try:
        data = {}
        for line in m.group(1).strip().split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip()] = v.strip()
        return data
    except:
        return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    now = datetime.utcnow()
    slots_context = get_slots_context()
    date_context = f"Hoy es {day_names[now.weekday()]} {now.day}/{now.month}."

    if user_id not in history:
        history[user_id] = [
            {"role": "system", "content": SYSTEM + f"\n\nCONTEXTO ACTUAL:\n{date_context}\nHorarios disponibles:\n{slots_context}"},
        ]

    history[user_id].append({"role": "user", "content": text})
    history[user_id] = history[user_id][-15:]

    reply = await ask_openrouter(history[user_id])
    if not reply:
        reply = "Perdón, ¿puedes repetirlo? No te escuché bien."

    booking_data = process_booking(reply)
    if booking_data:
        try:
            slot = BookingSlot(
                date=date.fromisoformat(booking_data["date"]),
                start_time=datetime.strptime(booking_data["time"], "%H:%M").time(),
                end_time=datetime.strptime(booking_data["time"], "%H:%M").time().replace(
                    hour=datetime.strptime(booking_data["time"], "%H:%M").time().hour,
                    minute=datetime.strptime(booking_data["time"], "%H:%M").time().minute + 15,
                ),
            )
            booking = create_booking(Booking(
                id="", created_at=datetime.utcnow(),
                prospect_name=booking_data.get("name", "Cliente"),
                prospect_email="",
                prospect_phone=booking_data.get("whatsapp", ""),
                company="",
                slot=slot,
                notes=f"IG: {booking_data.get('instagram', '')}",
            ))
            clean_reply = re.sub(r"---BOOKING---.*?---END---", "", reply, flags=re.DOTALL).strip()
            if clean_reply:
                await send_voice(update, clean_reply)

            wa_link = f"https://wa.me/526621072254?text=Hola%20César%2C%20soy%20{booking_data.get('name', 'cliente').replace(' ', '%20')}%2C%20agendé%20mi%20diagnóstico"
            await update.message.reply_text(
                f"✅ Cita agendada {slot.date} a las {booking_data['time']}\n\n"
                f"📞 César: {wa_link}\n"
                f"📸 @cesarholguin1\n"
                f"🌐 aztrotech.mx"
            )
        except Exception as e:
            logger.error(f"Booking processing error: {e}")
            clean_reply = re.sub(r"---BOOKING---.*?---END---", "", reply, flags=re.DOTALL).strip()
            if clean_reply:
                await send_voice(update, clean_reply)
    else:
        await send_voice(update, reply)

    history[user_id].append({"role": "assistant", "content": reply})
    history[user_id] = [history[user_id][0]] + history[user_id][-12:]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    history[user_id] = [
        {"role": "system", "content": SYSTEM + f"\n\nCONTEXTO ACTUAL:\nHoy es {day_names[datetime.utcnow().weekday()]} {datetime.utcnow().day}/{datetime.utcnow().month}.\nHorarios disponibles:\n{get_slots_context()}"},
    ]
    msg = (
        "Hola, soy Mystic, la asistente de AztroTech. "
        "Es un gusto poder saludarte el día de hoy. "
        "Cuéntame, ¿ya estás listo para dar el salto al cambio? "
        "César estará encantado de darte detalles especializados."
    )
    history[user_id].append({"role": "assistant", "content": msg})
    await send_voice(update, msg)

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
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
