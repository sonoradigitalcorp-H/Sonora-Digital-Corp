"""Basic tests for Harvis OS."""

from fastapi.testclient import TestClient

from src.core.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Harvis OS"
    assert "version" in data


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_task():
    """Test task creation."""
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
    assert data["category"] == "code"
    assert data["assigned_agent"] == "openhands"
    assert data["confidence"] > 0.8


def test_list_agents():
    """Test list agents."""
    response = client.get("/api/v1/agents")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    agent_ids = [a["id"] for a in data]
    assert "openhands" in agent_ids
    assert "aider" in agent_ids


def test_tasks_stats():
    """Test task statistics endpoint is reachable."""
    response = client.get("/api/v1/tasks/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_tasks" in data
    assert "tasks_by_status" in data


def test_agents_stats():
    """Test agent statistics endpoint is reachable."""
    response = client.get("/api/v1/agents/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_agents" in data
    assert "online_agents" in data


def test_publish_event():
    """Test event publishing."""
    response = client.post(
        "/api/v1/events",
        json={
            "type": "task.created",
            "source": "dispatcher",
            "payload": {"task_id": "test-123"}
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "task.created"
    assert "id" in data
