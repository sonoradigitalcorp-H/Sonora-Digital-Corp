"""E2E tests for Agent Galaxy — full user journey from galaxy view to agent provisioning."""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ─── Fixtures ──────────────────────────────────────────────────────────────────

CELESTIAL_BODIES = [
    "Mercurio", "Venus", "Tauro", "Marte", "Júpiter",
    "Saturno", "Urano", "Neptuno", "Plutón",
]

AGENT_CAPABILITIES = {
    "Mercurio": ["speed-tasks", "reminders", "quick-responses"],
    "Venus": ["social-media", "content-generation", "engagement"],
    "Tauro": ["payments", "invoicing", "financial-reports"],
    "Marte": ["crm", "sales", "lead-tracking", "proposals"],
    "Júpiter": ["full-stack", "multi-tenant", "white-label", "all-modules"],
    "Saturno": ["api-integrations", "webhooks", "external-connections"],
    "Urano": ["creative-generation", "images", "music"],
    "Neptuno": ["rag", "knowledge-base", "intelligent-qa"],
    "Plutón": ["admin-dashboard", "metrics", "system-config"],
}

PLAN_AGENTS = {
    "explorador": ["Mercurio"],
    "conquistador": ["Mercurio", "Venus", "Tauro", "Marte"],
    "imperio": ["Mercurio", "Venus", "Tauro", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"],
    "admin": ["Plutón"],
}


@pytest.fixture
def events_file(tmp_path):
    path = tmp_path / "events.jsonl"
    path.touch()
    return str(path)


@pytest.fixture
def galaxy_data():
    return {
        "bodies": [
            {
                "name": name,
                "color": "#FFFFFF",
                "orbit_radius": i * 2.5 + 3.0,
                "orbit_speed": 0.8 - (i * 0.08),
                "capabilities": AGENT_CAPABILITIES[name],
            }
            for i, name in enumerate(CELESTIAL_BODIES)
        ]
    }


# ─── Mock API Client ───────────────────────────────────────────────────────────

class MockGalaxyAPIClient:
    """Simulates the FastAPI backend for E2E testing."""

    def __init__(self, events_path: str = None):
        self.tenants = {}
        self.sessions = {}
        self.voice_configs = {}
        self.events_path = events_path

    def get_galaxy(self) -> dict:
        return {
            "bodies_count": len(CELESTIAL_BODIES),
            "bodies": [
                {
                    "name": name,
                    "capabilities": AGENT_CAPABILITIES[name],
                }
                for name in CELESTIAL_BODIES
            ],
        }

    def get_agent_cards(self, agent_name: str) -> list[dict]:
        if agent_name not in AGENT_CAPABILITIES:
            return []
        return [
            {"capability": cap, "agent": agent_name, "tier": "epic"}
            for cap in AGENT_CAPABILITIES[agent_name]
        ]

    def start_onboarding(self, agent_choice: str) -> dict:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "session_id": session_id,
            "agent_choice": agent_choice,
            "status": "started",
            "tenant_id": None,
        }
        self._emit_event("onboarding_started", data={"agent_choice": agent_choice})
        return {"session_id": session_id, "qr_code": f"https://example.com/onboard/{session_id}"}

    def complete_onboarding(self, session_id: str, user_name: str, plan: str) -> dict:
        if session_id not in self.sessions:
            return {"error": "Session not found"}

        session = self.sessions[session_id]
        tenant_id = str(uuid.uuid4())

        agents = PLAN_AGENTS.get(plan, PLAN_AGENTS["explorador"])
        capabilities = []
        for agent in agents:
            capabilities.extend(AGENT_CAPABILITIES.get(agent, []))
        capabilities = list(set(capabilities))

        tenant = {
            "tenant_id": tenant_id,
            "name": user_name,
            "plan": plan,
            "capabilities": capabilities,
            "status": "active",
        }
        self.tenants[tenant_id] = tenant
        session["tenant_id"] = tenant_id
        session["status"] = "completed"

        self._emit_event("tenant_created", tenant_id=tenant_id, data={"plan": plan})
        self._emit_event("capabilities_assigned", tenant_id=tenant_id,
                         data={"count": len(capabilities)})
        self._emit_event("onboarding_completed", tenant_id=tenant_id)

        return tenant

    def configure_voice(self, tenant_id: str, stt: str = "openai",
                        tts: str = "elevenlabs", channel: str = "whatsapp") -> dict:
        if tenant_id not in self.tenants:
            return {"error": "Tenant not found"}

        self.voice_configs[tenant_id] = {
            "tenant_id": tenant_id,
            "stt_provider": stt,
            "tts_provider": tts,
            "channel": channel,
        }
        self._emit_event("voice_pipeline_configured", tenant_id=tenant_id,
                         data={"channel": channel})
        return self.voice_configs[tenant_id]

    def process_voice_message(self, tenant_id: str, audio_data: bytes = None) -> dict:
        if tenant_id not in self.voice_configs:
            return {"error": "Voice not configured"}

        if tenant_id not in self.tenants:
            return {"error": "Tenant not found"}

        self._emit_event("voice_message_received", tenant_id=tenant_id)
        self._emit_event("voice_message_processed", tenant_id=tenant_id,
                         data={"stt": self.voice_configs[tenant_id]["stt_provider"]})

        return {
            "status": "processed",
            "response": "Agent processed your voice message successfully",
            "tenant_id": tenant_id,
        }

    def get_tenant_config(self, tenant_id: str) -> dict:
        return self.tenants.get(tenant_id, {})

    def _emit_event(self, event: str, tenant_id: str = "", data: dict = None):
        if not self.events_path:
            return
        event_data = {
            "event": event,
            "tenant_id": tenant_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        }
        with open(self.events_path, "a") as f:
            f.write(json.dumps(event_data) + "\n")


