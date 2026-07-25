"""
Router de intenciones por voz.
Clasifica lo que el usuario pide y lo enruta al destino correcto:
- Calendario / Booking / Cita
- Navegación / Ir a algún lado
- Compra / Cotización
- Información general
"""
import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger("voice-realtime.intent_router")

# ─── Intenciones del sistema ───

@dataclass
class Intent:
    """Intención clasificada con acción asociada."""
    id: str
    name: str
    description: str
    confidence: float = 0.0
    action: Optional[dict] = None
    entities: dict = field(default_factory=dict)

@dataclass
class RoutedAction:
    """Acción resultante del ruteo de intención."""
    type: str  # "navigate" | "book" | "buy" | "info" | "talk"
    destination: Optional[str] = None  # URL, ruta, nombre
    payload: dict = field(default_factory=dict)
    response_override: Optional[str] = None  # Respuesta personalizada si aplica
    redirect_url: Optional[str] = None  # URL para redirigir al usuario


# ─── Mapa de patrones de intención ───
# ORDENADO por especificidad (más específico primero)

INTENT_PATTERNS = [
    # ── Booking / Citas ──
    {
        "id": "book_appointment",
        "name": "Agendar cita",
        "description": "El usuario quiere agendar una cita, llamada o reunión",
        "patterns": [
            r"\b(agend|program[ae]|reserv[ae]|separ[ae]|apart[ae])\s.*(cita|reuni[oó]n|llamada|meet|call|appointment|diagn[oó]stico)",
            r"\b(quiero|necesito|puedo)\s.*(agend|program|reserv|separ|apart)",
            r"\b(habl[ae]r\s*con|contactar|comunicar)\s*(un\s*experto|con\s*alguien|con\s*un\s*asesor)",
            r"\b(quiero|me\s*gustar[íi]a)\s*(hablar|platicar|conversar)\s*(con|sobre)",
        ],
        "action": {"type": "navigate", "destination": "booking"},
        "response": "¡Claro! Te voy a llevar directo a mi calendario para que agendes la cita en el horario que más te acomode.",
    },
    # ── Diagnóstico ──
    {
        "id": "request_diagnosis",
        "name": "Solicitar diagnóstico",
        "description": "El usuario quiere un diagnóstico o auditoría",
        "patterns": [
            r"\b(diagn[oó]stic|auditor[íi]a|revis[ió]n|an[aá]lisis)\b",
            r"\b(quiero|necesito|puedo)\s.*(diagn[oó]stic|auditor|revis[ió]n)",
            r"\b(chec[ae]r|revis[ae]r|analiz[ae]r)\s.*(negocio|empresa|sistema|seguridad)",
        ],
        "action": {"type": "navigate", "destination": "diagnosis"},
        "response": "Te voy a llevar a nuestro diagnóstico express. En minutos sabes exactamente qué necesita tu negocio.",
    },
    # ── Comprar / Cotizar ──
    {
        "id": "buy_product",
        "name": "Comprar producto",
        "description": "El usuario quiere comprar un producto o saber precios",
        "patterns": [
            r"\b(quiero|necesito|me\s*interesa)\s*(compr[ae]r|adquirir|contrat[ae]r|pagar)",
            r"\b(cu[áa]nto\s*(cuest[ae]n?|salen?|valen?|cobran)|cu[áa]l\ses\s*el\s*precio|precios|presupuesto|planes|paquetes|cotizaci[oó]n)\b",
            r"\b(me\s*interesa)\s*(el|la|los|las)\s*(plan|paquete|servicio|producto)",
        ],
        "action": {"type": "navigate", "destination": "pricing"},
        "response": "Te llevo directo a nuestros planes y precios para que elijas el que mejor se ajuste a ti.",
    },
    # ── Navegación a secciones ──
    {
        "id": "go_pricing",
        "name": "Ver precios",
        "description": "El usuario quiere ver planes y precios",
        "patterns": [
            r"\b(ver|mostr[ae]r|enseñ[ae]r|quiero\s*ver)\s*(plan|precio|costo|paquete|precios|planes)",
            r"\b(cu[áa]nto\s*(cuest[ae]n?|salen|valen)|precios|planes|paquetes)\b",
        ],
        "action": {"type": "navigate", "destination": "pricing"},
    },
    {
        "id": "go_services",
        "name": "Ver servicios",
        "description": "El usuario quiere ver los servicios disponibles",
        "patterns": [
            r"\b(qu[eé]\s*servicios|qu[eé]\s*hacen|qu[eé]\s*ofrecen|servicios disponibles|qu[eé]\s*tienen)\b",
            r"\b(ver|mostr[ae]r)\s*(servicios|productos|cat[aá]logo)",
        ],
        "action": {"type": "navigate", "destination": "services"},
    },
    {
        "id": "go_contact",
        "name": "Contacto",
        "description": "El usuario quiere contactar a un humano",
        "patterns": [
            r"\b(habl[ae]r\s*con\s*un\s*humano|atenci[oó]n\s*humana|con\s*un\s*asesor|con\s*alguien\s*real)\b",
            r"\b(contacto|tel[eé]fono|correo|email|whatsapp|ubicaci[oó]n|direcci[oó]n)\b",
            r"\b(contactarl[oó]s|contactart[ée]|comunicarm[ée]|escribirles)\b",
            r"\b(quiero|necesito|c[oó]mo\s*puedo)\s*(hablar|platicar|contactar|comunicar)\s*(con|con\s*un)\s*(persona|humano|asesor|experto|ustedes)",
        ],
        "action": {"type": "navigate", "destination": "contact"},
    },
    # ── Productos específicos ──
    {
        "id": "product_ssl",
        "name": "SSL Guardian",
        "description": "El usuario pregunta por SSL Guardian",
        "patterns": [
            r"\b(ssl|ssl\s*guardian|certificado\s*ssl|seguridad\s*web)\b",
        ],
        "action": {"type": "buy", "destination": "ssl-guardian"},
    },
    {
        "id": "product_whatsapp",
        "name": "WhatsApp Agent",
        "description": "El usuario pregunta por WhatsApp Agent Mini",
        "patterns": [
            r"\b(whatsapp|whatsapp\s*agent|bot\s*whatsapp|wa\s*bot)\b",
        ],
        "action": {"type": "buy", "destination": "whatsapp-agent"},
    },
    # ── System Status ──
    {
        "id": "check_system",
        "name": "Estado del sistema",
        "description": "El usuario pregunta cómo está el servidor o sistema",
        "patterns": [
            r"\b(c[oó]mo\s*est[áa]\s*(el\s*)?(sistema|servidor|vps|server))\b",
            r"\b(estado\s*(del\s*)?(sistema|servidor))\b",
            r"\b(qu[eé]\s*tal\s*(est[áa]\s*)?(el\s*)?(sistema|servidor))\b",
            r"\b(monitor|monitoreo|monitorea)\s*(del\s*)?(sistema|servidor)?\b",
            r"\b(revisa|checa|verifica)\s*(el\s*)?(sistema|servidor|estado)\b",
            r"\b(c[oó]mo\s*vamos|qu[eé]\s*hay|qu[eé]\s*cuentas)\s*(del\s*)?(sistema|servidor)?\b",
        ],
        "action": {"type": "system", "destination": "status"},
    },
    # ── Conversación general (fallback) ──
    {
        "id": "general_chat",
        "name": "Conversación general",
        "description": "El usuario quiere conversar sin intención específica",
        "patterns": [],  # Fallback por defecto
        "action": {"type": "talk", "destination": "chat"},
    },
]


