#!/usr/bin/env python3
"""Mystic Notification Bot — Notificaciones de leads y agenda para César.

Envía leads en formato de tarjeta visual con:
- Nombre, teléfono, score del lead
- Botones de acción rápida
- Integración con Google Calendar para verificar agenda
"""

import os
import json
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("mystic-notif")

NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN", "")
OWNER_CHAT_ID = os.getenv("NOTIF_OWNER_CHAT_ID", "5738935134")

# Google Calendar
GOOGLE_CREDS_PATH = os.getenv("GOOGLE_CALENDAR_CREDS", "")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")


def get_calendar_service():
    """Create Google Calendar service."""
    if not GOOGLE_CREDS_PATH or not os.path.exists(GOOGLE_CREDS_PATH):
        return None
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        scopes = ["https://www.googleapis.com/auth/calendar.readonly"]
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDS_PATH, scopes=scopes
        )
        return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.warning(f"Google Calendar no disponible: {e}")
        return None


def get_upcoming_events(service, hours=24):
    """Get upcoming events from Google Calendar."""
    if not service:
        return []
    try:
        now = datetime.utcnow()
        end = now + timedelta(hours=hours)
        
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            maxResults=10,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        return events_result.get("items", [])
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        return []


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔔 <b>Mystic Notificaciones</b>\n\n"
        "Recibe alertas de leads y verifica la agenda.\n\n"
        "Comandos:\n"
        "/leads — Últimos leads\n"
        "/hot — Leads hot\n"
        "/agenda — Ver agenda de hoy\n"
        "/resumen — Resumen del día\n"
        "/salud — Estado del sistema",
        parse_mode="HTML"
    )


async def cmd_leads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show recent leads."""
    try:
        import asyncpg
        DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        rows = await pool.fetch(
            "SELECT phone, name, source, lead_score, created_at FROM leads "
            "WHERE created_at > NOW() - INTERVAL '24 hours' "
            "ORDER BY created_at DESC LIMIT 10"
        )
        await pool.close()

        if not rows:
            await update.message.reply_text("📭 No hay leads en las últimas 24h.", parse_mode="HTML")
            return

        msg = "📋 <b>Últimos leads (24h)</b>\n\n"
        for i, r in enumerate(rows, 1):
            score = r['lead_score'] or 0
            emoji = "🔴" if score >= 70 else "🟡" if score >= 40 else "🔵"
            msg += f"{emoji} <b>{i}. {r['name'] or 'Sin nombre'}</b>\n"
            msg += f"   📱 {r['source']} | Score: {score}\n"
            msg += f"   📅 {r['created_at'].strftime('%d/%m %H:%M')}\n\n"
        
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"cmd_leads error: {e}")
        await update.message.reply_text("❌ Error obteniendo leads.", parse_mode="HTML")


async def cmd_hot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hot leads."""
    try:
        import asyncpg
        DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        rows = await pool.fetch(
            "SELECT phone, name, source, lead_score, created_at FROM leads "
            "WHERE created_at > CURRENT_DATE AND lead_score >= 70 "
            "ORDER BY lead_score DESC LIMIT 10"
        )
        await pool.close()

        if not rows:
            await update.message.reply_text("🔥 No hay leads hot hoy.", parse_mode="HTML")
            return

        msg = "🔥 <b>Leads hot de hoy</b>\n\n"
        for i, r in enumerate(rows, 1):
            msg += f"🔴 <b>{r['name'] or 'Sin nombre'}</b>\n"
            msg += f"   📊 Score: {r['lead_score']} | 📱 {r['source']}\n"
            msg += f"   📅 {r['created_at'].strftime('%H:%M')}\n\n"
        
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"cmd_hot error: {e}")
        await update.message.reply_text("❌ Error obteniendo leads hot.", parse_mode="HTML")


