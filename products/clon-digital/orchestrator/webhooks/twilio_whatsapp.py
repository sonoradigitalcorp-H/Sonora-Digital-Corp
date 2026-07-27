import logging
from fastapi import APIRouter, Form, Request
from twilio.twiml.messaging_response import MessagingResponse

from apps.core.orchestrator import orchestrator
from apps.core.database import db
from agents.messaging_agent import MessagingAgent

logger = logging.getLogger(__name__)

router = APIRouter()
msg_agent = MessagingAgent()


@router.post("/twilio/whatsapp")
async def whatsapp_webhook(request: Request):
    form = await request.form()
    data = msg_agent.parse_whatsapp_webhook(dict(form))

    from_number = data["from"]
    body = data["body"].strip().lower()
    media_url = data["media_url"]

    resp = MessagingResponse()

    if media_url:
        logger.info(f"WhatsApp photo from {from_number}: {media_url}")
        await orchestrator.handle_incoming_photo(from_number, media_url)
        return str(resp)

    if body:
        logger.info(f"WhatsApp message from {from_number}: {body}")

        has_pending = any(
            o.get("client_phone") == from_number and o.get("status") in ("requesting_photo", "created")
            for o in db.list_orders()
        )

        if has_pending:
            resp.message("¡Hola! Por favor envíame una foto clara de tu rostro para empezar.")
        elif any(w in body for w in ["video", "quiero", "crea", "hazme", "hacer"]):
            resp.message(
                "¡Genial! Para crear tu video necesito:\n\n"
                "1️⃣ Una foto clara de tu rostro (frontal, bien iluminada)\n"
                "2️⃣ El texto que quieres que diga\n\n"
                "¡Empieza enviándome tu foto! 📸"
            )
        elif any(w in body for w in ["gracias", "ok", "vale"]):
            resp.message("¡De nada! Cuando quieras otro video, aquí estoy. 🎬")
        else:
            resp.message(
                "Hola, soy el asistente de Clon Digital. 🎬\n\n"
                "Puedes pedirme un video personalizado enviando:\n"
                "• Una foto tuya 📸\n"
                "• El texto que quieres que diga\n\n"
                "¿Te animas?"
            )

    return str(resp)
