"""E2E Tests - Tests end-to-end del sistema completo."""

import pytest
from fastapi.testclient import TestClient
from src.core.main import app


client = TestClient(app)


class TestE2EFullFlow:
    """Tests E2E del flujo completo."""

    def test_request_to_response_flow(self):
        """Test flujo completo: request -> classify -> route."""
        # 1. Send request
        response = client.post(
            "/api/v1/tasks",
            json={
                "source": "telegram",
                "user_id": "e2e_user",
                "content": "Create a REST API for users"
            }
        )
        assert response.status_code == 200
        task = response.json()

        # 2. Verify classification
        assert task["category"] == "code"
        assert task["assigned_agent"] == "openhands"
        assert task["confidence"] > 0.8

        # 3. Verify task exists
        response = client.get(f"/api/v1/tasks/{task['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == task["id"]

    def test_multiple_tasks_flow(self):
        """Test flujo con múltiples tareas."""
        tasks = []
        for i in range(5):
            response = client.post(
                "/api/v1/tasks",
                json={
                    "source": "telegram",
                    "user_id": f"user_{i}",
                    "content": f"Task {i}: create function"
                }
            )
            assert response.status_code == 200
            tasks.append(response.json())

        # Verify all tasks were created
        assert len(tasks) == 5

        # Verify unique IDs
        ids = [t["id"] for t in tasks]
        assert len(set(ids)) == 5

    def test_agent_availability_flow(self):
        """Test flujo de disponibilidad de agentes."""
        # 1. List agents
        response = client.get("/api/v1/agents")
        assert response.status_code == 200
        agents = response.json()
        assert len(agents) >= 4

        # 2. Get specific agent
        response = client.get("/api/v1/agents/openhands")
        assert response.status_code == 200
        agent = response.json()
        assert agent["status"] == "online"

        # 3. Health check
        response = client.get("/api/v1/agents/openhands/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestE2EEventPropagation:
    """Tests E2E de propagación de eventos."""

    def test_event_publish_and_list(self):
        """Test publicar y listar eventos."""
        # 1. Publish event
        response = client.post(
            "/api/v1/events",
            json={
                "type": "task.created",
                "source": "dispatcher",
                "payload": {"task_id": "test-123"}
            }
        )
        assert response.status_code == 200

        # 2. List events
        response = client.get("/api/v1/events")
        assert response.status_code == 200
        events = response.json()
        assert len(events) >= 1

    def test_event_stats_flow(self):
        """Test estadísticas de eventos."""
        # 1. Get stats
        response = client.get("/api/v1/events/stats")
        assert response.status_code == 200
        stats = response.json()
        assert "total_events" in stats
        assert "events_by_type" in stats


class TestE2EHealthCheck:
    """Tests E2E de health check."""

    def test_system_health(self):
        """Test health del sistema."""
        response = client.get("/health")
        assert response.status_code == 200
        health = response.json()
        assert health["status"] == "healthy"

    def test_system_info(self):
        """Test información del sistema."""
        response = client.get("/")
        assert response.status_code == 200
        info = response.json()
        assert info["name"] == "Harvis OS"
        assert "components" in info


class TestE2EConcurrent:
    """Tests E2E de concurrencia."""

    def test_concurrent_requests(self):
        """Test requests concurrentes."""
        import concurrent.futures

        def create_task(i):
            return client.post(
                "/api/v1/tasks",
                json={
                    "source": "telegram",
                    "user_id": f"user_{i}",
                    "content": f"Concurrent task {i}"
                }
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_task, i) for i in range(10)]
            results = [f.result() for f in futures]

        # All should succeed
        for result in results:
            assert result.status_code == 200

        # All should have unique IDs
        ids = [r.json()["id"] for r in results]
        assert len(set(ids)) == 10
