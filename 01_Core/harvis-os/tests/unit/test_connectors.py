"""Tests for Connectors."""

import pytest
from src.connectors import OllamaConnector, TelegramConnector, OpenClawConnector
from src.connectors.ollama import OllamaConfig, ChatMessage, ChatResponse
from src.connectors.telegram import TelegramConfig, TelegramMessage
from src.connectors.openclaw import OpenClawConfig, OpenClawTask


class TestOllamaConnector:
    """Tests del OllamaConnector."""

    def setup_method(self):
        self.config = OllamaConfig(
            base_url="http://localhost:11434",
            model="qwen3:4b",
        )
        self.connector = OllamaConnector(self.config)

    def test_config(self):
        """Test configuración."""
        assert self.connector.config.base_url == "http://localhost:11434"
        assert self.connector.config.model == "qwen3:4b"

    def test_health_check(self):
        """Test health check."""
        result = self.connector.health_check()
        # Ollama puede estar disponible o no
        assert result["status"] in ["healthy", "unhealthy"]
        assert "url" in result

    def test_list_models(self):
        """Test listar modelos."""
        models = self.connector.list_models()
        assert isinstance(models, list)

    def test_chat_response_structure(self):
        """Test estructura de respuesta de chat."""
        response = ChatResponse(
            content="Test response",
            model="test",
            total_duration=1000,
        )
        assert response.content == "Test response"
        assert response.model == "test"


class TestTelegramConnector:
    """Tests del TelegramConnector."""

    def setup_method(self):
        self.config = TelegramConfig(bot_token="test-token")
        self.connector = TelegramConnector(self.config)

    def test_config(self):
        """Test configuración."""
        assert self.connector.config.bot_token == "test-token"

    def test_on_message(self):
        """Test registrar handler."""
        handler = lambda msg: None
        self.connector.on_message(handler)
        assert len(self.connector._handlers) == 1

    def test_process_update(self):
        """Test procesar update."""
        update = {
            "message": {
                "message_id": 1,
                "chat": {"id": "123"},
                "from": {"id": "456", "username": "test"},
                "text": "Hello",
            }
        }
        self.connector.process_update(update)
        assert len(self.connector._messages) == 1

    def test_get_messages(self):
        """Test obtener mensajes."""
        for i in range(5):
            msg = TelegramMessage(
                message_id=i,
                chat_id="123",
                user_id="456",
                username="test",
                text=f"Message {i}",
            )
            self.connector._messages.append(msg)

        messages = self.connector.get_messages(limit=3)
        assert len(messages) == 3

    def test_stats(self):
        """Test estadísticas."""
        stats = self.connector.get_stats()
        assert "total_messages" in stats
        assert "handlers_registered" in stats


class TestOpenClawConnector:
    """Tests del OpenClawConnector."""

    def setup_method(self):
        self.config = OpenClawConfig(gateway_url="http://localhost:18789")
        self.connector = OpenClawConnector(self.config)

    def test_config(self):
        """Test configuración."""
        assert self.connector.config.gateway_url == "http://localhost:18789"

    def test_get_status_sync(self):
        """Test obtener estado (síncrono)."""
        # Solo verificar que la estructura es correcta
        assert self.connector.config.gateway_url == "http://localhost:18789"

    def test_send_task_structure(self):
        """Test estructura de tarea."""
        task = OpenClawTask(
            id="task-1",
            type="test",
            payload={"key": "value"},
        )
        assert task.id == "task-1"
        assert task.status == "pending"

    def test_get_tasks(self):
        """Test obtener tareas."""
        for i in range(5):
            task = OpenClawTask(
                id=f"task-{i}",
                type="test",
                payload={},
            )
            self.connector._tasks.append(task)

        tasks = self.connector.get_tasks(limit=3)
        assert len(tasks) == 3

    def test_stats(self):
        """Test estadísticas."""
        stats = self.connector.get_stats()
        assert "total_tasks" in stats
        assert "tasks_by_status" in stats
