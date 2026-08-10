"""Conversation Analyzer — Extrae insights de conversaciones para el CRM.

Calcula engagement_score, detecta servicios requeridos, intención de cita,
y genera resúmenes para reportes de audio.

Usage:
    from analysis_engine import ConversationAnalyzer
    analyzer = ConversationAnalyzer()
    score = analyzer.score_engagement(messages)
    services = analyzer.extract_services(messages)
    cita = analyzer.detect_cita_intent(messages)
    summary = await analyzer.summarize(messages)
"""
import json
import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# ── Service keywords from Aztrotech OKF ─────────────────────────
SERVICIOS_PATTERNS = {
    "Empleado Digital": [
        r"\b(empleado\s+digital|agente\s+ia|agente\s+whatsapp|chatbot|whatsapp\s+ia|automatizaci\w+)",
    ],
    "Sistema de Ventas Autónomo": [
        r"\b(sistema\s+de\s+ventas|crm|automatizaci\w+\s+ventas|ventas\s+autonomo|sales\s+automation)",
    ],
    "Desarrollo de Software": [
        r"\b(software|app|erp|aplicaci\w+|desarrollo\s+web|api|webapp|platforma)",
    ],
    "Empresa 90 Días": [
        r"\b(empresa\s+90\s+d\w+|mentori\W|90\s+dias|ceo\s+mentor)",
    ],
    "Socio Estratégico": [
        r"\b(socio|relation\s+long|socio\s+estrategico|joint\s+venture)",
    ],
}

# ── Cita intent patterns ─────────────────────────────────────────
CITA_PATTERNS = [
    r"\b(agendar|agendar|llamada|llamamos|cita|reuni�n|visita|tengo\s+disponibilidad)",
    r"\b(lunes|martes|mi�rcoles|jueves|viernes|ma�ana|pr�ximos\s+d�as|esta\s+semana|esta\s+semana)",
    r"\b(WhatsApp|tel�fono|celular|cuando\s+puedo)",
]

# ── Engagement signals ───────────────────────────────────────────
ENGAGEMENT_SIGNALS = {
    # Positive engagement
    "respuesta_rapida": 10,
    "pregunta_especifica": 15,
    "menciona_negocio": 12,
    "menciona_presupuesto": 15,
    "intencionalidad": 10,
    "emoji_positivo": 8,
    "confirmacion": 8,

    # Negative engagement
    "no_interes": -15,
    "reenvio": -8,
    "despedida_instantanea": -20,
    "precio_solo": -10,
}

NEGATIVE_PATTERNS = [
    r"\b(no\s+gracias|no\s+interesa|no\s+necesito|pass|gracias\s+pero|ya\s+lo\s+tengo)",
    r"\b(no\s+quiero|solo\s+consulto|voy\s+a\s+ver|despu�s\s+lo\s+veo)",
]

QUICK_RESPONSE_THRESHOLD_SECONDS = 120


@dataclass
class EngagementResult:
    score: float  # 0.0 to 1.0
    signals: List[str] = field(default_factory=list)
    turn_count: int = 0
    total_tokens: int = 0


@dataclass
class ServiceExtraction:
    servicios: List[str]
    confidence: float  # 0.0 to 1.0


@dataclass
class CitaIntent:
    has_cita: bool
    tipo: Optional[str]  # llamada, visita_oficina, visita_negocio
    fecha_mention: Optional[str]


