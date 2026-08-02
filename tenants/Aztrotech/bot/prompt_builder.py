"""Prompt Builder + Guardrails Anti-Venta — Construye el prompt con contexto completo.

Orden de inyección:
  1. System prompt (anti-venta, educativo, multi-idioma)
  2. Contexto RAG (fuentes del catálogo)
  3. Memoria emerge (perfil cliente + sesión)
  4. Emoción actual (flags)
  5. Clasificación lead (tipo + acción sugerida)
  6. Historial reciente (últimos N turns)
  7. Mensaje del usuario
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# System prompt principal — reemplaza SISTEMA hardcodeado de telegram.py
SYSTEM_PROMPT = """Eres el Asistente Digital de César Holguín y su empresa AstroTech, con sede en Hermosillo, Sonora.

REGLAS ESTRICTAS (NUNCA VIOLAR):
1. NUNCA revelas que formas parte de Sonora Digital Corp. Eres solo el asistente de AstroTech.
2. NUNCA des precios ni cotizaciones. Si preguntan por precio: "Los mejores precios te los doy en una llamada con César, porque cada negocio es diferente. ¿Te parece si le pido que te contacte?"
3. NO suenes a vendedor. Eres un consultor que PRIMERO entiende el negocio del cliente, luego propone. Nunca presiones.
4. PRIORIZA EDUCAR antes que vender: explica CÓMO funciona la tecnología y CÓMO resolvería el problema del cliente.
5. Pregunta para entender el DOLOR real: ¿a qué se dedica, qué problema tiene hoy, qué ha intentado?
6. Escucha y refleja: repite lo que entendiste del negocio del cliente antes de proponer algo.
7. Cuando tengas contexto suficiente, ofrece conectar con César para una llamada personal.
8. Nunca inventes servicios, precios ni características que no estén en el CONTEXTO del catálogo.
9. IMPORTANTE: El CONTEXTO DEL CATÁLOGO puede contener precios internos (como "Desde $299/mes").
   NUNCA reveles esos números al cliente. Si mencionan el contexto de precio, di que César les da la cotización personalizada en llamada.

PERSONALIDAD: Profesional, cálido, consultivo, sin tecnicismos innecesarios.

IDIOMA: Responde SIEMPRE en el idioma del cliente (es, en, pt, fr, etc.). Detecta el idioma del mensaje y responde en ese idioma.

CONTEXTO DEL CATÁLOGO (usa solo esto para hablar de servicios):
{rag_context}

MEMORIA DEL CLIENTE (contexto previo, úsalo para personalizar):
{memoria_context}

SEÑAL EMOCIONAL ACTUAL:
{emotion_context}

CONTEXTO DEL LEAD:
{lead_context}

INSTRUCCIONES DE RESPUESTA:
- Responde de forma natural, como si hablaras con un amigo empresario.
- Después de tu respuesta, incluye OPCIONES CONCRETAS Y ESPECÍFICAS como botones.
- Las opciones deben ser acciones claras, no genéricas. Ejemplos:
  * "Quiero un Empleado Digital para mi negocio" (no "Más info")
  * "César me llama para cotizar" (no "Contactar")
  * "Ver casos de éxito de negocios similares" (no "Casos de éxito")
  * "¿Cuánto tiempo tarda en funcionar?" (no "Pregunta técnica")
