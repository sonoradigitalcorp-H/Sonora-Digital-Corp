"""
Sistema de Templates de Voz — respuestas dinámicas con variación.
Cada template tiene múltiples variantes para que Mystic no suene robótica.
Las variantes se seleccionan según:
- Contexto de la conversación
- Intención detectada
- Estado de ánimo (tone)
- Número de interacciones previas (para evitar repetición)
"""
import json
import logging
import random
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("voice-realtime.templates")

# ─── Variantes de respuesta por contexto ───

GREETING_TEMPLATES = [
    "¡Hola! Soy Mystic, el alma de Sonora Digital Corp. ¿En qué puedo ayudarte hoy?",
    "¡Qué tal! Mystic al habla. Cuéntame, ¿qué necesitas?",
    "¡Bienvenido! Soy Mystic, tu asistente digital. ¿Cómo te ayudo?",
    "Hola, soy Mystic. Me alegra verte por aquí. ¿Qué traes en mente?",
    "¡Hey! Mystic presente. ¿En qué puedo servirte el día de hoy?",
    "Qué gusto tenerte aquí. Soy Mystic, ¿qué se te ofrece?",
]

SERVICES_TEMPLATES = [
    "Te cuento rápido: en Sonora Digital Corp tenemos {products_count} productos diseñados para impulsar tu negocio. Lo que más piden son nuestros agentes de ventas IA y las soluciones de ciberseguridad. ¿Quieres que te platique de alguno en especial?",
    "Mirá, tenemos de todo: desde agentes IA que venden por ti hasta protección cibernética completa. ¿Qué es lo que más te preocupa ahorita de tu negocio?",
    "¡Claro! Nuestro fuerte son los agentes de voz y WhatsApp que trabajan 24/7, y también tenemos monitoreo de seguridad. ¿Por dónde te gusta empezar?",
    "Tenemos un catálogo bien completo: {products_list}. ¿Hay algo en particular que llame tu atención?",
]

PRICING_TEMPLATES = [
    "Mira, nuestros planes están diseñados para que cualquier negocio pueda empezar. Desde {min_price}/mes el más accesible, hasta paquetes completos. ¿Qué tipo de solución te interesa?",
    "¡Claro que sí! Los precios van desde {min_price} hasta {max_price} MXN al mes, dependiendo del producto. ¿Quieres que te cuente de algún plan en específico?",
    "Tenemos desde {min_price}/mes para soluciones puntuales, hasta paquetes integrales. Lo mejor es que no hay contratos forzosos. ¿Qué presupuesto tienes en mente?",
    "Los precios son accesibles pensando en PYMEs como tú. Déjame preguntarte: ¿qué es exactamente lo que buscas solucionar? Así te recomiendo el plan ideal.",
]

BOOKING_TEMPLATES = [
    "¡Perfecto! Te voy a llevar directo a mi calendario para que agendes en el horario que más te acomode. ¿Listo?",
    "Dame un segundo y te redirijo a la agenda. Ahí puedes escoger el día y la hora que mejor te queden.",
    "Claro, con gusto. Te mando directo al calendario para que apartes tu espacio. ¿Vamos?",
    "¡Hecho! Te llevo a la página de citas para que elijas tu horario ideal.",
]

NAVIGATION_TEMPLATES = [
    "¡Claro! Te llevo ahí mismo. Espérame tantito...",
    "Dame chance y te redirijo. Un momento...",
    "¡Vamos! Te llevo directo. Preparado?",
]

GOODBYE_TEMPLATES = [
    "¡Fue un gusto ayudarte! Cuando necesites algo, aquí estoy. ¡Que tengas excelente día!",
    "Me da gusto que haya sido útil. Si algo más necesitas, ya sabes dónde encontrarme. ¡Cuídate!",
    "¡Con gusto! Siempre a la orden. Chao, que te vaya súper bien.",
    "Un placer como siempre. Cuando quieras, aquí estoy. ¡Éxito!",
]

FOLLOW_UP_TEMPLATES = [
    "¿Hay algo más en lo que pueda ayudarte?",
    "¿Qué más se te ofrece? Aquí estoy para lo que necesites.",
    "¿Alguna otra duda o pregunta?",
    "¿Te ayudo con algo más mientras estás por aquí?",
]

ERROR_TEMPLATES = [
    "Disculpa, no entendí bien. ¿Puedes repetirlo?",
    "Perdona, me falló la conexión. ¿Me dices otra vez?",
    "Uy, no te escuché bien. ¿Repites, porfa?",
    "Lo siento, no alcancé a captar. ¿Puedes decirlo de nuevo?",
]

# ─── Mapa de templates por intención ───

TEMPLATE_MAP = {
    "greeting": GREETING_TEMPLATES,
    "services": SERVICES_TEMPLATES,
    "pricing": PRICING_TEMPLATES,
    "book_appointment": BOOKING_TEMPLATES,
    "request_diagnosis": BOOKING_TEMPLATES,
    "buy_product": PRICING_TEMPLATES,
    "go_pricing": PRICING_TEMPLATES,
    "go_services": SERVICES_TEMPLATES,
    "go_contact": NAVIGATION_TEMPLATES,
    "goodbye": GOODBYE_TEMPLATES,
    "follow_up": FOLLOW_UP_TEMPLATES,
    "error": ERROR_TEMPLATES,
    "general_chat": [],  # Se maneja con LLM
}


class VoiceTemplateEngine:
    """
    Motor de templates con variación.
    Selecciona variantes sin repetir usando historial de uso.
    """

    def __init__(self):
        self._usage_history: dict[str, list[int]] = {}
        self._tone = "warm"  # warm | energetic | calm | professional

    def set_tone(self, tone: str):
        """Cambia el tono general de las respuestas."""
        if tone in ["warm", "energetic", "calm", "professional"]:
            self._tone = tone
            logger.info(f"Voice tone set to: {tone}")

    def get_response(self, intent_id: str, variables: dict = None) -> str:
        """
        Obtiene una respuesta variada para una intención.
        - intent_id: ID de la intención
        - variables: dict para reemplazar en el template {{variable}}
        """
        templates = TEMPLATE_MAP.get(intent_id, ERROR_TEMPLATES)
        if not templates:
            return ""  # Sin template, se usará respuesta del LLM

        # Filtrar variantes usadas recientemente
        history = self._usage_history.get(intent_id, [])
        available = [i for i in range(len(templates)) if i not in history[-3:]]

        if not available:
            available = list(range(len(templates)))
            history = []

        # Seleccionar aleatoriamente entre las disponibles
        idx = random.choice(available)
        template = templates[idx]

        # Actualizar historial
        self._usage_history.setdefault(intent_id, []).append(idx)
        if len(self._usage_history[intent_id]) > 10:
            self._usage_history[intent_id] = self._usage_history[intent_id][-10:]

        # Aplicar variables
        if variables:
            template = self._apply_variables(template, variables)

        return template

    def _apply_variables(self, template: str, variables: dict) -> str:
        """Reemplaza {{variables}} en el template."""
        result = template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def get_greeting(self, user_name: str = None) -> str:
        """Saludo inicial variado."""
        greeting = random.choice(GREETING_TEMPLATES)
        if user_name:
            greeting = greeting.replace("", user_name).replace("cliente", user_name)
        return greeting

    def get_goodbye(self) -> str:
        """Despedida variada."""
        return random.choice(GOODBYE_TEMPLATES)

    def get_follow_up(self) -> str:
        """Pregunta de seguimiento variada."""
        return random.choice(FOLLOW_UP_TEMPLATES)
