"""
Campaign system for AztroTech marketing.
Stores campaigns with product, price, promo data.
Generates Bryan Tracy-style sales prompts for the agent.
"""

import json
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

BASE = Path(__file__).resolve().parent
CAMPAIGNS_FILE = BASE / "campaigns.json"


@dataclass
class Campaign:
    id: str = ""
    name: str = ""
    product: str = ""
    price: str = ""
    promo: str = ""
    target_audience: str = ""
    key_benefits: list[str] = None
    objections: list[str] = None
    call_to_action: str = ""
    active: bool = True
    created_at: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = f"CAMP-{int(time.time())}"
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if self.key_benefits is None:
            self.key_benefits = []
        if self.objections is None:
            self.objections = []

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Campaign":
        return cls(**data)


BRYAN_TRACY_SYSTEM = """
Eres un vendedor entrenado en la metodologia de Brian Tracy (Seminario Fenis).

ESTRUCTURA DE LLAMADA:
1. APERTURA (5s) — "Hola [nombre], soy [agente] de AztroTech. Te marco porque..."
2. PROPOSICION DE VALOR (15s) — Una frase que conecta su dolor con tu solucion
3. SONDAJE (30s) — Preguntas para descubrir necesidad real
4. PRESENTACION (20s) — Solucion ajustada a lo que dijo
5. MANEJO DE OBJECIONES — 5 pasos:
   1. ESCUCHA COMPLETAMENTE — No interrumpas
   2. PAUSA 3 SEGUNDOS — Silencio estrategico
   3. VALIDA + PREGUNTA — "Buena pregunta... ¿a que te refieres exactamente?"
   4. RESPONDE — Feel → Felt → Found:
      - FEEL: "Entiendo, con los margenes es una decision importante..."
      - FELT: "[Cliente similar] pensaba igual antes de implementarlo"
      - FOUND: "Lo que descubrieron fue que aumentaron su capacidad 3x"
   5. CONFIRMA + CIERRA — "¿Eso responde tu inquietud? ¿Que tal si agendamos?"
6. CIERRE (10s) — Proximo paso concreto: llamada, demo, propuesta

REGLAS:
- Si la objecion persiste tras 3 intentos: salida educada con puerta abierta
- Nunca inventes precios o promos que no esten en la campana
- La objecion no es un rechazo, es una peticion de mas informacion
"""


def generate_prompt(campaign: Campaign) -> str:
    benefits = "\n".join(f"  - {b}" for b in campaign.key_benefits)
    objections = "\n".join(f"  - {o}" for o in campaign.objections)

    return f"""{BRYAN_TRACY_SYSTEM}

CAMPANA ACTIVA:
- Nombre: {campaign.name}
- Producto: {campaign.product}
- Precio: {campaign.price}
- Promocion: {campaign.promo}
- Audiiencia: {campaign.target_audience}

BENEFICIOS CLAVE:
{benefits}

OBJECIONES COMUNES:
{objections}

LLAMADA DE ACCION: {campaign.call_to_action}

IMPORTANTE: Usa SOLO la informacion de esta campana. No inventes precios ni promos adicionales.
Si el prospecto pregunta algo fuera de campana, dile que lo revisas y le confirmas.
"""


DEFAULT_CAMPAIGNS = [
    Campaign(
        name="Diagnostico Gratuito Q3",
        product="Diagnostico de IA Empresarial",
        price="Gratuito (valor $5,000 MXN)",
        promo="Diagnostico gratuito de 30 minutos + reporte personalizado",
        target_audience="Duenos de PYMES en Sonora que quieren automatizar ventas",
        key_benefits=[
            "Descubre exactamente donde tu negocio pierde ventas",
            "Te llevamos un reporte con oportunidades de automatizacion",
            "Sin compromiso, sin presion, solo valor real",
        ],
        objections=[
            "No tengo tiempo ahorita",
            "Ya tengo quien me ayuda con eso",
            "La IA no es para mi negocio",
            "Es muy caro",
            "Lo voy a pensar",
        ],
        call_to_action="Agendar diagnostico gratuito de 30 minutos",
    ),
    Campaign(
        name="Empleado Digital - Lanzamiento",
        product="Empleado Digital Pilot",
        price="$15,000 MXN setup + $2,500 MXN/mes",
        promo="Primer mes gratis en setup si contratas antes del 15 de agosto",
        target_audience="Negocios con 10-50 prospectos al mes",
        key_benefits=[
            "Un agente IA que vende por ti 24/7 en WhatsApp, Instagram y Facebook",
            "Califica leads, da seguimiento y agenda citas automaticamente",
            "Entrega en 48-72 horas, sin que sepas programar",
        ],
        objections=[
            "Ya tengo un chatbot",
            "Mis clientes prefieren hablarme directo",
            "No tengo presupuesto ahorita",
            "Como se que va a funcionar?",
        ],
        call_to_action="Agendar demo personalizada de 15 minutos",
    ),
]
