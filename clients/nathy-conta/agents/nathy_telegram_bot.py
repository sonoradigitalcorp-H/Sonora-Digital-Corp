"""
Nathy Telegram Bot — Conectado a Hermes/OpenClaw.

Habla con Nathy Conta por Telegram con IA.
Usa el mismo backend que el WhatsApp de Luis Daniel.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

TOKEN = os.environ.get("NATHY_BOT_TOKEN", "8269193231:AAF70NVpEMsrP_fePAc_qLdNEsJkBIGUy4g")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
LLM_MODEL = "opencode-go/deepseek-v4-flash"
OC_GATEWAY = "http://127.0.0.1:18789"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("nathy.bot")

SYSTEM_PROMPT = (
    "Eres Nathy, asistente contable digital. "
    "Hablas español mexicano, eres directa, profesional y eficiente. "
    "Ayudas a la contadora con:\n"
    "- Facturación CFDI 4.0 (timbrado, cancelación, complementos)\n"
    "- Declaraciones SAT (bimestrales RESICO, anuales, IVA)\n"
    "- Conciliación bancaria\n"
    "- Nóminas (CFDI, percepciones, deducciones, finiquitos)\n"
    "- CONTPAQi (pólizas, catálogos, balanzas)\n"
    "- RESICO (cálculo ISR progresivo, tope 3.5M)\n"
    "- Organización de archivos XML/PDF\n\n"
    "Tienes clientes en RESICO y regimen de actividades empresariales. "
    "Cuando te pidan algo técnico, lo explicas claro. "
    "Si no sabes algo, lo dices. Sin rodeos. Máximo 3 párrafos."
)

EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"


def _log_event(event: str, payload: dict) -> None:
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(EVENTS_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def _ask_llm(messages: list) -> str:
    if not OPENROUTER_KEY:
        return "⚠️ No tengo conexión con mi cerebro (falta OPENROUTER_API_KEY)"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": LLM_MODEL,
                    "messages": messages,
                    "max_tokens": 800,
                    "temperature": 0.7,
                },
            )
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        logger.exception("LLM error")
        return f"⚠️ Error de conexión: {e}"


async def start(update: Update, context) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"¡Hola {user.first_name}! 👋\n\n"
        "Soy Nathy, tu asistente contable digital.\n"
        "Puedo ayudarte con:\n"
        "📄 Facturación CFDI\n"
        "📊 Declaraciones SAT\n"
        "🏦 Conciliación bancaria\n"
        "👔 Nóminas\n"
        "💰 RESICO\n"
        "📁 Organizar archivos\n\n"
        "¿En qué te ayudo?"
    )
    _log_event("nathy:bot:start", {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
    })


async def help_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "Comandos disponibles:\n"
        "/start — Iniciar conversación\n"
        "/facturar — Ayuda con CFDI\n"
        "/declarar — Declaraciones SAT\n"
        "/conciliar — Conciliación bancaria\n"
        "/nomina — Nóminas\n"
        "/resico — Cálculo RESICO\n"
        "/organizar — Organizar archivos\n"
        "/help — Esta ayuda"
    )


async def handle_message(update: Update, context) -> None:
    user = update.effective_user
    text = update.message.text
    chat_id = update.effective_chat.id

    logger.info(f"Message from {user.id}: {text[:60]}...")

    _log_event("nathy:bot:message", {
        "user_id": user.id,
        "chat_id": chat_id,
        "text": text,
        "username": user.username,
    })

    # Build context from conversation history (last 10 exchanges)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if context.user_data.get("history"):
        for msg in context.user_data["history"][-20:]:
            messages.append(msg)

    messages.append({"role": "user", "content": text})

    await update.message.chat.send_action("typing")
    response = await _ask_llm(messages)

    # Save to history
    if "history" not in context.user_data:
        context.user_data["history"] = []
    context.user_data["history"].append({"role": "user", "content": text})
    context.user_data["history"].append({"role": "assistant", "content": response})

    await update.message.reply_text(response)

    _log_event("nathy:bot:response", {
        "user_id": user.id,
        "response_preview": response[:100],
    })


async def handle_error(update: Update, context) -> None:
    logger.error(f"Update {update} caused error {context.error}")
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Ocurrió un error. Intenta de nuevo."
            )
    except Exception:
        pass


async def cfdi_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "📄 *CFDI — Facturación Electrónica*\n\n"
        "Puedo ayudarte a:\n"
        "• Timbrar facturas de ingreso, pago, nómina\n"
        "• Cancelar CFDI (motivo 02/03/04)\n"
        "• Generar complementos de pago\n"
        "• Validar XML antes de timbrar\n\n"
        "¿Qué necesitas hacer?",
        parse_mode="Markdown",
    )


async def declarar_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "📊 *Declaraciones SAT*\n\n"
        "Puedo ayudarte con:\n"
        "• Declaraciones bimestrales RESICO\n"
        "• Declaración anual\n"
        "• Cálculo de ISR e IVA\n"
        "• Buzón tributario\n"
        "• Recordatorios de fechas clave\n\n"
        "¿Qué declaración necesitas?",
        parse_mode="Markdown",
    )


async def conciliar_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "🏦 *Conciliación Bancaria*\n\n"
        "Puedo ayudarte a:\n"
        "• Cruzar facturas vs movimientos bancarios\n"
        "• Detectar discrepancias\n"
        "• Identificar pagos sin factura\n"
        "• Generar reporte de conciliación\n\n"
        "¿Qué mes necesitas conciliar?",
        parse_mode="Markdown",
    )


async def nomina_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "👔 *Nóminas*\n\n"
        "Puedo ayudarte con:\n"
        "• CFDI de nómina ordinaria\n"
        "• Finiquitos y liquidaciones\n"
        "• Incidencias (incapacidades, permisos)\n"
        "• PRONAF\n"
        "• Cálculo de ISR e IMSS\n\n"
        "¿Qué necesitas procesar?",
        parse_mode="Markdown",
    )


async def resico_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "💰 *RESICO — Régimen Simplificado de Confianza*\n\n"
        "Puedo ayudarte con:\n"
        "• Cálculo de ISR progresivo (1-2.5%)\n"
        "• Control de tope de $3.5M anuales\n"
        "• Declaraciones bimestrales\n"
        "• Alertas de límite de ingresos\n\n"
        "¿De qué cliente necesitas calcular?",
        parse_mode="Markdown",
    )


async def organizar_cmd(update: Update, context) -> None:
    await update.message.reply_text(
        "📁 *Organizar Archivos*\n\n"
        "Puedo ayudarte a organizar el desorden de XMLs y PDFs:\n"
        "• Clasificar por cliente y RFC\n"
        "• Renombrar automáticamente\n"
        "• Detectar duplicados\n"
        "• Separar por año/mes/tipo\n\n"
        "¿Tienes archivos que necesitas ordenar?",
        parse_mode="Markdown",
    )


def main():
    if not OPENROUTER_KEY:
        logger.warning("OPENROUTER_API_KEY no configurada — el bot no podrá responder con IA")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("facturar", cfdi_cmd))
    app.add_handler(CommandHandler("declarar", declarar_cmd))
    app.add_handler(CommandHandler("conciliar", conciliar_cmd))
    app.add_handler(CommandHandler("nomina", nomina_cmd))
    app.add_handler(CommandHandler("resico", resico_cmd))
    app.add_handler(CommandHandler("organizar", organizar_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(handle_error)

    logger.info("Nathy Bot iniciado — @NathyCont_bot")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot detenido por usuario")
    except Exception as e:
        logger.error(f"Error en polling: {e}", exc_info=True)
        # Reintentar
        import time
        logger.info("Reiniciando en 5 segundos...")
        time.sleep(5)
        main()


if __name__ == "__main__":
    import sys
    while True:
        try:
            main()
        except Exception as e:
            logger.critical(f"Error fatal: {e}", exc_info=True)
            import time
            time.sleep(10)
