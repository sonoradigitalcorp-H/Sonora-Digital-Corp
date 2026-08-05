"""Unit tests for Dispatcher."""

import pytest
from src.dispatcher.classifier import TaskClassifier
from src.dispatcher.router import AgentRouter
from src.dispatcher.dispatcher import Dispatcher, IncomingRequest


class TestTaskClassifier:
    """Tests del clasificador de tareas."""

    def setup_method(self):
        self.classifier = TaskClassifier()

    def test_classify_code_task(self):
        """Test clasificar tarea de código."""
        result = self.classifier.classify("Crear una función para validar emails")
        assert result.category == "code"
        assert result.confidence > 0.8

    def test_classify_git_task(self):
        """Test clasificar tarea de git."""
        result = self.classifier.classify("Haz commit de los cambios")
        assert result.category == "git"
        assert result.confidence > 0.8

    def test_classify_deploy_task(self):
        """Test clasificar tarea de deploy."""
        result = self.classifier.classify("Desplegar la aplicación en Docker")
        assert result.category == "deploy"
        assert result.confidence > 0.8

    def test_classify_unknown_task(self):
        """Test clasificar tarea desconocida."""
        result = self.classifier.classify("Algo que no entiendo")
        assert result.category == "other"
        assert result.confidence == 0.5

    def test_classify_empty_content(self):
        """Test clasificar contenido vacío."""
        result = self.classifier.classify("")
        assert result.category == "invalid"
        assert result.confidence == 0.0

    def test_get_agent_for_category(self):
        """Test obtener agente para categoría."""
        assert self.classifier.get_agent_for_category("code") == "openhands"
        assert self.classifier.get_agent_for_category("git") == "aider"
        assert self.classifier.get_agent_for_category("other") == "planner"


class TestAgentRouter:
    """Tests del router de agentes."""

    def setup_method(self):
        self.router = AgentRouter()

    def test_route_to_existing_agent(self):
        """Test rutear a agente existente."""
        result = self.router.route("openhands", "task-123")
        assert result.status == "assigned"
        assert result.agent_id == "openhands"

    def test_route_to_nonexistent_agent(self):
        """Test rutear a agente inexistente."""
        result = self.router.route("nonexistent", "task-123")
        assert result.status == "error"

    def test_release_agent(self):
        """Test liberar agente."""
        self.router.route("openhands", "task-1")
        assert self.router.release_agent("openhands") is True

    def test_get_available_agents(self):
        """Test obtener agentes disponibles."""
        available = self.router.get_available_agents()
        assert "openhands" in available
        assert "aider" in available


class TestDispatcher:
    """Tests del Dispatcher."""

    def setup_method(self):
        self.dispatcher = Dispatcher()

    @pytest.mark.asyncio
    async def test_process_request(self):
        """Test procesar petición."""
        request = IncomingRequest(
            source="telegram",
            user_id="12345",
            content="Crear una función"
        )
        task = await self.dispatcher.process_request(request)
        assert task.category == "code"
        assert task.assigned_agent == "openhands"
        assert task.id is not None

    @pytest.mark.asyncio
    async def test_process_multiple_requests(self):
        """Test procesar múltiples peticiones."""
        tasks = []
        for i in range(5):
            request = IncomingRequest(
                source="telegram",
                user_id=f"user{i}",
                content="Crear función" if i % 2 == 0 else "Haz commit"
            )
            task = await self.dispatcher.process_request(request)
            tasks.append(task)

        assert len(tasks) == 5
        # Verificar IDs únicos
        ids = [t.id for t in tasks]
        assert len(set(ids)) == 5

    def test_get_task(self):
        """Test obtener tarea."""
        import uuid
        task_id = str(uuid.uuid4())
        # Crear tarea mock
        from src.dispatcher.dispatcher import ClassifiedTask
        task = ClassifiedTask(
            id=task_id,
            request=IncomingRequest(source="test", user_id="1", content="test"),
            category="code",
            priority="high",
            assigned_agent="openhands",
            confidence=0.9,
            routing_reason="test",
        )
        self.dispatcher.tasks[task_id] = task

        result = self.dispatcher.get_task(task_id)
        assert result is not None
        assert result.id == task_id

    def test_get_stats(self):
        """Test obtener estadísticas."""
        stats = self.dispatcher.get_stats()
        assert "total_tasks" in stats
        assert "tasks_by_status" in stats
