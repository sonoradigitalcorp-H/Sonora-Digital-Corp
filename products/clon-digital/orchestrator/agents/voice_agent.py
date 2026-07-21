import logging
from typing import Optional, Callable
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Gather

from core.config import settings

logger = logging.getLogger(__name__)


class VoiceAgent:
    def __init__(self):
        self.client = None
        self.approval_callback: Optional[Callable] = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.client = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)
        self._sids = {}

    def set_approval_callback(self, callback: Callable):
        self.approval_callback = callback

    def _ensure_client(self):
        if not self.client:
            raise RuntimeError("Twilio not configured")

    async def call_client(self, to: str, message: str, order_id: Optional[str] = None) -> Optional[str]:
        self._ensure_client()
        try:
            response = VoiceResponse()
            gather = Gather(
                input="speech",
                action=f"{settings.base_url}/twilio/voice-response",
                method="POST", language="es-ES",
                speech_timeout="auto", speech_model="default",
            )
            gather.say(message, voice="Polly.Mia", language="es-ES")
            response.append(gather)
            response.say("No te escuché. Adiós.", voice="Polly.Mia", language="es-ES")

            call = self.client.calls.create(
                twiml=str(response),
                to=to,
                from_=settings.twilio_phone,
                status_callback=f"{settings.base_url}/twilio/voice-status",
                status_callback_event=["completed", "answered", "busy", "no-answer", "failed"],
            )
            logger.info(f"Call to {to}: {call.sid}")
            if order_id:
                self._sids[call.sid] = order_id
            return call.sid
        except Exception as e:
            logger.error(f"Call failed to {to}: {e}")
            return None

    async def call_me(self, message: str, order_id: Optional[str] = None) -> Optional[str]:
        if not settings.owner_phone:
            logger.info(f"Would call owner: {message}")
            return None
        return await self.call_client(settings.owner_phone, message, order_id)

    def handle_incoming_call(self, call_sid: str, caller: str) -> str:
        logger.info(f"Incoming call from {caller} ({call_sid})")
        response = VoiceResponse()
        gather = Gather(
            input="speech",
            action=f"{settings.base_url}/twilio/voice-intent",
            method="POST", language="es-ES",
            speech_timeout="auto", speech_model="default",
        )
        gather.say(
            "Hola, soy tu asistente de Clon Digital. "
            "Puedes pedirme crear un video, revisar el estado de un pedido, "
            "o si necesitas hablar con un humano, solo dilo. ¿Qué deseas hacer?",
            voice="Polly.Mia", language="es-ES",
        )
        response.append(gather)
        response.say("No te escuché. Adiós.", voice="Polly.Mia", language="es-ES")
        return str(response)

    def handle_speech_result(self, speech_result: str, order_id: Optional[str] = None) -> str:
        from agents.intent_classifier import classify_intent
        intent = classify_intent(speech_result)
        logger.info(f"Intent: {speech_result} -> {intent}")

        response = VoiceResponse()
        intent_type = intent.get("intent", "other")
        entities = intent.get("entities", {})

        if intent_type == "approve":
            response.say(
                "Perfecto, el video ha sido aprobado y se está entregando.",
                voice="Polly.Mia", language="es-ES",
            )
            if self.approval_callback and order_id:
                import asyncio
                asyncio.ensure_future(self.approval_callback(order_id, True))
        elif intent_type == "reject":
            reason = entities.get("reason", "")
            response.say(
                "Entendido, el video ha sido rechazado.",
                voice="Polly.Mia", language="es-ES",
            )
            if self.approval_callback and order_id:
                import asyncio
                asyncio.ensure_future(self.approval_callback(order_id, False, reason))
        elif intent_type == "check_orders":
            from core.database import db
            metrics = db.get_todays_metrics()
            completed = int(metrics.get("orders_completed", 0))
            pending_count = len(db.list_orders(status="awaiting_approval"))
            response.say(
                f"Tienes {completed} videos completados hoy y {pending_count} pendientes.",
                voice="Polly.Mia", language="es-ES",
            )
        elif intent_type == "speak_human":
            if settings.owner_phone:
                response.dial(settings.owner_phone)
        else:
            response.say(
                "No entendí bien. Di: aprueba, rechaza, o revisa pedidos.",
                voice="Polly.Mia", language="es-ES",
            )

        return str(response)

    def get_order_for_call(self, call_sid: str) -> Optional[str]:
        return self._sids.get(call_sid)
