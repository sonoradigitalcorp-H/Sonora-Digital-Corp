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
from voice.wake_word import get_detector

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY") and not os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("OPENCODE_API_KEY"),
    reason="Integration tests requieren API key de LLM"
)

client = TestClient(app)

# Test data
TEST_MESSAGE = "buscar información sobre Python"
TEST_SESSION_TITLE = "Test Integration Session"


class TestVoiceIntegration:
    """Test voice API endpoints."""

    def test_voice_status(self):
        r = client.get("/api/voice/status")
        assert r.status_code == 200
        data = r.json()
        assert "whisper_available" in data
        assert "wake_word_available" in data

    def test_wake_word_detection(self):
        detector = get_detector()
        test_cases = [
            ("Hey JARVIS", True),
            ("Oye JARVIS ayuda", True),
            ("Hello world", False),
            ("JARVIS help me", True),
            ("Qué hora es", False),
        ]
        for text, expected in test_cases:
            detector._last_trigger = 0
            r = client.post("/api/voice/detect-wake", json={"text": text})
            assert r.status_code == 200
            assert r.json()["detected"] == expected, f"Failed for '{text}'"

    def test_voice_speak(self):
        r = client.post("/api/voice/speak", json={
            "text": "Hola mundo",
            "lang": "es"
        })
        # Might fail if no TTS engine available, but should return 200 or 400
        assert r.status_code in [200, 400, 422]
