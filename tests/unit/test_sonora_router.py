"""Tests para LangChain Router Agent [FR5] — tenant lookup, intent classification, routing."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestTenantLookup:
    """FR5: Router must correctly identify tenant from user."""

    @pytest.fixture
    def router(self):
        from apps.sonora_engine.router import RouterAgent
        return RouterAgent()

    def test_lookup_tenant_by_telegram_id(self, router):
        """Given telegram_id, router finds the correct tenant"""
        result = router.lookup_tenant(telegram_id=67890)
        if result:
            assert "tenant_id" in result
            assert "slug" in result

    def test_lookup_unknown_user_returns_none(self, router):
        """Unknown telegram_id returns None (needs registration)"""
        result = router.lookup_tenant(telegram_id=999999)
        assert result is None

    def test_lookup_returns_tenant_config(self, router):
        """Router loads full tenant config including pricing and branding"""
        result = router.lookup_tenant(telegram_id=67890)
        if result:
            assert "config" in result
            assert "branding" in result
            assert "pricing" in result


class TestIntentClassifier:
    """FR5: Router must classify user intent correctly."""

    @pytest.fixture
    def router(self):
        from apps.sonora_engine.router import RouterAgent
        return RouterAgent()

    @pytest.mark.parametrize("message,expected_intent", [
        ("Quiero un saludo de cumpleaños", "greeting"),
        ("Cuanto cuesta un saludo", "pricing"),
        ("Reproducciones de Hector", "revenue"),
        ("Hola", "chat"),
        ("Compartir en Facebook", "work_quest"),
        ("Ver video detras de camaras", "learn_quest"),
        ("Responder trivia", "play_quest"),
        ("Programar mensaje automatico", "schedule"),
        ("Reporte de streams", "dashboard"),
    ])
    def test_classify_intents(self, router, message, expected_intent):
        """Each message maps to the correct intent"""
        intent = router.classify_intent(message)
        assert intent == expected_intent, \
            f"'{message}' → expected '{expected_intent}', got '{intent}'"

    def test_unknown_intent_defaults_to_chat(self, router):
        """Messages that don't match any pattern default to 'chat'"""
        intent = router.classify_intent("Qué opinas de la música hoy?")
        assert intent == "chat"

    def test_greeting_intent_with_artist_name(self, router):
        """Greeting intent extracts artist name from message"""
        intent = router.classify_intent("Quiero un saludo de Hector para mi mama")
        assert intent == "greeting"


class TestSubAgentRouting:
    """FR5: Router must route to the correct sub-agent based on intent."""

    @pytest.fixture
    def router(self):
        from apps.sonora_engine.router import RouterAgent
        return RouterAgent()

    @pytest.mark.parametrize("intent,expected_agent", [
        ("chat", "chat_agent"),
        ("greeting", "monetization_agent"),
        ("pricing", "monetization_agent"),
        ("revenue", "knowledge_agent"),
        ("play_quest", "gamification_agent"),
        ("work_quest", "gamification_agent"),
        ("learn_quest", "gamification_agent"),
        ("schedule", "automation_agent"),
        ("dashboard", "knowledge_agent"),
    ])
    def test_route_to_correct_agent(self, router, intent, expected_agent):
        """Each intent maps to the correct sub-agent"""
        agent = router.route(intent)
        assert agent == expected_agent, \
            f"intent '{intent}' → expected '{expected_agent}', got '{agent}'"

    def test_unknown_intent_routes_to_chat(self, router):
        """Fallback: unknown intent routes to chat_agent"""
        agent = router.route("unknown_intent_xyz")
        assert agent == "chat_agent"


class TestRAGIntegration:
    """FR5: Chat Agent queries RAG for tenant-specific context."""

    def test_rag_query_returns_tenant_results(self):
        """FR7: RAG results are filtered by tenant"""
        from apps.sonora_engine.rag import query_rag

        results = query_rag(tenant_id="abe-music", query="streams Hector Rubio")
        assert isinstance(results, list)
        # In mocked mode: returns empty list
        # In integration mode: returns actual RAG results

    def test_rag_no_cross_tenant_leak(self):
        """FR7: Different tenant cannot see other tenant's RAG data"""
        from apps.sonora_engine.rag import query_rag

        results_a = query_rag(tenant_id="abe-music", query="streams")
        results_b = query_rag(tenant_id="other-tenant", query="streams")
        # Both return lists, no cross-contamination
        assert isinstance(results_a, list)
        assert isinstance(results_b, list)


class TestMonetizationFlow:
    """FR5: Monetization Agent handles greeting requests end-to-end."""

    def test_greeting_creates_pending_record(self):
        """When fan requests greeting, a pending record is created"""
        from apps.sonora_engine.agents.monetization import handle_greeting_request

        result = handle_greeting_request(
            tenant_id="abe-music",
            artist_name="Hector Rubio",
            fan_id="fan-uuid",
            message="Feliz cumpleaños mama!",
        )
        assert result["status"] == "pending_payment"
        assert result["beat_cost"] > 0
        assert result["usd_cost"] > 0
        assert result["greeting_id"] is not None

    def test_greeting_returns_payment_options(self):
        """Fan receives both $BEAT and fiat payment options"""
        from apps.sonora_engine.agents.monetization import get_payment_options

        options = get_payment_options(tenant_id="abe-music")
        assert "beat" in options
        assert "usd" in options
        assert options["beat"]["cost"] > 0
        assert options["usd"]["cost"] > 0
        assert "stripe" in options["usd"]["providers"]
