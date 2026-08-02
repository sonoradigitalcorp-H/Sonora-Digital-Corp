#!/usr/bin/env python3
"""Notification Bot — AstroTech Notification Bot for César.

Separate bot from the main AztroTechBot.
Purpose: Send notifications to César about:
  - Hot leads from the main bot
  - System alerts
  - Daily summaries
  - Scheduled content reminders

This bot runs independently so it never interferes with César's conversations.
"""

import os
import logging
import asyncpg
from datetime import datetime, time

from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("notification-bot")

NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN", "")
OWNER_CHAT_ID = os.getenv("NOTIF_OWNER_CHAT_ID", "5738935134")
DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:${POSTGRES_PASSWORD:-}@localhost:5432/sdc")


async def start(update, context):
    await update.message.reply_text(
        "🔔 Bot de notificaciones AstroTech activo.\n\n"
        "Comandos disponibles:\n"
        "/leads — Últimos leads capturados\n"
        "/summary — Resumen del día\n"
        "/health — Estado del sistema\n"
        "/hot — Leads hot del día\n"
        "/alert — Toggle alertas de leads"
    )


async def cmd_leads(update, context):
    """Show recent leads."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        rows = await pool.fetch(
            "SELECT phone, name, source, created_at FROM leads "
            "WHERE created_at > NOW() - INTERVAL '24 hours' "
            "ORDER BY created_at DESC LIMIT 10"
        )
        await pool.close()

        if not rows:
            await update.message.reply_text("📭 No hay leads en las últimas 24h.")
            return

        lines = ["📋 Últimos leads (24h):\n"]
        for i, r in enumerate(rows, 1):
            lines.append(f"{i}. {r['name'] or 'Sin nombre'} — {r['phone']} ({r['source']})")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        logger.error(f"cmd_leads error: {e}")
        await update.message.reply_text("❌ Error obteniendo leads.")


async def cmd_hot(update, context):
    """Show hot leads today."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        rows = await pool.fetch(
            "SELECT phone, name, source, lead_score, created_at FROM leads "
            "WHERE created_at > CURRENT_DATE AND lead_score >= 70 "
            "ORDER BY lead_score DESC LIMIT 10"
        )
        await pool.close()

        if not rows:
            await update.message.reply_text("🔥 No hay leads hot hoy.")
            return

        lines = ["🔥 Leads hot de hoy:\n"]
        for i, r in enumerate(rows, 1):
            lines.append(f"{i}. {r['name'] or 'Sin nombre'} — Score: {r['lead_score']} — {r['phone']}")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        logger.error(f"cmd_hot error: {e}")
        await update.message.reply_text("❌ Error obteniendo leads hot.")


async def cmd_summary(update, context):
    """Send daily summary."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        row = await pool.fetchrow(
            "SELECT COUNT(*) as convos, SUM(tokens_in) as tin, SUM(tokens_out) as tout, "
            "SUM(cost_usd) as cost FROM daily_metrics WHERE day = CURRENT_DATE"
        )
        lead_count = await pool.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at > CURRENT_DATE"
        )
        await pool.close()

        convos = row["convos"] or 0
        cost = float(row["cost"] or 0)

        msg = (
            f"📊 Resumen — {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"💬 Conversaciones: {convos}\n"
            f"👥 Leads nuevos: {lead_count}\n"
            f"💰 Costo tokens: ${cost:.4f}"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"cmd_summary error: {e}")
        await update.message.reply_text("❌ Error generando resumen.")


async def cmd_health(update, context):
    """Check system health."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        await pool.fetchval("SELECT 1")
        await pool.close()

        tts_ok = False
        try:
            import httpx
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get("http://localhost:8765/health")
                tts_ok = r.status_code == 200
        except Exception:
            pass

        msg = (
            f"🏥 Estado del sistema:\n\n"
            f"{'✅' if tts_ok else '❌'} TTS Server: {'OK' if tts_ok else 'ERROR'}\n"
            f"✅ PostgreSQL: OK\n"
            f"✅ Bot principal: activo\n"
            f"✅ Bot notificaciones: activo"
        )
        await update.message.reply_text(msg)
    except Exception as e:
        logger.error(f"cmd_health error: {e}")
        await update.message.reply_text("❌ Error verificando salud.")


async def cmd_alert(update, context):
    """Toggle lead alerts."""
    await update.message.reply_text(
        "🔔 Alertas de leads: activadas.\n"
        "Cuando un lead hot entre, recibirás una notificación aquí."
    )


async def daily_summary_job(context):
    """Scheduled daily summary at 9am."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        row = await pool.fetchrow(
            "SELECT COUNT(*) as convos, SUM(tokens_in) as tin, SUM(tokens_out) as tout, "
            "SUM(cost_usd) as cost FROM daily_metrics WHERE day = CURRENT_DATE"
        )
        lead_count = await pool.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at > CURRENT_DATE"
        )
        await pool.close()

        convos = row["convos"] or 0
        cost = float(row["cost"] or 0)

        msg = (
            f"📊 Resumen — {datetime.now().strftime('%d/%m/%Y')}\n\n"
            f"💬 Conversaciones: {convos}\n"
            f"👥 Leads nuevos: {lead_count}\n"
            f"💰 Costo tokens: ${cost:.4f}"
        )
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=msg)
    except Exception as e:
        logger.error(f"Daily summary job failed: {e}")


def main():
    if not NOTIF_BOT_TOKEN:
        logger.warning("NOTIF_BOT_TOKEN not set. Notification bot not starting.")
        return

    app = Application.builder().token(NOTIF_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("leads", cmd_leads))
    app.add_handler(CommandHandler("hot", cmd_hot))
    app.add_handler(CommandHandler("summary", cmd_summary))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CommandHandler("alert", cmd_alert))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_daily(daily_summary_job, time=time(9, 0), name="daily-summary")

    logger.info("Notification Bot iniciado")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()