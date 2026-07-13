"""LangChain Router Agent [FR5] — tenant lookup, intent classification, sub-agent routing.

Este es el entry point del LangChain engine. Recibe mensajes de la cola
telegram:inbox, identifica el tenant, clasifica el intento, y rutea al
sub-agente correcto.
"""

import logging
from typing import Any

log = logging.getLogger("sonora.engine.router")

INTENT_PATTERNS: dict[str, list[str]] = {
    "pricing": ["cuanto cuesta", "cuanto sale", "precio", "costar", "valor"],
    "greeting": ["mensaje para", "cumpleaños", "felicitar", "saludar", "saludo"],
    "revenue": ["reproduccion", "oyente", "ingreso", "stream", "regalia"],
    "play_quest": ["responder trivia", "jugar trivia", "adivina", "trivia", "juego", "votar"],
    "work_quest": ["compartir", "referir", "invitar", "publicar en"],
    "learn_quest": ["detras de camaras", "aprender", "video detras", "leccion", "curso"],
    "schedule": ["programar mensaje", "agendar", "recordatorio", "automatico", "programar"],
    "dashboard": ["reporte de", "dashboard", "metricas", "panel", "kpi", "estadistica", "reporte"],
}

ROUTING_TABLE = {
    "greeting": "monetization_agent",
    "pricing": "monetization_agent",
    "revenue": "knowledge_agent",
    "play_quest": "gamification_agent",
    "work_quest": "gamification_agent",
    "learn_quest": "gamification_agent",
    "schedule": "automation_agent",
    "dashboard": "knowledge_agent",
    "chat": "chat_agent",
}


class RouterAgent:
    """Routes incoming messages to the correct sub-agent."""

    def lookup_tenant(self, telegram_id: int) -> dict[str, Any] | None:
        """Look up tenant by telegram_id.

        In production: queries telegram_users + tenants via Hasura.
        In test/fallback: returns None (user needs registration).
        """
        try:
            from .hasura import query

            result = query("""
                query GetTenantByTelegram($telegram_id: bigint!) {
                    telegram_users(
                        where: {telegram_id: {_eq: $telegram_id}}
                        limit: 1
                    ) {
                        tenant_id
                        user_id
                        tenant {
                            slug
                            name
                            pricing_config
                            branding
                        }
                    }
                }
            """, {"telegram_id": telegram_id})

            users = result.get("data", {}).get("telegram_users", [])
            if not users:
                return None

            u = users[0]
            tenant = u.get("tenant", {})
            return {
                "tenant_id": u["tenant_id"],
                "user_id": u["user_id"],
                "slug": tenant.get("slug", ""),
                "name": tenant.get("name", ""),
                "pricing": tenant.get("pricing_config", {}),
                "branding": tenant.get("branding", {}),
            }
        except Exception:
            return None  # Fallback for tests / unavailable Hasura

    def classify_intent(self, message: str) -> str:
        """Classify user intent using keyword matching.

        Returns one of: greeting, pricing, revenue, play_quest, work_quest,
                      learn_quest, schedule, dashboard, chat
        """
        msg_lower = message.lower()

        all_patterns = [
            (pattern, intent)
            for intent, patterns in INTENT_PATTERNS.items()
            for pattern in patterns
        ]
        all_patterns.sort(key=lambda x: len(x[0]), reverse=True)

        for pattern, intent in all_patterns:
            if pattern in msg_lower:
                return intent

        return "chat"

    def route(self, intent: str) -> str:
        """Route intent to the correct sub-agent name."""
        return ROUTING_TABLE.get(intent, "chat_agent")

    def process(self, message: str, telegram_id: int) -> dict[str, Any]:
        """Full processing pipeline: lookup → classify → route."""
        tenant_info = self.lookup_tenant(telegram_id)
        intent = self.classify_intent(message)
        agent = self.route(intent)

        return {
            "tenant": tenant_info,
            "intent": intent,
            "agent": agent,
        }
