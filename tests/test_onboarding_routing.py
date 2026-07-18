"""Tests para Routing por Número — FR-03: Routing por teléfono"""

import json
import os
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

import sys

sys.path.insert(0, str(REPO))

os.environ["ONBOARDING_DB_PATH"] = str(Path(tempfile.mkdtemp()) / "test_routing.db")

from scripts.onboarding import detect_tenant, generate, validate


class TestDetectTenant:
    def test_detects_known_tenant(self):
        gen = json.loads(generate("aztrotech", "Test", "pro"))
        validate(gen["code"], "+5216620000001")
        result = json.loads(detect_tenant("+5216620000001"))
        assert result["tenant_id"] is not None
        assert result["type"] == "cliente"

    def test_returns_unknown_for_new_number(self):
        result = json.loads(detect_tenant("+5216629999999"))
        assert result["tenant_id"] is None
        assert result["type"] == "unknown"

    def test_returns_unknown_for_empty_phone(self):
        result = json.loads(detect_tenant(""))
        assert result["tenant_id"] is None
        assert result["type"] == "unknown"

    def test_multiple_clients_detected_correctly(self):
        gen1 = json.loads(generate("aztrotech", "Client A"))
        gen2 = json.loads(generate("abe_music", "Client B"))
        validate(gen1["code"], "+5216620000010")
        validate(gen2["code"], "+5216620000020")
        r1 = json.loads(detect_tenant("+5216620000010"))
        r2 = json.loads(detect_tenant("+5216620000020"))
        assert r1["tenant_id"] != r2["tenant_id"]
        assert r1["name"] == "Client A"
        assert r2["name"] == "Client B"

    def test_detects_partner_routing(self):
        gen = json.loads(generate("aztrotech", "Partner", "enterprise"))
        validate(gen["code"], "+5216620000030")
        result = json.loads(detect_tenant("+5216620000030"))
        assert result["partner_id"] == "aztrotech"

    def test_unknown_phone_gets_welcome_message(self):
        result = json.loads(detect_tenant("+5216629999999"))
        assert "message" in result
        assert "Bienvenido" in result["message"]
