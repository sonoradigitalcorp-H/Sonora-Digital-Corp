"""Tests for bridge agents (HermesAgent, OpenClawAgent, GbrainAgent)."""

import pytest
from unittest.mock import patch, MagicMock
from src.core.orchestrator import (
    HermesAgent, OpenClawAgent, GbrainAgent
)


class TestHermesAgent:
    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.HermesBridge")
    async def test_telegram_offline(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "offline"}
        agent = HermesAgent()
        result = await agent.run("mandá un mensaje por Telegram")
        assert result["status"] == "success"
        assert result.get("hermes_health", {}).get("status") == "offline"

    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.HermesBridge")
    async def test_whatsapp_offline(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "error"}
        agent = HermesAgent()
        result = await agent.run("enviar mensaje por WhatsApp a test")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_hermes_help(self):
        agent = HermesAgent()
        result = await agent.run("mostrame los comandos de hermes")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_hermes_passthrough(self):
        agent = HermesAgent()
        result = await agent.run("Hola desde el test")
        assert result["status"] == "success"


class TestOpenClawAgent:
    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.OpenClawBridge")
    async def test_delegate_offline(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "offline"}
        mock_bridge().list_agents.return_value = []
        agent = OpenClawAgent()
        result = await agent.run("delegá esta tarea a openclaw")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_openclaw_help(self):
        agent = OpenClawAgent()
        result = await agent.run("mostrame los agentes disponibles")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_openclaw_generic(self):
        agent = OpenClawAgent()
        result = await agent.run("cualquier consulta genérica")
        assert result["status"] == "success"


class TestGbrainAgent:
    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.GbrainBridge")
    async def test_search_offline(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "offline"}
        agent = GbrainAgent()
        result = await agent.run("buscá información sobre Python")
        assert result["status"] == "error"
        assert "GBrain no disponible" in result.get("error", "")

    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.GbrainBridge")
    async def test_think_offline(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "offline"}
        agent = GbrainAgent()
        result = await agent.run("sintetizá la información del proyecto")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    @patch("src.core.unified_bridge.GbrainBridge")
    async def test_gbrain_help(self, mock_bridge):
        mock_bridge().health.return_value = {"status": "ok"}
        mock_bridge().search.return_value = {"status": "success", "output": "GBrain help"}
        agent = GbrainAgent()
        result = await agent.run("mostrame los comandos de gbrain")
        assert result["status"] == "success"
