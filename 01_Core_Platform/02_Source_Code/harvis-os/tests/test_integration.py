"""Integration tests for Harvis OS."""

import pytest
from fastapi.testclient import TestClient

from src.core.main import app, dispatcher, registry, event_bus, planner


client = TestClient(app)


class TestDispatcherIntegration:
    """Tests de integración del Dispatcher."""

    def test_create_and_get_task(self):
        """Test crear y obtener tarea."""
        # Crear tarea
        response = client.post(
            "/api/v1/tasks",
            json={
                "source": "telegram",
                "user_id": "12345",
                "content": "Crea una función para validar emails"
            }
        )
        assert response.status_code == 200
        data = response.json()
        task_id = data["id"]

        # Obtener tarea
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_id

    def test_task_classification(self):
        """Test clasificación de tareas."""
        # Test código
        response = client.post(
            "/api/v1/tasks",
            json={
                "source": "web",
                "user_id": "user1",
                "content": "Implementar función de login"
            }
        )
        assert response.json()["category"] == "code"
        assert response.json()["assigned_agent"] == "openhands"

        # Test git
        response = client.post(
            "/api/v1/tasks",
            json={
                "source": "cli",
                "user_id": "user2",
                "content": "Haz commit de los cambios"
            }
        )
        assert response.json()["category"] == "git"
        assert response.json()["assigned_agent"] == "aider"

    def test_list_tasks_with_filters(self):
        """Test listar tareas con filtros."""
        # Crear varias tareas
        for i in range(5):
            client.post(
                "/api/v1/tasks",
                json={
                    "source": "telegram",
                    "user_id": f"user{i}",
                    "content": "Crea una función" if i % 2 == 0 else "Haz commit"
                }
            )

        # Listar todas
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200
        assert len(response.json()) >= 5

        # Filtrar por categoría
        response = client.get("/api/v1/tasks?category=code")
        assert response.status_code == 200


class TestRegistryIntegration:
    """Tests de integración del Agent Registry."""

    def test_list_agents(self):
        """Test listar agentes."""
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 4

    def test_get_agent(self):
        """Test obtener agente específico."""
        response = client.get("/api/v1/agents/openhands")
        assert response.status_code == 200
        assert response.json()["id"] == "openhands"

    def test_agent_health(self):
        """Test health check de agente."""
        response = client.get("/api/v1/agents/openhands/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestEventBusIntegration:
    """Tests de integración del Event Bus."""

    def test_publish_and_list_events(self):
        """Test publicar y listar eventos."""
        # Publicar evento
        response = client.post(
            "/api/v1/events",
            json={
                "type": "task.created",
                "source": "dispatcher",
                "payload": {"task_id": "test-123"}
            }
        )
        assert response.status_code == 200

        # Listar eventos
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_event_stats(self):
        """Test estadísticas de eventos."""
        response = client.get("/api/v1/events/stats")
        assert response.status_code == 200
        assert "total_events" in response.json()


class TestEndToEnd:
    """Tests end-to-end del flujo completo."""

    def test_full_flow(self):
        """Test flujo completo: request -> classify -> route -> plan."""
        # 1. Crear tarea
        response = client.post(
            "/api/v1/tasks",
            json={
                "source": "telegram",
                "user_id": "12345",
                "content": "Crear API REST para usuarios"
            }
        )
        assert response.status_code == 200
        task = response.json()
        task_id = task["id"]

        # 2. Verificar clasificación
        assert task["category"] == "code"
        assert task["assigned_agent"] == "openhands"
        assert task["confidence"] > 0.8

        # 3. Verificar que la tarea existe
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        # 4. Verificar agente disponible
        response = client.get("/api/v1/agents/openhands")
        assert response.status_code == 200
        assert response.json()["status"] == "online"

    def test_multiple_requests(self):
        """Test múltiples requests concurrentes."""
        tasks = []
        for i in range(10):
            response = client.post(
                "/api/v1/tasks",
                json={
                    "source": "telegram",
                    "user_id": f"user{i}",
                    "content": f"Tarea {i}: crear función"
                }
            )
            assert response.status_code == 200
            tasks.append(response.json())

        # Verificar que todas las tareas fueron creadas
        assert len(tasks) == 10

        # Verificar IDs únicos
        ids = [t["id"] for t in tasks]
        assert len(set(ids)) == 10
