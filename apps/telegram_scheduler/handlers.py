"""Telegram command handlers for the scheduler bot."""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

sys.path.insert(0, str(Path(__file__).parent))
import db
import whatsapp as wa

logger = logging.getLogger(__name__)

OWNER_ID = os.environ.get("OWNER_TELEGRAM_ID")


def _is_owner(update: Update) -> bool:
    return str(update.effective_user.id) == OWNER_ID


async def _check_owner(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not _is_owner(update):
        await update.message.reply_text(
            "⛔ No autorizado. Solo el dueño del bot puede usar este comando."
        )
        return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    text = (
        "🤖 *Telegram Scheduler — Sonora Digital Corp*\n\n"
        "Programa mensajes para tus clientes y se envían automáticamente.\n\n"
        "*Comandos:*\n"
        "📋 `/clientes` — Lista todos los clientes\n"
        "➕ `/agregar_cliente <nombre> [telegram_id] [whatsapp_jid]` — Nuevo cliente\n"
        "🗑️ `/eliminar_cliente <nombre>` — Elimina cliente\n"
        "📅 `/programar <nombre> \\\"<mensaje>\\\" <YYYY-MM-DD> <HH:MM>` — Programa mensaje\n"
        "⚡ `/programar_hoy <nombre> \\\"<mensaje>\\\" <HH:MM>` — Atajo para hoy\n"
        "📌 `/pendientes` — Mensajes pendientes\n"
        "❌ `/cancelar <id>` — Cancela mensaje\n"
        "📜 `/historial <nombre>` — Últimos 10 mensajes\n\n"
        "_Los mensajes se envían por Telegram si el cliente tiene Telegram ID, "
        "o por WhatsApp si solo tiene JID._"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def agregar_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Usa: `/agregar_cliente <nombre> [telegram_id] [whatsapp_jid]`",
            parse_mode="Markdown"
        )
        return
    nombre = args[0]
    telegram_id = None
    whatsapp_jid = None
    if len(args) > 1:
        if args[1].replace("+", "").isdigit():
            telegram_id = args[1]
        else:
            whatsapp_jid = args[1]
    if len(args) > 2:
        if args[2].replace("+", "").isdigit():
            telegram_id = args[2]
        else:
            whatsapp_jid = args[2]
    try:
        cliente_id = db.add_cliente(nombre, telegram_id, whatsapp_jid)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return
    msg = f"✅ Cliente *{nombre}* agregado (ID: `{cliente_id}`)"
    if telegram_id:
        msg += f"\n📱 Telegram ID: `{telegram_id}`"
    if whatsapp_jid:
        msg += f"\n💬 WhatsApp: `{whatsapp_jid}`"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def clientes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    clientes = db.list_clientes()
    if not clientes:
        await update.message.reply_text("📭 No hay clientes registrados.")
        return
    lines = ["📋 *Clientes registrados:*\n"]
    for c in clientes:
        tg = "✅" if c["telegram_id"] else "❌"
        wa_icon = "✅" if c["whatsapp_jid"] else "❌"
        lines.append(
            f"• *{c['nombre']}* (ID: `{c['id']}`)\n"
            f"  📱 Telegram: {tg}  💬 WhatsApp: {wa_icon}"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def programar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    text = update.message.text
    cmd_end = text.find(" ")
    if cmd_end == -1:
        await update.message.reply_text(
            "❌ Formato: `/programar <nombre> \\\"<mensaje>\\\" <YYYY-MM-DD> <HH:MM>`",
            parse_mode="Markdown"
        )
        return
    rest = text[cmd_end + 1:]
    quote_start = rest.find('"')
    if quote_start == -1:
        await update.message.reply_text(
            "❌ El mensaje debe ir entre comillas dobles.\n"
            "Formato: `/programar <nombre> \\\"<mensaje>\\\" <YYYY-MM-DD> <HH:MM>`",
            parse_mode="Markdown"
        )
        return
    nombre = rest[:quote_start].strip()
    if not nombre:
        await update.message.reply_text("❌ Debes especificar el nombre del cliente.")
        return
    quote_end = rest.find('"', quote_start + 1)
    if quote_end == -1:
        await update.message.reply_text("❌ Faltan las comillas de cierre del mensaje.")
        return
    mensaje = rest[quote_start + 1:quote_end]
    if not mensaje:
        await update.message.reply_text("❌ El mensaje no puede estar vacío.")
        return
    after_quote = rest[quote_end + 1:].strip()
    parts = after_quote.split()
    if len(parts) < 2:
        await update.message.reply_text(
            "❌ Faltan la fecha o la hora.\nFormato: `... <YYYY-MM-DD> <HH:MM>`",
            parse_mode="Markdown"
        )
        return
    fecha_str = parts[0]
    hora_str = parts[1]
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text(
            "❌ Fecha inválida. Usa formato YYYY-MM-DD (ej: 2025-07-20)"
        )
        return
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "❌ Hora inválida. Usa formato HH:MM en 24h (ej: 15:30)"
        )
        return
    programado_para = datetime.combine(fecha, hora)
    now = datetime.now()
    if programado_para <= now:
        await update.message.reply_text("❌ No puedes programar mensajes en el pasado.")
        return
    cliente = db.get_cliente(nombre)
    if not cliente:
        await update.message.reply_text(
            f"❌ Cliente *{nombre}* no encontrado. Usa `/agregar_cliente` primero.",
            parse_mode="Markdown"
        )
        return
    msg_id = db.add_mensaje(cliente["id"], mensaje, programado_para.isoformat())
    preview = mensaje[:100] + ("..." if len(mensaje) > 100 else "")
    await update.message.reply_text(
        f"✅ Mensaje programado para *{nombre}*\n"
        f"📅 {fecha_str} a las {hora_str}\n"
        f"📝 {preview}\n"
        f"🆔 ID: `{msg_id}`",
        parse_mode="Markdown"
    )


async def programar_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    text = update.message.text
    cmd_end = text.find(" ")
    if cmd_end == -1:
        await update.message.reply_text(
            "❌ Formato: `/programar_hoy <nombre> \\\"<mensaje>\\\" <HH:MM>`",
            parse_mode="Markdown"
        )
        return
    rest = text[cmd_end + 1:]
    quote_start = rest.find('"')
    if quote_start == -1:
        await update.message.reply_text(
            "❌ El mensaje debe ir entre comillas dobles.\n"
            "Formato: `/programar_hoy <nombre> \\\"<mensaje>\\\" <HH:MM>`",
            parse_mode="Markdown"
        )
        return
    nombre = rest[:quote_start].strip()
    if not nombre:
        await update.message.reply_text("❌ Debes especificar el nombre del cliente.")
        return
    quote_end = rest.find('"', quote_start + 1)
    if quote_end == -1:
        await update.message.reply_text("❌ Faltan las comillas de cierre del mensaje.")
        return
    mensaje = rest[quote_start + 1:quote_end]
    if not mensaje:
        await update.message.reply_text("❌ El mensaje no puede estar vacío.")
        return
    after_quote = rest[quote_end + 1:].strip()
    if not after_quote:
        await update.message.reply_text("❌ Falta la hora. Formato: `... <HH:MM>`")
        return
    hora_str = after_quote.split()[0]
    try:
        hora = datetime.strptime(hora_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text(
            "❌ Hora inválida. Usa formato HH:MM en 24h (ej: 15:30)"
        )
        return
    today = datetime.now().date()
    programado_para = datetime.combine(today, hora)
    now = datetime.now()
    if programado_para <= now:
        await update.message.reply_text("❌ Esa hora ya pasó hoy.")
        return
    cliente = db.get_cliente(nombre)
    if not cliente:
        await update.message.reply_text(
            f"❌ Cliente *{nombre}* no encontrado.",
            parse_mode="Markdown"
        )
        return
    msg_id = db.add_mensaje(cliente["id"], mensaje, programado_para.isoformat())
    preview = mensaje[:100] + ("..." if len(mensaje) > 100 else "")
    await update.message.reply_text(
        f"✅ Mensaje programado para HOY *{nombre}* a las {hora_str}\n"
        f"📝 {preview}\n"
        f"🆔 ID: `{msg_id}`",
        parse_mode="Markdown"
    )


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("❌ Usa: `/cancelar <id_mensaje>`", parse_mode="Markdown")
        return
    msg_id = int(context.args[0])
    mensaje = db.get_mensaje(msg_id)
    if not mensaje:
        await update.message.reply_text(f"❌ Mensaje con ID `{msg_id}` no encontrado.", parse_mode="Markdown")
        return
    if mensaje["estado"] != "pendiente":
        status_map = {"enviado": "✅ ya fue enviado", "fallido": "❌ falló al enviar", "cancelado": "⏭️ ya fue cancelado"}
        status_text = status_map.get(mensaje["estado"], mensaje["estado"])
        await update.message.reply_text(f"⚠️ El mensaje ID `{msg_id}` {status_text}.")
        return
    ok = db.cancel_mensaje(msg_id)
    if ok:
        await update.message.reply_text(f"✅ Mensaje `{msg_id}` cancelado.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ No se pudo cancelar el mensaje `{msg_id}`.", parse_mode="Markdown")


async def pendientes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    pendientes = db.get_pendientes()
    if not pendientes:
        await update.message.reply_text("✅ No hay mensajes pendientes.")
        return
    lines = ["📌 *Mensajes pendientes:*\n"]
    for m in pendientes:
        fecha = datetime.fromisoformat(m["programado_para"]).strftime("%d/%m/%Y %H:%M")
        canal = m["canal"] or "auto"
        preview = m["contenido"][:80] + ("..." if len(m["contenido"]) > 80 else "")
        lines.append(
            f"🆔 `{m['id']}` — *{m['nombre']}*\n"
            f"📅 {fecha}  📡 {canal}\n"
            f"📝 {preview}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def historial(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Usa: `/historial <nombre_cliente>`", parse_mode="Markdown")
        return
    nombre = " ".join(context.args)
    cliente = db.get_cliente(nombre)
    if not cliente:
        await update.message.reply_text(f"❌ Cliente *{nombre}* no encontrado.", parse_mode="Markdown")
        return
    registros = db.get_historial(cliente["id"])
    if not registros:
        await update.message.reply_text(f"📭 No hay historial para *{nombre}*.", parse_mode="Markdown")
        return
    lines = [f"📜 *Historial de {nombre}* (últimos {len(registros)}):\n"]
    for r in registros:
        fecha = datetime.fromisoformat(r["sent_at"]).strftime("%d/%m/%Y %H:%M")
        estado_icon = "✅" if r["estado"] == "enviado" else "❌"
        error = f" — `{r['error_msg']}`" if r.get("error_msg") else ""
        preview = r["contenido"][:80] + ("..." if len(r["contenido"]) > 80 else "")
        lines.append(
            f"{estado_icon} [{fecha}] *{r['canal']}*\n"
            f"📝 {preview}{error}\n"
        )
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def eliminar_cliente(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _check_owner(update, context):
        return
    if not context.args:
        await update.message.reply_text("❌ Usa: `/eliminar_cliente <nombre>`", parse_mode="Markdown")
        return
    nombre = " ".join(context.args)
    ok = db.delete_cliente(nombre)
    if ok:
        await update.message.reply_text(f"🗑️ Cliente *{nombre}* eliminado.", parse_mode="Markdown")
    else:
        await update.message.reply_text(f"❌ Cliente *{nombre}* no encontrado.", parse_mode="Markdown")


def register_handlers(app) -> None:
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("agregar_cliente", agregar_cliente))
    app.add_handler(CommandHandler("clientes", clientes))
    app.add_handler(CommandHandler("programar", programar))
    app.add_handler(CommandHandler("programar_hoy", programar_hoy))
    app.add_handler(CommandHandler("cancelar", cancelar))
    app.add_handler(CommandHandler("pendientes", pendientes))
    app.add_handler(CommandHandler("historial", historial))
    app.add_handler(CommandHandler("eliminar_cliente", eliminar_cliente))
