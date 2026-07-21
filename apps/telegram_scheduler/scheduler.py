"""Automatic scheduler that checks and sends pending messages."""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from telegram.ext import Application

sys.path.insert(0, str(Path(__file__).parent))
import db
import whatsapp as wa

logger = logging.getLogger(__name__)

CHECK_INTERVAL = 30

OWNER_ID = os.environ.get("OWNER_TELEGRAM_ID")


def start_scheduler(application: Application) -> asyncio.Task:
    task = asyncio.create_task(_scheduler_loop(application))
    logger.info("Scheduler started (interval=%ds)", CHECK_INTERVAL)
    return task


async def _scheduler_loop(application: Application) -> None:
    while True:
        try:
            await _check_and_send(application)
        except Exception as e:
            logger.error("Scheduler error: %s", e, exc_info=True)
        await asyncio.sleep(CHECK_INTERVAL)


async def _check_and_send(application: Application) -> None:
    now = datetime.now()
    pendientes = db.get_pendientes()

    for msg in pendientes:
        programado = datetime.fromisoformat(msg["programado_para"])
        if programado > now:
            continue

        cliente_nombre = msg["nombre"]
        cliente_id = msg["cliente_id"]
        contenido = msg["contenido"]
        msg_id = msg["id"]
        canal = (msg["canal"] or "auto").lower()

        has_tg = bool(msg["telegram_id"])
        has_wa = bool(msg["whatsapp_jid"])

        use_telegram = False
        use_whatsapp = False

        if canal == "telegram":
            use_telegram = has_tg
        elif canal == "whatsapp":
            use_whatsapp = has_wa
        else:
            if has_tg:
                use_telegram = True
            elif has_wa:
                use_whatsapp = True

        success = False
        channel_used = None
        error_msg = None

        if use_telegram:
            try:
                await application.bot.send_message(
                    chat_id=int(msg["telegram_id"]),
                    text=f"📩 *Mensaje de Mystic:*\n\n{contenido}",
                    parse_mode="Markdown"
                )
                success = True
                channel_used = "telegram"
            except Exception as e:
                error_msg = str(e)[:200]
                logger.warning("Telegram send failed for %s: %s", cliente_nombre, error_msg)
                if canal == "auto" and has_wa:
                    use_whatsapp = True

        if not success and use_whatsapp:
            ok, result = wa.send_whatsapp(msg["whatsapp_jid"], contenido)
            success = ok
            channel_used = "whatsapp"
            if not ok:
                error_msg = result
                logger.warning("WhatsApp send failed for %s: %s", cliente_nombre, error_msg)

        if success:
            sent_at = datetime.now().isoformat()
            db.update_mensaje_estado(msg_id, "enviado", enviado_en=sent_at)
            db.add_historial(cliente_id, contenido, channel_used, "enviado", sent_at=sent_at)
            logger.info("Mensaje %d enviado a %s via %s", msg_id, cliente_nombre, channel_used)
        else:
            db.update_mensaje_estado(msg_id, "fallido", error_msg=error_msg)
            db.add_historial(
                cliente_id, contenido, canal or "auto", "fallido",
                error_msg=error_msg
            )
            logger.error("Mensaje %d FALLIDO para %s: %s", msg_id, cliente_nombre, error_msg)
            await _notify_owner(application, cliente_nombre, msg_id, contenido, error_msg)


async def _notify_owner(application: Application, cliente: str, msg_id: int, contenido: str, error: str) -> None:
    if not OWNER_ID:
        return
    try:
        preview = contenido[:100] + ("..." if len(contenido) > 100 else "")
        await application.bot.send_message(
            chat_id=int(OWNER_ID),
            text=(
                f"❌ *Falló envío a {cliente}*\n"
                f"🆔 Mensaje: `{msg_id}`\n"
                f"📝 {preview}\n"
                f"🔴 Error: `{error}`"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error("Failed to notify owner: %s", e)
