"""
End-to-end integration tests for JARVIS core flows.
Tests the complete pipeline: API → Orchestrator → Agents → Response.
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
from fastapi.testclient import TestClient
from webui.fastapp import app
from voice.wake_word import get_detector

client = TestClient(app)

# Test data
TEST_MESSAGE = "buscar información sobre Python"
TEST_SESSION_TITLE = "Test Integration Session"


class TestAPIIntegration:
    """Test the complete REST API surface."""

    def test_status(self):
        r = client.get("/api/status")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "running"
        assert data["version"] == "2.0.0"

    def test_session_crud(self):
        # Create
        r = client.post("/api/sessions", json={
            "title": TEST_SESSION_TITLE,
            "project": "Test"
        })
        assert r.status_code == 200
        session = r.json()
        assert session["title"] == TEST_SESSION_TITLE
        session_id = session["id"]

        # List
        r = client.get("/api/sessions")
        assert r.status_code == 200
        assert len(r.json()["sessions"]) >= 1

        # Get
        r = client.get(f"/api/sessions/{session_id}")
        assert r.status_code == 200
        assert r.json()["id"] == session_id

        # Update
        r = client.put(f"/api/sessions/{session_id}", json={
            "title": "Updated Title",
            "pinned": True
        })
        assert r.status_code == 200
        assert r.json()["pinned"] == True

        # Pin toggle
        r = client.post(f"/api/sessions/{session_id}/pin")
        assert r.status_code == 200
        assert "pinned" in r.json()

        # Delete
        r = client.delete(f"/api/sessions/{session_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"

    def test_session_search(self):
        r = client.get("/api/sessions/search?q=Bienvenido")
        assert r.status_code == 200
        assert r.json()["total"] >= 1

    def test_session_export(self):
        r = client.get("/api/sessions/search?q=Bienvenido")
        sessions = r.json().get("results", [])
        if sessions:
            sid = sessions[0]["id"]
            r = client.get(f"/api/sessions/{sid}/export/json")
            assert r.status_code == 200

    def test_sse_streaming(self):
        r = client.get(
            "/api/chat/default/stream",
            params={"message": TEST_MESSAGE}
        )
        assert r.status_code == 200
        assert r.headers.get("content-type") == "text/event-stream; charset=utf-8"
        content = r.text
        assert "event:" in content
        assert "data:" in content

    def test_orchestrator_routing(self):
        r = client.get(
            "/api/chat/default/stream",
            params={"message": "escribe una función en Python"}
        )
        assert r.status_code == 200
        content = r.text
        # Should mention code agent
        assert "code" in content or "tokens" in content

    def test_files(self):
        r = client.get("/api/files?path=.")
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "directory"
        assert len(data["items"]) > 0

    def test_git_status(self):
        r = client.get("/api/files/git")
        assert r.status_code == 200
        assert "branch" in r.json()

    def test_commands(self):
        for cmd in ["/help", "/clear", "/status", "/skills", "/voice", "/theme"]:
            r = client.post("/api/commands", json={
                "command": cmd,
                "session_id": "default"
            })
            assert r.status_code == 200
            assert r.json()["type"] in ["help", "clear", "status", "skills", "voice", "theme", "error"]

    def test_messages(self):
        r = client.post("/api/sessions/default/messages", json={
            "role": "user",
            "content": "Hola mundo",
            "tokens": 2
        })
        assert r.status_code == 200
        msg = r.json()
        assert msg["role"] == "user"
        assert msg["content"] == "Hola mundo"
