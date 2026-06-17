"""
End-to-end integration tests for JARVIS core flows.
Tests the complete pipeline: API → Orchestrator → Agents → Response.
"""
import sys
import os
import json


import pytest
from fastapi.testclient import TestClient
from webui.fastapp import app

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("OPENCODE_API_KEY"),
    reason="Integration tests requieren API key de LLM"
)
from voice.wake_word import get_detector

client = TestClient(app)

# Test data
TEST_MESSAGE = "buscar información sobre Python"
TEST_SESSION_TITLE = "Test Integration Session"


class TestCoreStability:
    """Test stability under various conditions."""

    def test_empty_message(self):
        r = client.get(
            "/api/chat/default/stream",
            params={"message": ""}
        )
        assert r.status_code in [200, 422]

    def test_long_message(self):
        long_msg = "Hola " * 100
        r = client.get(
            "/api/chat/default/stream",
            params={"message": long_msg}
        )
        assert r.status_code == 200

    def test_invalid_session(self):
        r = client.get("/api/sessions/nonexistent-id")
        assert r.status_code == 404

    def test_invalid_file_path(self):
        r = client.get("/api/files?path=/nonexistent")
        assert r.status_code == 404

    def test_concurrent_sessions(self):
        # Create multiple sessions
        session_ids = []
        for i in range(5):
            r = client.post("/api/sessions", json={
                "title": f"Concurrent Test {i}",
                "project": "StressTest"
            })
            assert r.status_code == 200
            session_ids.append(r.json()["id"])

        # Verify they all exist
        for sid in session_ids:
            r = client.get(f"/api/sessions/{sid}")
            assert r.status_code == 200

        # Cleanup
        for sid in session_ids:
            client.delete(f"/api/sessions/{sid}")

    # ===== Methodology Commands =====

    def test_gsd_command(self):
        r = client.post("/api/commands", json={"command": "/gsd", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "gsd"

    def test_wrap_up_command(self):
        r = client.post("/api/commands", json={"command": "/wrap-up", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "wrap-up"

    def test_reflect_command(self):
        r = client.post("/api/commands", json={"command": "/reflect", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "reflect"

    def test_learn_command(self):
        r = client.post("/api/commands", json={"command": "/learn", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "learn"

    def test_methodology_in_help(self):
        r = client.post("/api/commands", json={"command": "/help", "session_id": "default"})
        assert r.status_code == 200
        data = r.json()
        assert "/gsd" in data["content"]
        assert "/wrap-up" in data["content"]
        assert "/reflect" in data["content"]
        assert "/learn" in data["content"]

    def test_skill_agent_routes_gsd(self):
        from src.core.orchestrator import get_orchestrator
        orch = get_orchestrator()
        agent = orch.route("ejecutá gsd para el proyecto")
        assert agent == "skill"

    def test_gbrain_agent_routes_learning_loop(self):
        from src.core.orchestrator import get_orchestrator
        orch = get_orchestrator()
        agent = orch.route("detectá patrones con learning-loop")
        assert agent == "gbrain"

    # ===== SDC Business Layer =====

    def test_sdc_list_plans(self):
        r = client.get("/api/sdc/plans")
        assert r.status_code == 200
        data = r.json()
        assert len(data["plans"]) == 4

    def test_sdc_get_plan(self):
        r = client.get("/api/sdc/plan/conquistador")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "Conquistador"
        assert data["effective_price"] == 39

    def test_sdc_get_plan_adult(self):
        r = client.get("/api/sdc/plan/conquistador?nicho=adulto")
        assert r.status_code == 200
        data = r.json()
        assert data["effective_price"] == 78

    def test_sdc_get_plan_not_found(self):
        r = client.get("/api/sdc/plan/nonexistent")
        assert r.status_code == 404

    def test_sdc_nicho_profile(self):
        r = client.get("/api/sdc/nicho/adulto")
        assert r.status_code == 200
        data = r.json()
        assert data["profile"]["multiplier"] == 2.0

    def test_sdc_onboarding_persona(self):
        r = client.post("/api/sdc/onboarding", json={
            "tipo": "persona",
            "nicho": "musica",
            "necesidad": "vender",
            "nombre": "Test Artist",
            "email": "artist@test.com",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "onboarded"
        assert data["plan"] == "conquistador"
        assert data["price"] == 39

    def test_sdc_onboarding_adult(self):
        r = client.post("/api/sdc/onboarding", json={
            "tipo": "persona",
            "nicho": "adulto",
            "necesidad": "vender",
            "nombre": "Creadora Test",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["price"] == 78

    def test_sdc_mystic_onboarding_step0(self):
        r = client.post("/api/sdc/onboarding/mystic", json={"message": "", "step": 0})
        assert r.status_code == 200
        data = r.json()
        assert data["step"] == 1
        assert "question" in data

    def test_sdc_mystic_onboarding_step1(self):
        r = client.post("/api/sdc/onboarding/mystic", json={
            "message": "soy una persona creativa",
            "step": 1,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["step"] == 2
        assert data["tipo"] == "persona"

    def test_sdc_mystic_onboarding_complete(self):
        r = client.post("/api/sdc/onboarding/mystic", json={
            "message": "vender",
            "step": 3,
            "tipo": "persona",
            "nicho": "musica",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["completed"] is True
        assert data["plan"] == "conquistador"

    # ===== ABE MUSIC API =====

    def test_abe_create_artist(self):
        r = client.post("/api/abe/artists", json={
            "nombre": "Artista Test",
            "genero": "Reggaeton",
            "pais": "PR",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["nombre"] == "Artista Test"

    def test_abe_list_artists(self):
        r = client.get("/api/abe/artists")
        assert r.status_code == 200
        assert "artists" in r.json()

    def test_abe_ceo_dashboard(self):
        r = client.get("/api/abe/dashboard/ceo")
        assert r.status_code == 200
        data = r.json()
        assert "total_artists" in data
        assert "total_revenue" in data
