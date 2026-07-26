"""
Nathy Conta — Bot de Telegram + Canal Automatizado.

Bot:   @NathyCont_bot (interactivo, AI, audios)
Canal: @NathyConta (automated accounting updates)

CLI:   python3 nathy_bot.py --post "mensaje" (posta al canal)
       python3 nathy_bot.py --audio "texto" (genera audio)
       python3 nathy_bot.py --summary "cliente" (resumen de cliente)
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

# ─── Config ───────────────────────────────────────────────
TOKEN = os.environ.get("NATHY_BOT_TOKEN", "8269193231:AAF70NVpEMsrP_fePAc_qLdNEsJkBIGUy4g")
CHANNEL_ID = os.environ.get("NATHY_CHANNEL_ID", "@NathyConta")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = "opencode-go/deepseek-v4-flash"

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CLIENTES_FILE = DATA_DIR / "clientes.json"
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nathy.bot")

# ─── System Prompt ────────────────────────────────────────
SYSTEM_PROMPT = (
    "Eres Nathy, asistente contable digital mexicana. "
    "Hablas español, eres directa y profesional. "
    "Ayudas con CFDI 4.0, SAT, RESICO, nóminas, CONTPAQi, conciliación bancaria.\n\n"
    "Cuando un cliente pida un resumen, genera un texto claro y conciso "
    "que incluya: ingresos del periodo, impuestos calculados, fechas importantes. "
    "Si pide audio, el texto se convertirá a voz automáticamente."
)

# ─── Helpers ──────────────────────────────────────────────

def _log_event(event: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {"event": event, "timestamp": datetime.now(timezone.utc).isoformat(), "payload": payload}
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _load_clientes() -> dict:
    if CLIENTES_FILE.exists():
        return json.loads(CLIENTES_FILE.read_text())
    return {}


def _save_clientes(data: dict) -> None:
    CLIENTES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


async def _ask_llm(messages: list) -> str:
    if not OPENROUTER_KEY:
        return "⚠️ No tengo conexión con mi cerebro (falta OPENROUTER_API_KEY)"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
                json={"model": LLM_MODEL, "messages": messages, "max_tokens": 800, "temperature": 0.7},
            )
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.exception("LLM error")
        return f"⚠️ Error: {e}"


def _text_to_audio(text: str) -> str | None:
    """Genera audio con edge-tts, devuelve path del .ogg."""
    try:
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, mode="wb")
        mp3_path = tmp.name
        tmp.close()
        subprocess.run(
            ["edge-tts", "--voice", "es-MX-DaliaNeural", "--text", text, "--write-media", mp3_path],
            capture_output=True, timeout=30,
        )
        ogg_path = mp3_path.replace(".mp3", ".ogg")
        subprocess.run(
            ["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus", "-b:a", "16k", "-ar", "16000", ogg_path],
            capture_output=True, timeout=30,
        )
        os.unlink(mp3_path)
        return ogg_path
    except Exception as e:
        logger.error(f"Audio error: {e}")
        return None


# ─── Bot Handlers ─────────────────────────────────────────

async def start(update: Update, context) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy Nathy, tu asistente contable digital.\n\n"
        "📌 *Comandos:*\n"
        "/resumen — Resumen de tu situación contable\n"
        "/audio — Te lo explico en voz\n"
        "/facturas — Estado de facturación\n"
        "/declaraciones — Próximas declaraciones\n"
        "/redes — Mis redes sociales\n"
        "/contacto — Contactar a Nathy\n\n"
        "¿En qué te ayudo?",
        parse_mode="Markdown",
    )
    _log_event("bot:start", {"user_id": user.id, "username": user.username})


async def resumen_cmd(update: Update, context) -> None:
    user = update.effective_user
    clientes = _load_clientes()
    user_id_str = str(user.id)
    cliente = clientes.get(user_id_str)

    if cliente:
        text = (
            f"📊 *Resumen de {cliente.get('nombre', 'Cliente')}*\n\n"
            f"📅 Última actualización: {cliente.get('ultima_actualizacion', 'N/A')}\n"
            f"💰 Ingresos del mes: ${cliente.get('ingresos_mes', 0):,.2f}\n"
            f"📄 Facturas emitidas: {cliente.get('facturas_emitidas', 0)}\n"
            f"📄 Facturas recibidas: {cliente.get('facturas_recibidas', 0)}\n"
            f"🧾 ISR calculado: ${cliente.get('isr_calculado', 0):,.2f}\n"
            f"🏛 IVA: ${cliente.get('iva', 0):,.2f}\n"
            f"📅 Próxima declaración: {cliente.get('proxima_declaracion', 'N/A')}\n"
        )
        if cliente.get("redes"):
            text += "\n🌐 *Redes Sociales:*\n"
            for red, url in cliente["redes"].items():
                text += f"  • {red}: {url}\n"
    else:
        text = (
            "📊 *Resumen Contable*\n\n"
            "Aún no tengo información registrada para ti. "
            "¿Quieres que prepare un resumen? "
            "Dime tu RFC o nombre de tu negocio y te ayudo."
        )

    await update.message.reply_text(text, parse_mode="Markdown")
    _log_event("bot:resumen", {"user_id": user.id})


async def audio_cmd(update: Update, context) -> None:
    user = update.effective_user
    await update.message.chat.send_action("record_audio")

    clientes = _load_clientes()
    user_id_str = str(user.id)
    cliente = clientes.get(user_id_str)

    if cliente:
        text = (
            f"Hola {cliente.get('nombre', 'Cliente')}, "
            f"aquí está tu resumen contable. "
            f"Tus ingresos del mes son {cliente.get('ingresos_mes', 0):,.0f} pesos. "
            f"Has emitido {cliente.get('facturas_emitidas', 0)} facturas "
            f"y recibido {cliente.get('facturas_recibidas', 0)}. "
            f"Tu ISR calculado es de {cliente.get('isr_calculado', 0):,.0f} pesos. "
            f"Tu próxima declaración es {cliente.get('proxima_declaracion', 'pronto')}. "
            f"Si necesitas más detalles, estoy aquí para ayudarte."
        )
    else:
        text = (
            "Hola, gracias por comunicarte con Nathy Conta. "
            "Aún no tengo tus datos registrados. "
            "Por favor comparte tu RFC o nombre de negocio "
            "para que pueda preparar tu resumen personalizado."
        )

    ogg_path = _text_to_audio(text)
    if ogg_path:
        with open(ogg_path, "rb") as f:
            await update.message.reply_voice(f)
        os.unlink(ogg_path)
    else:
        await update.message.reply_text(text)

    _log_event("bot:audio", {"user_id": user.id})


async def facturas_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "📄 *Facturación*\n\n"
        "Puedo ayudarte con:\n"
        "• Estado de tus CFDI del mes\n"
        "• Facturas pendientes de pago\n"
        "• Complementos de pago\n"
        "• Cancelaciones y sustituciones\n\n"
        "¿Qué necesitas revisar?",
        parse_mode="Markdown",
    )


async def declaraciones_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "📅 *Declaraciones*\n\n"
        "Próximas fechas importantes:\n"
        "• Bimestral RESICO: días 1-17 del mes siguiente\n"
        "• IVA mensual: días 1-17\n"
        "• Declaración anual: abril 2027\n\n"
        "¿Quieres que calcule algo específico?",
        parse_mode="Markdown",
    )


async def redes_cmd(update: Update, context) -> None:
    user = update.effective_user
    clientes = _load_clientes()
    user_id_str = str(user.id)
    cliente = clientes.get(user_id_str)

    if cliente and cliente.get("redes"):
        text = f"🌐 *Redes Sociales de {cliente['nombre']}*\n\n"
        for red, url in cliente["redes"].items():
            text += f"• *{red}*: {url}\n"
        text += "\n¿Quieres que comparta algo en tus redes?"
    else:
        text = (
            "🌐 *Redes Sociales*\n\n"
            "Comparte el enlace de tus redes sociales "
            "y las tendré visibles para ti y tu equipo.\n\n"
            "Ejemplo: Instagram: https://instagram.com/tu_cuenta"
        )

    await update.message.reply_text(text, parse_mode="Markdown")


async def contacto_cmd(update: Update, context) -> None:
    kb = [[InlineKeyboardButton("📱 WhatsApp", url="https://wa.me/5216622681111")]]
    await update.message.reply_text(
        "📞 *Contactar a Nathy*\n\n"
        "Puedes contactarme directamente por WhatsApp:\n"
        "• Consultas rápidas\n"
        "• Envío de facturas\n"
        "• Dudas fiscales\n\n"
        "O responde aquí mismo y te atiendo.",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def handle_message(update: Update, context) -> None:
    user = update.effective_user
    text = update.message.text

    logger.info(f"Msg from {user.id}: {text[:60]}...")
    _log_event("bot:message", {"user_id": user.id, "text": text})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context.user_data.get("history"):
        messages.extend(context.user_data["history"][-20:])
    messages.append({"role": "user", "content": text})

    await update.message.chat.send_action("typing")
    response = await _ask_llm(messages)

    if "history" not in context.user_data:
        context.user_data["history"] = []
    context.user_data["history"].append({"role": "user", "content": text})
    context.user_data["history"].append({"role": "assistant", "content": response})

    await update.message.reply_text(response)
    _log_event("bot:response", {"user_id": user.id, "preview": response[:100]})


async def handle_error(update: Update, context) -> None:
    logger.error(f"Error: {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text("⚠️ Ocurrió un error. Intenta de nuevo.")
    except Exception:
        pass


# ─── Channel & CLI ────────────────────────────────────────

async def post_to_channel(text: str, parse_mode: str = "Markdown") -> bool:
    """Postea al canal de Telegram."""
    app = Application.builder().token(TOKEN).build()
    async with app:
        try:
            await app.bot.send_message(chat_id=CHANNEL_ID, text=text, parse_mode=parse_mode)
            logger.info(f"Posteado al canal: {text[:60]}...")
            return True
        except Exception as e:
            logger.error(f"Error posteando al canal: {e}")
            return False


async def send_audio_to_channel(text: str) -> bool:
    """Genera audio y lo envía al canal."""
    ogg_path = _text_to_audio(text)
    if not ogg_path:
        return False
    app = Application.builder().token(TOKEN).build()
    async with app:
        try:
            with open(ogg_path, "rb") as f:
                await app.bot.send_voice(chat_id=CHANNEL_ID, voice=f)
            os.unlink(ogg_path)
            return True
        except Exception as e:
            logger.error(f"Error enviando audio al canal: {e}")
            return False


def cli():
    """Interfaz CLI para controlar el bot y canal."""
    parser = argparse.ArgumentParser(description="Nathy Conta CLI")
    parser.add_argument("--post", help="Postear mensaje al canal")
    parser.add_argument("--audio", help="Generar y enviar audio al canal")
    parser.add_argument("--summary", help="Generar resumen de un cliente")
    parser.add_argument("--add-cliente", nargs=2, metavar=("USER_ID", "NOMBRE"), help="Agregar cliente")
    parser.add_argument("--add-red", nargs=3, metavar=("USER_ID", "RED", "URL"), help="Agregar red social a cliente")
    parser.add_argument("--update-finanzas", nargs=7, metavar=(
        "USER_ID", "INGRESOS", "FACT_EMIT", "FACT_RECIB", "ISR", "IVA", "PROX_DEC"
    ), help="Actualizar finanzas de cliente")
    parser.add_argument("--list-clientes", action="store_true", help="Listar clientes")

    args = parser.parse_args()

    if args.post:
        asyncio.run(post_to_channel(args.post))
        print("✅ Posteado al canal")

    elif args.audio:
        asyncio.run(send_audio_to_channel(args.audio))
        print("✅ Audio enviado al canal")

    elif args.summary:
        clientes = _load_clientes()
        cid = args.summary
        if cid in clientes:
            c = clientes[cid]
            text = (
                f"📊 Resumen de {c['nombre']}\n"
                f"  Ingresos: ${c.get('ingresos_mes', 0):,.2f}\n"
                f"  Facturas emitidas: {c.get('facturas_emitidas', 0)}\n"
                f"  ISR: ${c.get('isr_calculado', 0):,.2f}\n"
                f"  Próxima decl: {c.get('proxima_declaracion', 'N/A')}\n"
                f"  Redes: {list(c.get('redes', {}).keys())}"
            )
            print(text)
        else:
            print(f"❌ Cliente '{cid}' no encontrado")

    elif args.add_cliente:
        uid, nombre = args.add_cliente
        clientes = _load_clientes()
        clientes[uid] = {"nombre": nombre, "ingresos_mes": 0, "facturas_emitidas": 0,
                         "facturas_recibidas": 0, "isr_calculado": 0, "iva": 0,
                         "proxima_declaracion": "N/A", "redes": {},
                         "ultima_actualizacion": datetime.now().isoformat()[:10]}
        _save_clientes(clientes)
        print(f"✅ Cliente {nombre} (ID: {uid}) agregado")

    elif args.add_red:
        uid, red, url = args.add_red
        clientes = _load_clientes()
        if uid in clientes:
            clientes[uid].setdefault("redes", {})[red] = url
            _save_clientes(clientes)
            print(f"✅ Red {red} agregada a {clientes[uid]['nombre']}")
        else:
            print(f"❌ Cliente '{uid}' no encontrado")

    elif args.update_finanzas:
        uid, ing, fe, fr, isr, iva, prox = args.update_finanzas
        clientes = _load_clientes()
        if uid in clientes:
            clientes[uid].update({"ingresos_mes": float(ing), "facturas_emitidas": int(fe),
                                  "facturas_recibidas": int(fr), "isr_calculado": float(isr),
                                  "iva": float(iva), "proxima_declaracion": prox,
                                  "ultima_actualizacion": datetime.now().isoformat()[:10]})
            _save_clientes(clientes)
            print(f"✅ Finanzas de {clientes[uid]['nombre']} actualizadas")
            # Postear al canal
            asyncio.run(post_to_channel(
                f"📊 *{clientes[uid]['nombre']}* — Finanzas actualizadas\n"
                f"Ingresos: ${float(ing):,.2f} | ISR: ${float(isr):,.2f} | Próxima decl: {prox}"
            ))
        else:
            print(f"❌ Cliente '{uid}' no encontrado")

    elif args.list_clientes:
        clientes = _load_clientes()
        if clientes:
            for uid, c in clientes.items():
                print(f"  {uid}: {c['nombre']} — ${c.get('ingresos_mes', 0):,.2f} — {c.get('proxima_declaracion', 'N/A')}")
        else:
            print("  No hay clientes registrados")


# ─── Main ─────────────────────────────────────────────────

def run_bot():
    """Ejecuta el bot con event loop propio (evita problemas de señal)."""
    import asyncio

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("resumen", resumen_cmd))
    app.add_handler(CommandHandler("audio", audio_cmd))
    app.add_handler(CommandHandler("facturas", facturas_cmd))
    app.add_handler(CommandHandler("declaraciones", declaraciones_cmd))
    app.add_handler(CommandHandler("redes", redes_cmd))
    app.add_handler(CommandHandler("contacto", contacto_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(handle_error)

    logger.info("Nathy Bot @NathyCont_bot — polling started")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(app.initialize())
    loop.run_until_complete(app.start())
    if app.updater:
        loop.run_until_complete(app.updater.start_polling())
    logger.info("Bot running forever...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(app.updater.stop() if app.updater else None)
        loop.run_until_complete(app.stop())
        loop.run_until_complete(app.shutdown())


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli()
    else:
        run_bot()
