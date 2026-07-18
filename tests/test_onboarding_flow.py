"""Tests para Onboarding Flow — FR-04: Flow de bienvenida"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(REPO))

from scripts.onboarding import get_flow_step


class TestFlowStep:
    def test_step_1_welcome(self):
        result = json.loads(get_flow_step(1, "Juan", "AztroTech"))
        assert result["step"] == 1
        assert "Juan" in result["message"]
        assert "AztroTech" in result["message"]
        assert result["delay"] == "0s"

    def test_step_2_tutorial(self):
        result = json.loads(get_flow_step(2, "Maria"))
        assert result["step"] == 2
        assert result["delay"] == "5m"
        assert "fotos" in result["message"].lower()

    def test_step_3_first_use(self):
        result = json.loads(get_flow_step(3))
        assert result["step"] == 3
        assert "foto" in result["message"].lower()

    def test_step_4_followup(self):
        result = json.loads(get_flow_step(4, "Carlos"))
        assert result["step"] == 4
        assert "Carlos" in result["message"]
        assert result["delay"] == "24h"

    def test_step_5_weekly(self):
        result = json.loads(get_flow_step(5, "Ana", photos_count=10, videos_count=3, chat_count=25))
        assert result["step"] == 5
        assert "10" in result["message"]
        assert "3" in result["message"]
        assert result["delay"] == "7d"

    def test_invalid_step_returns_error(self):
        result = json.loads(get_flow_step(99))
        assert "error" in result

    def test_channel_is_whatsapp(self):
        result = json.loads(get_flow_step(1))
        assert result["channel"] == "whatsapp"
