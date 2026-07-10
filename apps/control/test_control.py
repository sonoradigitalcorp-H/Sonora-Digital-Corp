import pytest
from fastapi.testclient import TestClient
from apps.control.main import app, SERVICES, KERNEL_LEVELS, check_service

client = TestClient(app)


def test_control_status_endpoint():
    resp = client.get("/api/v1/control/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "services" in data
    assert "alive_count" in data
    assert "total" in data
    assert data["total"] == len(SERVICES)


def test_kernel_status_endpoint():
    resp = client.get("/api/v1/control/kernel")
    assert resp.status_code == 200
    data = resp.json()
    assert "levels" in data
    assert len(data["levels"]) == 7


def test_execution_status_endpoint():
    resp = client.get("/api/v1/control/execution")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data


def test_health_endpoint():
    resp = client.get("/api/v1/control/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "details" in data


def test_dashboard_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Control Kernel" in resp.text
    assert "Cognitive Kernel Level 7" in resp.text


@pytest.mark.asyncio
async def test_check_service_localhost():
    result = await check_service("localhost", 19999)
    assert not result["alive"]
    assert result["port"] == 19999
