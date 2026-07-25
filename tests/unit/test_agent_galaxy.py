"""Tests for Agent Galaxy — galaxy data, agent cards, tenant capabilities, voice pipeline, onboarding."""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest


# ─── Data Structures ───────────────────────────────────────────────────────────

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


class GalaxyAgent:
    """Data class for a celestial body agent (FR1-FR3)."""

    def __init__(self, name: str, color: str, orbit_radius: float, orbit_speed: float, plan: str):
        self.name = name
        self.color = color
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed
        self.plan = plan
        self.capabilities = AGENT_CAPABILITIES.get(name, [])

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "color": self.color,
            "orbit_radius": self.orbit_radius,
            "orbit_speed": self.orbit_speed,
            "plan": self.plan,
            "capabilities": self.capabilities,
        }


class AgentCard:
    """Yu-Gi-Oh style capability card (FR3-FR4)."""

    def __init__(self, agent_name: str, capability: str, description: str, tier: str = "common"):
        self.agent_name = agent_name
        self.capability = capability
        self.description = description
        self.tier = tier  # common | rare | epic | legendary

    def to_dict(self) -> dict:
        return {
            "agent_name": self.agent_name,
            "capability": self.capability,
            "description": self.description,
            "tier": self.tier,
        }


class Tenant:
    """Multi-tenant data model (FR6)."""

    def __init__(self, tenant_id: str, name: str, plan: str):
        self.tenant_id = tenant_id
        self.name = name
        self.plan = plan
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.status = "active"
        self.capabilities = self._assign_capabilities()

    def _assign_capabilities(self) -> list[str]:
        agents = PLAN_AGENTS.get(self.plan, PLAN_AGENTS["explorador"])
        caps = []
        for agent in agents:
            caps.extend(AGENT_CAPABILITIES.get(agent, []))
        return list(set(caps))


class VoicePipelineConfig:
    """Voice STT/TTS configuration (FR7)."""

    VALID_PROVIDERS = {"openai", "local"}
    VALID_CHANNELS = {"whatsapp", "telegram", "web"}

    def __init__(self, tenant_id: str, stt_provider: str = "openai",
                 tts_provider: str = "elevenlabs", channel: str = "whatsapp"):
        self.tenant_id = tenant_id
        if stt_provider not in self.VALID_PROVIDERS:
            raise ValueError(f"Invalid STT provider: {stt_provider}")
        if tts_provider not in self.VALID_PROVIDERS and tts_provider != "elevenlabs":
            raise ValueError(f"Invalid TTS provider: {tts_provider}")
        if channel not in self.VALID_CHANNELS:
            raise ValueError(f"Invalid channel: {channel}")
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider
        self.channel = channel
        self.configured_at = datetime.now(timezone.utc).isoformat()