- Si el lead es HOT, la opción debe ser "Hablemos ahora, ¿cuándo le cae bien a César?"
- Si el lead es WARM, la opción debe ser "Cuéntame más de tu negocio y te doy un plan"
- Si el lead es COLD, la opción debe ser "¿Qué problema específico quieres resolver?"
- NUNCA uses botones como "Servicios", "Más info", "Contacto", "Siguiente".
- Sé específico: cada botón debe llevar a una acción concreta.
- Si el usuario habla de un problema específico, la siguiente opción debe ser sobre ese problema.
- Si el usuario pregunta por precio, NO des opciones de precio, da la opción de "Hablemos con César para una cotización personalizada".
"""

# Guardrails post-LLM: detecta violaciones
GUARDRAIL_PATTERNS = {
    "precio_revelado": [
        r"\$\s?\d+",
        r"\b\d{3,}\s*(mxn|usd|pesos|dólares|dolares)\b",
        r"\bdesde\s+\$?\d+",
        r"\bcuesta\s+\$?\d+",
        r"\bprecio\s+(de|es)\s+\$?\d+",
    ],
    "revela_sdc": [
        r"\b(sonora digital corp|sonora\s+digital)\b",
        r"\bSDC\b",
    ],
    "tono_agresivo": [
        r"\b(apúrate|compr\w*\s+ya|no\s+lo\s+pienses|solo\s+hoy|oferta\s+por\s+tiempo)\b",
    ],
}


@dataclass
class PromptContext:
    user_message: str
    rag_context: str = ""
    memoria_context: str = ""
    emotion_context: str = ""
    lead_context: str = ""
    history: List[Dict[str, str]] = field(default_factory=list)
    locale: str = "es"
    max_history_turns: int = 8


class PromptBuilder:
    def __init__(self, system_prompt: str = SYSTEM_PROMPT):
        self.system_prompt = system_prompt

    def _format_emotion(self, emotion: Dict[str, Any]) -> str:
        if not emotion:
            return "Sin señal emocional destacada."
        flags = emotion.get("flags", {})
        active = [k.replace("_", " ") for k, v in flags.items() if v]
        dominant = emotion.get("dominant", "neutral")
        return f"Emoción dominante: {dominant}. Señales: {', '.join(active) if active else 'ninguna destacada'}."

    def _format_lead(self, lead: Dict[str, Any]) -> str:
        if not lead:
            return "Lead aún sin clasificar."
        return (
            f"Tipo de lead: {lead.get('tipo', 'unknown').upper()} "
            f"(confianza {lead.get('confianza', 0):.0%}). "
            f"Acción sugerida: {lead.get('proxima_accion', '')}. "
            f"Datos faltantes: {', '.join(lead.get('datos_faltantes', [])) or 'ninguno'}."
        )

    def build(self, ctx: PromptContext) -> List[Dict[str, str]]:
        system = (
            self.system_prompt
            .replace("{rag_context}", ctx.rag_context or "(sin contexto de catálogo)")
            .replace("{memoria_context}", ctx.memoria_context or "(sin memoria previa)")
            .replace("{emotion_context}", self._format_emotion(
                json_loads_safe(ctx.emotion_context) if ctx.emotion_context else {}
            ))
            .replace("{lead_context}", self._format_lead(
                json_loads_safe(ctx.lead_context) if ctx.lead_context else {}
            ))
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": system}]
        # Historial
        for turn in ctx.history[-ctx.max_history_turns:]:
            messages.append(turn)
        messages.append({"role": "user", "content": ctx.user_message})
        return messages

    # ── Guardrails ──────────────────────────────────────────────
    def check_guardrails(self, response: str) -> Dict[str, Any]:
        """Valida la respuesta del LLM contra reglas anti-venta/anti-precio."""
        violations = {}
        t = response.lower()
        for rule, patterns in GUARDRAIL_PATTERNS.items():
            hits = []
            for pat in patterns:
                m = re.search(pat, t)
                if m:
                    hits.append(m.group(0))
            if hits:
                violations[rule] = hits
        return {
            "violations": violations,
            "pass": len(violations) == 0,
            "message": (
                "ok" if not violations else
                f"Guardrail violado: {', '.join(violations.keys())}"
            ),
        }


def json_loads_safe(s: str) -> Dict[str, Any]:
    """Si emotion_context/lead_context viene como JSON string, lo parsea."""
    try:
        import json
        return json.loads(s)
    except Exception:
        return {}


def create_prompt_builder() -> PromptBuilder:
    return PromptBuilder()


if __name__ == "__main__":
    b = create_prompt_builder()
    ctx = PromptContext(
        user_message="¿Cuánto cuesta el empleado digital?",
        rag_context="Empleado Digital: agente IA 24/7 para WhatsApp, Instagram y Facebook.",
        emotion_context=json.dumps({"dominant": "interes_genuino", "flags": {"interested": True}}),
        lead_context=json.dumps({"tipo": "warm", "confianza": 0.9, "proxima_accion": "calificar", "datos_faltantes": []}),
        history=[{"role": "user", "content": "Hola, tengo una tienda de ropa"}],
    )
    msgs = b.build(ctx)
    print("System prompt (primeras 300 chars):")
    print(msgs[0]["content"][:300])
    print(f"\nTotal messages: {len(msgs)}")

    # Test guardrail
    r = b.check_guardrails("Nuestro servicio cuesta $599 al mes")
    print(f"\nGuardrail test: {r}")