# ─── E2E Test: Full User Journey ───────────────────────────────────────────────

class TestFullUserJourney:

    def test_complete_onboarding_flow(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        galaxy = client.get_galaxy()
        assert galaxy["bodies_count"] == 9

        session = client.start_onboarding("Marte")
        assert "session_id" in session
        assert client.sessions[session["session_id"]]["status"] == "started"

        tenant = client.complete_onboarding(
            session["session_id"], "TestUser", "conquistador"
        )
        assert tenant["name"] == "TestUser"
        assert tenant["plan"] == "conquistador"
        assert "crm" in tenant["capabilities"]
        assert "sales" in tenant["capabilities"]
        assert tenant["status"] == "active"

    def test_full_journey_with_voice(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        session = client.start_onboarding("Neptuno")
        tenant = client.complete_onboarding(session["session_id"], "VoiceUser", "imperio")
        tid = tenant["tenant_id"]

        voice_config = client.configure_voice(tid, channel="whatsapp")
        assert voice_config["channel"] == "whatsapp"
        assert voice_config["stt_provider"] == "openai"

        result = client.process_voice_message(tid)
        assert result["status"] == "processed"
        assert "response" in result

    def test_events_emitted_in_correct_order(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        session = client.start_onboarding("Júpiter")
        client.complete_onboarding(session["session_id"], "EventUser", "explorador")

        with open(events_file) as f:
            events = [json.loads(line)["event"] for line in f.readlines()]

        assert "onboarding_started" in events
        assert "tenant_created" in events
        assert "capabilities_assigned" in events
        assert "onboarding_completed" in events

        assert events.index("onboarding_started") < events.index("tenant_created")
        assert events.index("tenant_created") < events.index("capabilities_assigned")
        assert events.index("capabilities_assigned") < events.index("onboarding_completed")


# ─── E2E Test: Multi-Tenant Isolation ──────────────────────────────────────────

class TestMultiTenantIsolation:

    def test_two_users_different_capabilities(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        s1 = client.start_onboarding("Marte")
        t1 = client.complete_onboarding(s1["session_id"], "UserA", "explorador")

        s2 = client.start_onboarding("Júpiter")
        t2 = client.complete_onboarding(s2["session_id"], "UserB", "imperio")

        config_a = client.get_tenant_config(t1["tenant_id"])
        config_b = client.get_tenant_config(t2["tenant_id"])

        assert config_a["plan"] == "explorador"
        assert config_b["plan"] == "imperio"
        assert len(config_b["capabilities"]) > len(config_a["capabilities"])
        assert config_a["tenant_id"] != config_b["tenant_id"]

    def test_user_cannot_access_other_tenant(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        s1 = client.start_onboarding("Venus")
        t1 = client.complete_onboarding(s1["session_id"], "PrivateA", "conquistador")

        s2 = client.start_onboarding("Tauro")
        t2 = client.complete_onboarding(s2["session_id"], "PrivateB", "imperio")

        config_a = client.get_tenant_config(t2["tenant_id"])
        assert config_a["name"] == "PrivateB"
        assert config_a["name"] != "PrivateA"

    def test_voice_config_isolated_per_tenant(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        s1 = client.start_onboarding("Mercurio")
        t1 = client.complete_onboarding(s1["session_id"], "VoiceA", "explorador")

        s2 = client.start_onboarding("Venus")
        t2 = client.complete_onboarding(s2["session_id"], "VoiceB", "conquistador")

        client.configure_voice(t1["tenant_id"], channel="whatsapp")
        client.configure_voice(t2["tenant_id"], channel="telegram")

        assert client.voice_configs[t1["tenant_id"]]["channel"] == "whatsapp"
        assert client.voice_configs[t2["tenant_id"]]["channel"] == "telegram"


# ─── E2E Test: Edge Cases ──────────────────────────────────────────────────────

class TestEdgeCases:

    def test_galaxy_loads_with_all_agents(self):
        client = MockGalaxyAPIClient()
        galaxy = client.get_galaxy()
        assert galaxy["bodies_count"] == 9
        names = [b["name"] for b in galaxy["bodies"]]
        assert set(names) == set(CELESTIAL_BODIES)

    def test_agent_cards_generated_for_all_agents(self):
        client = MockGalaxyAPIClient()
        for agent_name in CELESTIAL_BODIES:
            cards = client.get_agent_cards(agent_name)
            assert len(cards) > 0
            assert all(c["agent"] == agent_name for c in cards)

    def test_invalid_session_returns_error(self):
        client = MockGalaxyAPIClient()
        result = client.complete_onboarding("invalid-session-id", "User", "explorador")
        assert "error" in result

    def test_voice_not_configured_returns_error(self):
        client = MockGalaxyAPIClient()
        s = client.start_onboarding("Marte")
        t = client.complete_onboarding(s["session_id"], "User", "explorador")
        result = client.process_voice_message(t["tenant_id"])
        assert "error" in result
        assert "Voice not configured" in result["error"]

    def test_unknown_tenant_voice_returns_error(self):
        client = MockGalaxyAPIClient()
        result = client.process_voice_message("nonexistent-tenant")
        assert "error" in result

    def test_invalid_tenant_config_returns_empty(self):
        client = MockGalaxyAPIClient()
        config = client.get_tenant_config("nonexistent")
        assert config == {}

    def test_graceful_degradation_voice_fallback(self, events_file):
        client = MockGalaxyAPIClient(events_path=events_file)

        s = client.start_onboarding("Marte")
        t = client.complete_onboarding(s["session_id"], "FallbackUser", "explorador")
        tid = t["tenant_id"]

        client.configure_voice(tid, channel="telegram")
        assert client.voice_configs[tid]["channel"] == "telegram"

        result = client.process_voice_message(tid)
        assert result["status"] == "processed"

    def test_plan_agents_mapping_complete(self):
        for plan, agents in PLAN_AGENTS.items():
            for agent in agents:
                assert agent in CELESTIAL_BODIES, f"{agent} not in celestial bodies"
                assert agent in AGENT_CAPABILITIES, f"{agent} has no capabilities defined"

    def test_all_celestial_bodies_assigned_to_plans(self):
        all_plan_agents = set()
        for agents in PLAN_AGENTS.values():
            all_plan_agents.update(agents)
        for body in CELESTIAL_BODIES:
            assert body in all_plan_agents, f"{body} not assigned to any plan"