class OnboardingSession:
    """Onboarding session model (FR5)."""

    def __init__(self, agent_choice: str, timeout_minutes: int = 1440):
        self.session_id = str(uuid.uuid4())
        self.agent_choice = agent_choice
        self.tenant_id = None
        self.status = "started"
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.expires_at = datetime.now(timezone.utc).replace(
            hour=23, minute=59, second=59
        ).isoformat()  # simplified expiry

    def complete(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.status = "completed"

    def is_expired(self) -> bool:
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.now(timezone.utc) > expires


def emit_event(event: str, tenant_id: str = "", data: dict = None, events_path: str = None):
    """Emit event to JSONL file (FR9)."""
    event_data = {
        "event": event,
        "tenant_id": tenant_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data or {},
    }
    if events_path:
        with open(events_path, "a") as f:
            f.write(json.dumps(event_data) + "\n")
    return event_data


# ─── Tests: Galaxy Data Structure ──────────────────────────────────────────────

class TestGalaxyDataStructure:

    def test_celestial_bodies_count(self):
        assert len(CELESTIAL_BODIES) == 9

    def test_all_celestial_bodies_present(self):
        expected = {"Mercurio", "Venus", "Tauro", "Marte", "Júpiter",
                    "Saturno", "Urano", "Neptuno", "Plutón"}
        assert set(CELESTIAL_BODIES) == expected

    def test_galaxy_agent_creation(self):
        agent = GalaxyAgent("Marte", "#DC143C", 7.5, 0.4, "conquistador")
        assert agent.name == "Marte"
        assert agent.color == "#DC143C"
        assert agent.orbit_radius == 7.5
        assert agent.orbit_speed == 0.4
        assert "crm" in agent.capabilities
        assert "sales" in agent.capabilities

    def test_galaxy_agent_to_dict(self):
        agent = GalaxyAgent("Venus", "#FFD700", 4.5, 0.6, "conquistador")
        data = agent.to_dict()
        assert data["name"] == "Venus"
        assert data["capabilities"] == AGENT_CAPABILITIES["Venus"]
        assert isinstance(data, dict)

    def test_unknown_agent_has_empty_capabilities(self):
        agent = GalaxyAgent("UnknownBody", "#FFFFFF", 25.0, 0.05, "explorador")
        assert agent.capabilities == []

    def test_jupiter_has_all_modules(self):
        agent = GalaxyAgent("Júpiter", "#DAA520", 10.0, 0.3, "imperio")
        assert "full-stack" in agent.capabilities
        assert "white-label" in agent.capabilities
        assert "all-modules" in agent.capabilities

    def test_pluton_is_admin_only(self):
        agent = GalaxyAgent("Plutón", "#8B4513", 20.0, 0.1, "admin")
        assert "admin-dashboard" in agent.capabilities
        assert "metrics" in agent.capabilities
        assert "system-config" in agent.capabilities


# ─── Tests: Agent Card Generation ──────────────────────────────────────────────

class TestAgentCardGeneration:

    def test_card_creation(self):
        card = AgentCard("Marte", "crm", "Manage customer relationships", "epic")
        assert card.agent_name == "Marte"
        assert card.capability == "crm"
        assert card.tier == "epic"

    def test_card_to_dict(self):
        card = AgentCard("Venus", "social-media", "Post to social networks", "rare")
        data = card.to_dict()
        assert data["capability"] == "social-media"
        assert data["tier"] == "rare"

    def test_card_default_tier(self):
        card = AgentCard("Tauro", "payments", "Process payments")
        assert card.tier == "common"

    def test_generate_cards_for_agent(self):
        agent = GalaxyAgent("Marte", "#DC143C", 7.5, 0.4, "conquistador")
        cards = [
            AgentCard(agent.name, cap, f"Capability: {cap}", "epic")
            for cap in agent.capabilities
        ]
        assert len(cards) == len(agent.capabilities)
        assert all(c.agent_name == "Marte" for c in cards)


# ─── Tests: Tenant Capability Assignment ───────────────────────────────────────

class TestTenantCapabilityAssignment:

    def test_explorador_plan_capabilities(self):
        tenant = Tenant(str(uuid.uuid4()), "Alpha", "explorador")
        expected = set(AGENT_CAPABILITIES["Mercurio"])
        assert set(tenant.capabilities) == expected

    def test_conquistador_plan_capabilities(self):
        tenant = Tenant(str(uuid.uuid4()), "Beta", "conquistador")
        expected_agents = ["Mercurio", "Venus", "Tauro", "Marte"]
        expected_caps = set()
        for a in expected_agents:
            expected_caps.update(AGENT_CAPABILITIES[a])
        assert set(tenant.capabilities) == expected_caps

    def test_imperio_plan_excludes_pluton(self):
        tenant = Tenant(str(uuid.uuid4()), "Gamma", "imperio")
        assert "admin-dashboard" not in tenant.capabilities
        assert "metrics" not in tenant.capabilities  # Plutón-only caps

    def test_admin_plan_has_pluton_only(self):
        tenant = Tenant(str(uuid.uuid4()), "Admin", "admin")
        expected = set(AGENT_CAPABILITIES["Plutón"])
        assert set(tenant.capabilities) == expected

    def test_unknown_plan_defaults_to_explorador(self):
        tenant = Tenant(str(uuid.uuid4()), "Unknown", "nonexistent")
        expected = set(AGENT_CAPABILITIES["Mercurio"])
        assert set(tenant.capabilities) == expected

    def test_tenants_have_isolated_capabilities(self):
        t1 = Tenant(str(uuid.uuid4()), "T1", "explorador")
        t2 = Tenant(str(uuid.uuid4()), "T2", "imperio")
        assert t1.capabilities != t2.capabilities
        assert len(t2.capabilities) > len(t1.capabilities)

    def test_tenant_has_unique_id(self):
        t1 = Tenant(str(uuid.uuid4()), "T1", "explorador")
        t2 = Tenant(str(uuid.uuid4()), "T2", "explorador")
        assert t1.tenant_id != t2.tenant_id

    def test_tenant_status_default(self):
        tenant = Tenant(str(uuid.uuid4()), "New", "explorador")
        assert tenant.status == "active"


# ─── Tests: STT/TTS Pipeline Configuration ─────────────────────────────────────

class TestVoicePipelineConfig:

    def test_default_config(self):
        config = VoicePipelineConfig(str(uuid.uuid4()))
        assert config.stt_provider == "openai"
        assert config.tts_provider == "elevenlabs"
        assert config.channel == "whatsapp"

    def test_custom_providers(self):
        config = VoicePipelineConfig(str(uuid.uuid4()), "local", "local", "telegram")
        assert config.stt_provider == "local"
        assert config.tts_provider == "local"
        assert config.channel == "telegram"

    def test_invalid_stt_provider(self):
        with pytest.raises(ValueError, match="Invalid STT provider"):
            VoicePipelineConfig(str(uuid.uuid4()), "invalid-stt", "elevenlabs")

    def test_invalid_channel(self):
        with pytest.raises(ValueError, match="Invalid channel"):
            VoicePipelineConfig(str(uuid.uuid4()), "openai", "elevenlabs", "discord")

    def test_web_channel(self):
        config = VoicePipelineConfig(str(uuid.uuid4()), channel="web")
        assert config.channel == "web"

    def test_config_has_timestamp(self):
        config = VoicePipelineConfig(str(uuid.uuid4()))
        assert config.configured_at is not None
        assert "T" in config.configured_at  # ISO 8601


# ─── Tests: Onboarding Flow ────────────────────────────────────────────────────

class TestOnboardingFlow:

    def test_session_creation(self):
        session = OnboardingSession("Marte")
        assert session.status == "started"
        assert session.tenant_id is None
        assert len(session.session_id) > 0

    def test_session_completion(self):
        session = OnboardingSession("Júpiter")
        tid = str(uuid.uuid4())
        session.complete(tid)
        assert session.status == "completed"
        assert session.tenant_id == tid

    def test_session_has_uuid(self):
        session = OnboardingSession("Venus")
        uuid.UUID(session.session_id)  # Should not raise

    def test_session_expiry(self):
        session = OnboardingSession("Tauro")
        session.expires_at = datetime.now(timezone.utc).replace(year=2000).isoformat()
        assert session.is_expired() is True

    def test_session_not_expired(self):
        session = OnboardingSession("Saturno")
        session.expires_at = datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc).isoformat()
        assert session.is_expired() is False

    def test_full_onboarding_flow(self):
        session = OnboardingSession("Neptuno")
        tenant = Tenant(str(uuid.uuid4()), "NewUser", "imperio")
        session.complete(tenant.tenant_id)
        assert session.status == "completed"
        assert "rag" in tenant.capabilities
        assert "knowledge-base" in tenant.capabilities