class ConversationAnalyzer:
    """Analyze conversations for engagement, services, cita intent."""

    def __init__(self):
        self.service_patterns = SERVICIOS_PATTERNS

    def score_engagement(
        self,
        messages: List[Dict[str, Any]],
        timestamps: Optional[List[datetime]] = None,
    ) -> EngagementResult:
        """Calcula engagement_score 0-1 basado en interacción.

        Factores:
        - Conversación larga (turns) = 0.3 peso
        - Mensajes específicos (preguntas, business mention) = 0.25 peso
        - Velocidad de respuesta = 0.15 peso
        - Intencionalidad (precio, budget) = 0.3 peso
        """
        if not messages:
            return EngagementResult(score=0.0, turn_count=0)

        signals = []
        raw_score = 0.0
        turn_count = len(messages)
        total_tokens = sum(m.get("tokens_in", 0) + m.get("tokens_out", 0) for m in messages)

        # User messages only
        user_msgs = [m for m in messages if m.get("role") == "user"]
        user_texts = [m.get("content", "") for m in user_msgs]

        # Factor 1: Conversation length (0-30 points)
        length_score = min(30, turn_count * 2.5)
        if turn_count >= 4:
            signals.append("conversación_activa")
        if turn_count >= 8:
            signals.append("alta_participación")

        # Factor 2: Engagement signals in user messages (0-25 points)
        eng_text = " ".join(user_texts).lower()
        if re.search(r"\b(me\s+interesa|quisiera|cotizar|quiero\s+saber|comparar)\b", eng_text):
            raw_score += 15
            signals.append("interés_expresado")
        if re.search(r"\b(tengo\s+una|tengo\s+un|mi\s+negocio|mi\s+empresa|dueno\s+de)\b", eng_text):
            raw_score += 12
            signals.append("menciona_negocio")
        if re.search(r"\b(presupuesto|budget|\$\d|precio|cuanto\s+cuesta|cotizaci\w+)\b", eng_text):
            raw_score += 15
            signals.append("presupuesto_mencionado")
        if any(emoji in eng_text for emoji in ["😊", "👍", "🙂", "✅", "💪"]):
            raw_score += 8
            signals.append("emoji_positivo")
        if re.search(r"\b(si|claro|sí|perfecto|genial|ok|dale)\b", eng_text):
            raw_score += 8
            signals.append("confirmacion")
        if re.search(r"\b(llamada|agendar|cita|reuni�n|visita)\b", eng_text):
            raw_score += 10
            signals.append("acci�n_positiva")
        if re.search(r"\b(urgente|ya|inmediato|asap|ahora)", eng_text):
            raw_score += 8
            signals.append("urgencia")

        # Negative signals
        if any(re.search(pat, eng_text) for pat in NEGATIVE_PATTERNS):
            raw_score -= 15
            signals.append("no_interes")

        # Factor 3: Speed of response (0-15 points)
        if timestamps and len(timestamps) >= 2:
            user_times = [t for i, t in enumerate(timestamps) if messages[i].get("role") == "user"]
            if len(user_times) >= 2:
                gaps = [(user_times[i+1] - user_times[i]).total_seconds() for i in range(len(user_times)-1)]
                avg_gap = sum(gaps) / len(gaps) if gaps else 999
                if avg_gap < 30:
                    raw_score += 15
                    signals.append("respuesta_rapida")
                elif avg_gap < 120:
                    raw_score += 10
                    signals.append("respuesta_normal")
                else:
                    raw_score += 5
                    signals.append("respuesta_lenta")

        # Factor 4: Intencionalidad / intent to buy (0-30 points)
        intent_text = " ".join(user_texts).lower()
        if re.search(r"\b(contratar|comprar|empezar|listo|firmar|aprobado)\b", intent_text):
            raw_score += 30
            signals.append("intencionalidad_fuerte")
        elif re.search(r"\b(agendar|cita|llamada|visita|hablar\s+con)", intent_text):
            raw_score += 20
            signals.append("intencionalidad_media")

        # Normalize to 0-1 (max possible ~100 points)
        normalized = min(1.0, max(0.0, raw_score / 100.0))

        # Blend with length score
        length_component = min(1.0, length_score / 30.0) * 0.2
        final_score = normalized * 0.8 + length_component

        return EngagementResult(
            score=round(final_score, 3),
            signals=signals,
            turn_count=turn_count,
            total_tokens=total_tokens,
        )

    def extract_services(self, texts: List[str]) -> ServiceExtraction:
        """Extrae servicios requeridos de textos de conversación."""
        full_text = " ".join(texts).lower()
        found = []
        for service, patterns in self.service_patterns.items():
            for pat in patterns:
                if re.search(pat, full_text):
                    found.append(service)
                    break
        confidence = min(1.0, len(found) * 0.4 + 0.2)
        return ServiceExtraction(servicios=found, confidence=round(confidence, 2))

    def detect_cita_intent(self, texts: List[str]) -> CitaIntent:
        """Detecta intento de agendar cita/reunión."""
        full_text = " ".join(texts).lower()

        tipo = None
        if re.search(r"\b(llamada|llamar|video\s*llamada)\b", full_text):
            tipo = "llamada"
        elif re.search(r"\b(visita\s+a\s+oficina|oficina|sucursal|local)", full_text):
            tipo = "visita_oficina"
        elif re.search(r"\b(visita\s+al\s+negocio|visitar\s+mi|negocio|casa)", full_text):
            tipo = "visita_negocio"

        fecha_mention = None
        fecha_match = re.search(
            r"\b(lunes|martes|mi�rcoles|jueves|viernes|s�bado|domingo|"
            r"ma�ana|pasado\s+ma�ana|pr�xim(?:o|a)\s+semana|esta\s+semana|"
            r"\d{1,2}/\d{1,2}/\d{2,4})\b",
            full_text,
        )
        if fecha_match:
            fecha_mention = fecha_match.group(0)

        has_cita = bool(fecha_mention or tipo)
        if not has_cita:
            for pat in CITA_PATTERNS:
                if re.search(pat, full_text):
                    has_cita = True
                    break

        return CitaIntent(has_cita=has_cita, tipo=tipo, fecha_mention=fecha_mention)

    def generate_survey_trigger(self, lead_type: str, engagement_score: float) -> bool:
        """Determina si se debe enviar encuesta post-conversación.

        Envía encuesta cuando:
        - Lead type es cold o warm (no hot — hot leads ya están calificados)
        - Engagement score < 0.8 (no terminó la conversación de golpe)
        """
        if lead_type == "hot" and engagement_score > 0.6:
            return False  # Hot lead already qualified, skip survey
        if engagement_score < 0.15:
            return False  # Bot no respondió / conversación trivial
        return True

    async def summarize(
        self,
        conversation_id: str,
        messages: List[Dict[str, Any]],
        llm_call=None,
    ) -> str:
        """Genera resumen narrativo de conversación para reporte de audio.

        Si llm_call disponible, usa LLM. Si no, usa extractiva heurística.
        """
        if not messages:
            return "Sin mensajes en esta conversación."

        full_text = "\n".join(
            f"[{'Usuario' if m.get('role') == 'user' else 'Bot'}] {m.get('content', '')}"
            for m in messages
        )

        if llm_call and len(full_text) > 200:
            try:
                prompt = [
                    {"role": "system", "content": (
                        "Eres un analista de CRM. Resume esta conversación en 5-7 líneas "
                        "para César, el CEO. Incluye: pain points del cliente, servicio "
                        "de interés, nivel de intención (cold/warm/hot), próximos pasos. "
                        "Sé conciso, lenguaje español. NO reveles que eres una IA."
                    )},
                    {"role": "user", "content": full_text[:3000]},
                ]
                result = await llm_call(prompt)
                summary = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                if summary:
                    return summary.strip()
            except Exception as e:
                logger.warning(f"LLM summary falló: {e}")

        # Fallback: extractive
        user_texts = [m.get("content", "") for m in messages if m.get("role") == "user"]
        pain_keywords = ["problema", "dificultad", "lento", "pierdo", "no funciona", "costoso"]
        pain_points = [t for t in user_texts if any(kw in t.lower() for kw in pain_keywords)]

        return (
            f"Conversación de {len(messages)} mensajes. "
            f"Pain points: {'; '.join(pain_points[:2]) if pain_points else 'No identificados'}. "
            f"Servicios mencionados: {', '.join(self.extract_services(user_texts).servicios) or 'Ninguno'}."
        )


def create_analyzer() -> ConversationAnalyzer:
    return ConversationAnalyzer()
