"""Tests for OpenClaw Integration."""

import pytest
from src.integration import OpenClawIntegration, OpenClawBridge, OpenClawMessage, LLMResponse


class TestOpenClawIntegration:
    """Tests de integración con OpenClaw."""

    def setup_method(self):
        self.integration = OpenClawIntegration()

    def test_receive_message(self):
        """Test recibir mensaje."""
        message = OpenClawMessage(
            id="msg-1",
            source="openclaw",
            content="Hello from OpenClaw",
        )
        result = self.integration.receive_message(message)
        assert result is True
        assert len(self.integration.messages) == 1
        assert self.integration.messages[0].direction == "inbound"

    def test_send_message(self):
        """Test enviar mensaje."""
        message = OpenClawMessage(
            id="msg-1",
            source="harvis",
            content="Hello from Harvis",
        )
        result = self.integration.send_message(message)
        assert result is True
        assert len(self.integration.messages) == 1
        assert self.integration.messages[0].direction == "outbound"

    def test_process_with_llm(self):
        """Test procesar con LLM."""
        response = self.integration.process_with_llm("Test input")
        assert response.success is True
        assert response.model == "qwen2.5:1.5b"
        assert "Processed" in response.content

    def test_get_messages(self):
        """Test obtener mensajes."""
        for i in range(5):
            msg = OpenClawMessage(
                id=f"msg-{i}",
                source="test",
                content=f"Message {i}",
            )
            self.integration.receive_message(msg)

        messages = self.integration.get_messages(limit=3)
        assert len(messages) == 3

    def test_get_llm_stats(self):
        """Test estadísticas del LLM."""
        self.integration.process_with_llm("test1")
        self.integration.process_with_llm("test2")

        stats = self.integration.get_llm_stats()
        assert stats["total_requests"] == 2
        assert stats["successful"] == 2

    def test_verify_integration(self):
        """Test verificar integración."""
        status = self.integration.verify_integration()
        assert status["openclaw"]["enabled"] is True
        assert status["llm"]["enabled"] is True
        assert status["integration_status"] == "healthy"


class TestOpenClawBridge:
    """Tests del puente OpenClaw."""

    def setup_method(self):
        self.bridge = OpenClawBridge()

    def test_handle_inbound(self):
        """Test manejar mensaje entrante."""
        raw_message = {
            "id": "msg-1",
            "source": "openclaw",
            "content": "Test message",
        }
        result = self.bridge.handle_inbound(raw_message)
        assert result["status"] == "processed"
        assert "response" in result

    def test_get_status(self):
        """Test obtener estado."""
        status = self.bridge.get_status()
        assert "openclaw" in status
        assert "llm" in status
        assert "integration_status" in status