# ─── Tests: Event Emission ─────────────────────────────────────────────────────

class TestEventEmission:

    def test_emit_event_returns_dict(self):
        event = emit_event("galaxy_page_loaded")
        assert event["event"] == "galaxy_page_loaded"
        assert "timestamp" in event
        assert "data" in event

    def test_emit_event_with_tenant(self):
        tid = str(uuid.uuid4())
        event = emit_event("tenant_created", tenant_id=tid)
        assert event["tenant_id"] == tid

    def test_emit_event_with_data(self):
        event = emit_event("capabilities_assigned", data={"plan": "imperio"})
        assert event["data"]["plan"] == "imperio"

    def test_emit_event_writes_to_file(self, tmp_path):
        events_file = str(tmp_path / "events.jsonl")
        emit_event("test_event", tenant_id="test", events_path=events_file)
        with open(events_file) as f:
            lines = f.readlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["event"] == "test_event"

    def test_onboarding_events_sequence(self, tmp_path):
        events_file = str(tmp_path / "events.jsonl")
        tid = str(uuid.uuid4())

        emit_event("onboarding_started", tenant_id=tid, events_path=events_file)
        emit_event("tenant_created", tenant_id=tid, events_path=events_file)
        emit_event("capabilities_assigned", tenant_id=tid,
                   data={"plan": "conquistador"}, events_path=events_file)
        emit_event("onboarding_completed", tenant_id=tid, events_path=events_file)

        with open(events_file) as f:
            events = [json.loads(line) for line in f.readlines()]

        assert len(events) == 4
        assert events[0]["event"] == "onboarding_started"
        assert events[3]["event"] == "onboarding_completed"