async def cmd_agenda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show upcoming calendar events."""
    service = get_calendar_service()
    if not service:
        await update.message.reply_text(
            "📅 <b>Agenda</b>\n\n"
            "⚠️ Google Calendar no configurado.\n"
            "Configura GOOGLE_CALENDAR_CREDS en el servicio.",
            parse_mode="HTML"
        )
        return
    
    events = get_upcoming_events(service, hours=48)
    
    if not events:
        await update.message.reply_text("📅 No hay eventos próximos en las próximas 48 horas.", parse_mode="HTML")
        return
    
    msg = "📅 <b>Tu agenda (próximas 48h)</b>\n\n"
    for event in events[:10]:
        start = event["start"].get("dateTime", event["start"].get("date"))
        try:
            dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            time_str = dt.strftime("%d/%m %H:%M")
        except:
            time_str = start
        
        summary = event.get("summary", "Sin título")
        msg += f"🕐 <b>{time_str}</b> — {summary}\n"
        
        if event.get("location"):
            msg += f"   📍 {event['location']}\n"
        if event.get("description"):
            desc = event["description"][:100]
            msg += f"   📝 {desc}\n"
        msg += "\n"
    
    await update.message.reply_text(msg, parse_mode="HTML")


async def cmd_resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Daily summary."""
    try:
        import asyncpg
        DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        
        row = await pool.fetchrow(
            "SELECT COUNT(*) as convos, SUM(cost_usd) as cost FROM daily_metrics WHERE day = CURRENT_DATE"
        )
        lead_count = await pool.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at > CURRENT_DATE"
        )
        hot_count = await pool.fetchval(
            "SELECT COUNT(*) FROM leads WHERE created_at > CURRENT_DATE AND lead_score >= 70"
        )
        await pool.close()

        convos = row["convos"] or 0
        cost = float(row["cost"] or 0)

        msg = (
            f"📊 <b>Resumen — {datetime.now().strftime('%d/%m/%Y')}</b>\n\n"
            f"💬 Conversaciones: {convos}\n"
            f"👥 Leads nuevos: {lead_count}\n"
            f"🔴 Leads hot: {hot_count}\n"
            f"💰 Costo tokens: ${cost:.4f}\n"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
    except Exception as e:
        logger.error(f"cmd_resumen error: {e}")
        await update.message.reply_text("❌ Error generando resumen.", parse_mode="HTML")


async def cmd_salud(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """System health."""
    import httpx
    
    tts_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:8765/health")
            tts_ok = r.status_code == 200
    except:
        pass
    
    postgres_ok = False
    try:
        import asyncpg
        DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        await pool.fetchval("SELECT 1")
        await pool.close()
        postgres_ok = True
    except:
        pass
    
    qdrant_ok = False
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("http://localhost:6333/collections")
            qdrant_ok = r.status_code == 200
    except:
        pass
    
    redis_ok = False
    try:
        import redis
        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        redis_ok = True
    except:
        pass
    
    calendar_ok = get_calendar_service() is not None
    
    msg = (
        "🏥 <b>Estado del sistema</b>\n\n"
        f"{'✅' if tts_ok else '❌'} TTS Server: {'OK' if tts_ok else 'ERROR'}\n"
        f"{'✅' if postgres_ok else '❌'} PostgreSQL: {'OK' if postgres_ok else 'ERROR'}\n"
        f"{'✅' if qdrant_ok else '❌'} Qdrant: {'OK' if qdrant_ok else 'ERROR'}\n"
        f"{'✅' if redis_ok else '❌'} Redis: {'OK' if redis_ok else 'ERROR'}\n"
        f"{'✅' if calendar_ok else '⚠️'} Google Calendar: {'OK' if calendar_ok else 'NO CONFIGURADO'}\n"
    )
    await update.message.reply_text(msg, parse_mode="HTML")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages."""
    msg = update.message
    if msg and msg.text:
        await msg.reply_text(
            "🔔 <b>Mystic Notificaciones</b>\n\n"
            "Usa los comandos:\n"
            "/leads — Últimos leads\n"
            "/hot — Leads hot\n"
            "/agenda — Ver agenda\n"
            "/resumen — Resumen del día\n"
            "/salud — Estado del sistema",
            parse_mode="HTML"
        )


async def send_lead_notification(context: ContextTypes.DEFAULT_TYPE, lead_data: dict):
    """Send rich lead notification card."""
    chat_id = lead_data.get("chat_id", OWNER_CHAT_ID)
    
    name = lead_data.get("name", "Sin nombre")
    phone = lead_data.get("phone", "")
    score = lead_data.get("score", 0)
    emotion = lead_data.get("emotion", "neutral")
    source = lead_data.get("source", "telegram")
    message = lead_data.get("message", "")
    
    score_emoji = "🔴" if score >= 70 else "🟡" if score >= 40 else "🔵"
    score_label = "HOT" if score >= 70 else "WARM" if score >= 40 else "COLD"
    
    # Check calendar availability
    service = get_calendar_service()
    calendar_info = ""
    if service:
        events = get_upcoming_events(service, hours=2)
        if events:
            calendar_info = "\n⚠️ <b>Tienes eventos en las próximas 2 horas:</b>\n"
            for e in events[:3]:
                start = e["start"].get("dateTime", e["start"].get("date"))
                try:
                    dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
                    calendar_info += f"  • {dt.strftime('%H:%M')} - {e.get('summary', 'Sin título')}\n"
                except:
                    calendar_info += f"  • {start} - {e.get('summary', 'Sin título')}\n"
        else:
            calendar_info = "\n✅ <b>Tu agenda está libre en las próximas 2 horas</b>"
    
    msg = (
        f"🔔 <b>NUEVO LEAD</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 <b>{name}</b>\n"
        f"📱 {phone}\n"
        f"🌐 {source}\n\n"
        f"{score_emoji} <b>Score: {score} ({score_label})</b>\n"
        f"😊 Emoción: {emotion}\n"
        f"💬 <i>\"{message[:150]}\"</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{calendar_info}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📲 <b>Acciones:</b>"
    )
    
    wa_link = f"https://wa.me/52{phone}" if phone else "https://wa.me/526621072254"
    tg_link = f"https://t.me/{source}" if source != "telegram" else "https://t.me/"
    
    keyboard = [
        [
            InlineKeyboardButton("📲 WhatsApp", url=wa_link),
            InlineKeyboardButton("🌐 Perfil", url=tg_link),
        ],
        [
            InlineKeyboardButton("✅ Contactado", callback_data=f"lead_done_{lead_data.get('user_id', '')}"),
            InlineKeyboardButton("📅 Agendar llamada", callback_data=f"lead_schedule_{lead_data.get('user_id', '')}"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=chat_id,
        text=msg,
        parse_mode="HTML",
        reply_markup=reply_markup
    )


def main():
    if not NOTIF_BOT_TOKEN:
        logger.warning("NOTIF_BOT_TOKEN not set. Notification bot not starting.")
        return

    app = Application.builder().token(NOTIF_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("leads", cmd_leads))
    app.add_handler(CommandHandler("hot", cmd_hot))
    app.add_handler(CommandHandler("agenda", cmd_agenda))
    app.add_handler(CommandHandler("resumen", cmd_resumen))
    app.add_handler(CommandHandler("salud", cmd_salud))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Mystic Notification Bot iniciado")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
