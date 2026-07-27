import json
import logging
from openai import OpenAI

from apps.core.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

SYSTEM_PROMPT = """Eres un clasificador de intención para un sistema de clon digital.
El usuario puede estar aprobando un video, rechazándolo, pidiendo información,
o queriendo hablar con un humano.

Responde SOLO con JSON:
{
  "intent": "approve" | "reject" | "check_orders" | "new_order" | "speak_human" | "other",
  "confidence": 0.0-1.0,
  "entities": {
    "order_id": "..." (si se menciona),
    "reason": "..." (si es rechazo),
    "product": "..." (si es pedido nuevo)
  }
}

Ejemplos:
- "sí entrégalo" → {"intent": "approve", "confidence": 0.95, "entities": {}}
- "no, la voz no suena natural" → {"intent": "reject", "confidence": 0.9, "entities": {"reason": "voz no natural"}}
- "cuántos videos van hoy" → {"intent": "check_orders", "confidence": 0.9, "entities": {}}
- "quiero un video" → {"intent": "new_order", "confidence": 0.85, "entities": {}}
- "quiero hablar con una persona" → {"intent": "speak_human", "confidence": 0.95, "entities": {}}
"""


def classify_intent(text: str) -> dict:
    if not client:
        logger.warning("OpenAI not configured, using basic classification")

        import re
        text_lower = text.lower().strip()
        words = set(re.findall(r'\b\w+\b', text_lower))

        approval_words = {"sí", "si", "aprueba", "entrégalo", "dale", "ok", "aprobado", "entregalo", "apruebalo", "adelante"}
        reject_words = {"no", "rechaza", "rechazado", "malo", "cambia", "detente", "equivocado"}
        check_words = {"cuántos", "cuantos", "pedidos", "órdenes", "ordenes", "estado", "progreso", "avance"}
        human_words = {"humano", "persona", "transferir", "operador", "asistente"}

        reject_phrases = ["no me gusta", "mejor no", "está mal", "no está bien", "cámbialo"]
        new_order_words = {"video", "nuevo", "crea", "crear", "hazme", "hacer", "quiero"}
        new_order_phrases = ["quiero un video", "crea un video", "hazme un video", "nuevo video", "otro video"]
        human_phrases = ["hablar con alguien", "hablar con un humano", "hablar con una persona", "habla conmigo"]

        for w in approval_words:
            if w in words or f" {w} " in f" {text_lower} ":
                return {"intent": "approve", "confidence": 0.7, "entities": {}}
        for phrase in reject_phrases:
            if phrase in text_lower:
                return {"intent": "reject", "confidence": 0.8, "entities": {"reason": text}}
        for w in reject_words:
            if w in words:
                return {"intent": "reject", "confidence": 0.7, "entities": {"reason": text}}
        for w in check_words:
            if w in words:
                return {"intent": "check_orders", "confidence": 0.7, "entities": {}}
        for phrase in new_order_phrases:
            if phrase in text_lower:
                return {"intent": "new_order", "confidence": 0.7, "entities": {}}
        for w in new_order_words:
            if w in words:
                return {"intent": "new_order", "confidence": 0.6, "entities": {}}
        for phrase in human_phrases:
            if phrase in text_lower:
                return {"intent": "speak_human", "confidence": 0.8, "entities": {}}
        for w in human_words:
            if w in words:
                return {"intent": "speak_human", "confidence": 0.7, "entities": {}}

        return {"intent": "other", "confidence": 0.4, "entities": {}}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return {"intent": "other", "confidence": 0.0, "entities": {}}
