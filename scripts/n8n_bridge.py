#!/usr/bin/env python3
"""n8n Bridge — Webhook server para integrar el bot con n8n.

Este servidor expone endpoints que n8n puede llamar para:
  - /webhook/lead_hot   → Notificar lead hot al bot de notificaciones
  - /webhook/followup   → Disparar follow-up automático
  - /webhook/schedule   → Programar mensaje futuro
  - /webhook/status     → Estado del sistema para n8n

También permite que el bot dispare workflows de n8n:
  - Lead capturado → n8n workflow (CRM update, email, calendar)
  - Lead hot → n8n workflow (notify César, create task)
"""

import os
import json
import logging
import asyncio
import asyncpg
from datetime import datetime
from aiohttp import web, ClientSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("n8n-bridge")

DB_URL = "postgresql://sdc:sdc_local_dev@localhost:5432/sdc"
N8N_BASE = "http://localhost:5678"
NOTIF_BOT_TOKEN = os.getenv("NOTIF_BOT_TOKEN", "8782296127:AAHO6Fx7U6WfvS8AyD5h6rLYqc5wJ7Sf3nY")
OWNER_CHAT_ID = os.getenv("NOTIF_OWNER_CHAT_ID", "5738935134")
PORT = 8767


async def handle_lead_hot(request):
    """n8n llama este endpoint cuando un lead hot es detectado."""
    try:
        data = await request.json()
        phone = data.get("phone", "")
        name = data.get("name", "Anónimo")
        score = data.get("score", 0)
        source = data.get("source", "telegram")

        # Guardar en Postgres
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        await pool.execute(
            "INSERT INTO leads (phone, name, source, lead_score, lead_type, notes) "
            "VALUES ($1, $2, $3, $4, 'hot', $5)",
            phone, name, source, score, json.dumps(data),
        )
        await pool.close()

        # Notificar a César via bot de notificaciones
        msg = (
            f"🔥 NUEVO LEAD HOT\n\n"
            f"👤 {name}\n"
            f"📱 {phone}\n"
            f"📊 Score: {score}/100\n"
            f"💬 Fuente: {source}\n"
            f"🕐 {datetime.now().strftime('%H:%M')}"
        )
        async with ClientSession() as session:
            await session.post(
                f"https://api.telegram.org/bot{NOTIF_BOT_TOKEN}/sendMessage",
                json={"chat_id": OWNER_CHAT_ID, "text": msg},
            )

        return web.json_response({"status": "ok", "lead_id": phone})
    except Exception as e:
        logger.error(f"lead_hot error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def handle_followup(request):
    """n8n llama este endpoint para disparar follow-up a un lead."""
    try:
        data = await request.json()
        phone = data.get("phone", "")
        message = data.get("message", "")

        # Aquí se integraría con wacli para enviar WhatsApp
        # Por ahora solo logueamos
        logger.info(f"Follow-up programado para {phone}: {message}")

        return web.json_response({"status": "ok", "phone": phone})
    except Exception as e:
        logger.error(f"followup error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def handle_schedule(request):
    """Programar un mensaje futuro."""
    try:
        data = await request.json()
        phone = data.get("phone", "")
        message = data.get("message", "")
        send_at = data.get("send_at", "")

        logger.info(f"Mensaje programado para {phone} a las {send_at}: {message}")
        return web.json_response({"status": "ok"})
    except Exception as e:
        logger.error(f"schedule error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def handle_status(request):
    """Estado del sistema para n8n."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=1)
        convos = await pool.fetchval("SELECT count(*) FROM conversations WHERE started_at > CURRENT_DATE")
        leads = await pool.fetchval("SELECT count(*) FROM leads WHERE created_at > CURRENT_DATE")
        hot_leads = await pool.fetchval("SELECT count(*) FROM leads WHERE lead_score >= 70 AND created_at > CURRENT_DATE")
        await pool.close()

        import aiohttp
        async with ClientSession() as session:
            tts_resp = await session.get("http://localhost:8765/health", timeout=2)
            tts_ok = tts_resp.status == 200
            qdrant_resp = await session.get("http://localhost:6333/collections", timeout=2)
            qdrant_ok = qdrant_resp.status == 200

        return web.json_response({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "conversations_today": convos,
                "leads_today": leads,
                "hot_leads_today": hot_leads,
                "tts_server": "up" if tts_ok else "down",
                "qdrant": "up" if qdrant_ok else "down",
            }
        })
    except Exception as e:
        return web.json_response({"status": "error", "message": str(e)}, status=500)


async def handle_n8n_trigger(request):
    """El bot llama este endpoint para disparar un workflow de n8n."""
    try:
        data = await request.json()
        workflow_id = data.get("workflow_id", "")
        payload = data.get("payload", {})

        async with ClientSession() as session:
            resp = await session.post(
                f"{N8N_BASE}/webhook/{workflow_id}",
                json=payload,
                timeout=10,
            )
            result = await resp.text()

        return web.json_response({"status": "ok", "n8n_response": result})
    except Exception as e:
        logger.error(f"n8n_trigger error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)


def main():
    app = web.Application()
    app.router.add_post("/webhook/lead_hot", handle_lead_hot)
    app.router.add_post("/webhook/followup", handle_followup)
    app.router.add_post("/webhook/schedule", handle_schedule)
    app.router.add_get("/webhook/status", handle_status)
    app.router.add_post("/n8n/trigger", handle_n8n_trigger)

    logger.info(f"n8n Bridge iniciando en puerto {PORT}")
    web.run_app(app, port=PORT)


if __name__ == "__main__":
    main()