class IntentRouter:
    """
    Clasifica intenciones de voz y las enruta a acciones.
    Usa patrones regex primero, luego LLM para casos complejos.
    """

    def __init__(self, use_llm_fallback: bool = True):
        self.use_llm_fallback = use_llm_fallback
        # Compilar patrones
        self._compiled = []
        for intent in INTENT_PATTERNS:
            if intent["patterns"]:
                compiled = [
                    re.compile(p, re.IGNORECASE | re.UNICODE)
                    for p in intent["patterns"]
                ]
                self._compiled.append((intent, compiled))
        logger.info(f"IntentRouter initialized with {len(INTENT_PATTERNS)} intents")

    def classify_regex(self, text: str) -> Intent:
        """
        Clasifica intención usando patrones regex.
        Returns la intención con mayor confianza.
        """
        best_intent = None
        best_score = 0

        for intent_def, patterns in self._compiled:
            score = 0
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    score += 1.0
                    # Keywords matched
                    score += len(match.group()) / len(text) if len(text) > 0 else 0

            if score > best_score:
                best_score = score
                action = intent_def.get("action", {})
                # Extraer URL o query de búsqueda
                entities = {
                    "response": intent_def.get("response", ""),
                    "redirect_url": self._get_redirect_url(action),
                }
                if intent_def["id"] == "browse_web":
                    url = self._extract_url(text)
                    if url:
                        action["destination"] = url
                        entities["url"] = url
                elif intent_def["id"] == "search_web":
                    query = self._extract_search_query(text)
                    if query:
                        action["destination"] = query
                        entities["query"] = query
                
                best_intent = Intent(
                    id=intent_def["id"],
                    name=intent_def["name"],
                    description=intent_def["description"],
                    confidence=min(score / 3.0, 1.0),
                    action=action,
                    entities=entities,
                )

        return best_intent or self._fallback()

    def classify_with_llm(self, text: str, conversation_history: list = None) -> Intent:
        """
        Clasifica intención usando LLM como respaldo.
        Útil cuando regex no da suficiente confianza (<70%).
        """
        from src.core.mem_sabe import MemSabe
        # Usar mem_sabe para análisis semántico
        context = {
            "text": text,
            "task": "intent_classification",
            "available_intents": [i["id"] for i in INTENT_PATTERNS],
        }
        try:
            sabe = MemSabe()
            result = sabe.sabe(text, context)
            intent_id = result.get("intent", "general_chat")
            confidence = result.get("confidence", 0.5)
            # Buscar el intent_def
            for intent_def in INTENT_PATTERNS:
                if intent_def["id"] == intent_id:
                    action = intent_def.get("action", {})
                    return Intent(
                        id=intent_id,
                        name=intent_def["name"],
                        description=intent_def.get("description", ""),
                        confidence=confidence,
                        action=action,
                        entities={"response": intent_def.get("response", ""), "llm_analysis": result},
                    )
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")

        return self._fallback()

    def route(self, text: str, conversation_history: list = None) -> RoutedAction:
        """
        Clasifica y enruta el texto de voz a una acción.
        Pipeline: regex → (si baja confianza) LLM → acción.
        """
        # Paso 1: Regex rápido
        intent = self.classify_regex(text)

        # Paso 2: Si confianza baja, usar LLM
        if intent.confidence < 0.5 and self.use_llm_fallback:
            intent = self.classify_with_llm(text, conversation_history)

        # Paso 3: Construir acción
        action = intent.action or {"type": "talk", "destination": "chat"}
        route = RoutedAction(
            type=action.get("type", "talk"),
            destination=action.get("destination", "chat"),
            payload={
                "intent_id": intent.id,
                "intent_name": intent.name,
                "confidence": intent.confidence,
                "entities": intent.entities,
            },
            response_override=intent.entities.get("response"),
            redirect_url=intent.entities.get("redirect_url"),
        )

        logger.info(f"Route: '{text[:50]}...' → {route.type}/{route.destination} (conf={intent.confidence:.2f})")
        return route

    def _extract_url(self, text: str) -> Optional[str]:
        """Extrae una URL del texto del usuario."""
        # URL completa
        url_match = re.search(r'https?://[\w\-./%?#&=]+', text)
        if url_match:
            return url_match.group(0)
        # Dominio simple (ej: "google.com", "sonoradigitalcorp.com")
        domain_match = re.search(r'(?:a|visitar|entrar|navegar)\s+(?:en\s+)?(https?://)?([\w\-]+\.[\w\-]+(?:\.[\w\-]+)?)', text, re.IGNORECASE)
        if domain_match:
            return "https://" + domain_match.group(2)
        # Detectar dominio suelto
        domain_only = re.search(r'\b([\w\-]+\.(com|mx|org|net|io|app|dev|ai)(?:\/[\w\-./%?#&=]*)?)\b', text)
        if domain_only:
            url = domain_only.group(0)
            if not url.startswith("http"):
                url = "https://" + url
            return url
        return None

    def _extract_search_query(self, text: str) -> Optional[str]:
        """Extrae la consulta de búsqueda del texto del usuario."""
        # "busca X", "investiga sobre X", "dime sobre X", etc.
        patterns = [
            r'(?:busca|investiga|consulta|googlea|google|bing|averigua|encuentra)\s+(?:en\s+)?(?:internet|web|google|bing)?\s*(.+?)(?:\?|$)',
            r'(?:dime|cuéntame|explícame|cuenta|diga)\s+(?:sobre|acerca|de)\s+(.+?)(?:\?|$)',
            r'(?:quiero|quisiera|necesito)\s+(?:saber|encontrar|buscar|investigar)\s+(?:sobre|acerca|información\s+de|de)\s+(.+?)(?:\?|$)',
            r'qué\s+(?:hay|sabes|conoces)\s+(?:de|sobre|acerca)\s+(.+?)(?:\?|$)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                query = m.group(1).strip()
                if len(query) > 2:
                    return query
        # Fallback: si no hay patrón de búsqueda pero el intent es search, usar todo el texto
        return text.strip()[:100] if len(text.strip()) > 5 else None

    def _get_redirect_url(self, action: dict) -> Optional[str]:
        """Obtiene URL de redirección para una acción."""
        urls = {
            "booking": "https://calendario.sonoradigitalcorp.com",
            "diagnosis": "/diagnostico",
            "pricing": "/#pricing",
            "services": "/#features",
            "contact": "https://wa.me/526621072254",
            "ssl-guardian": "/productos/ssl-guardian",
            "whatsapp-agent": "/productos/whatsapp-agent",
        }
        return urls.get(action.get("destination"))

    def _fallback(self) -> Intent:
        """Intención por defecto cuando no hay match."""
        return Intent(
            id="general_chat",
            name="Conversación general",
            description="El usuario quiere conversar",
            confidence=1.0,
            action={"type": "talk", "destination": "chat"},
            entities={"response": None},
        )