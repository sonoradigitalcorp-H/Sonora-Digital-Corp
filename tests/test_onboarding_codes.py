"""Tests para Onboarding Codes — FR-01/FR-02: Generación y validación"""

import json
import os
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

import sys

sys.path.insert(0, str(REPO))

os.environ["ONBOARDING_DB_PATH"] = str(Path(tempfile.mkdtemp()) / "test_onboarding.db")

from scripts.onboarding import generate, list_codes, validate


class TestGenerate:
    def test_generates_valid_code(self):
        result = json.loads(generate("aztrotech", "Juan Pérez"))
        assert result["code"].startswith("SDC")
        assert len(result["code"]) == 9  # SDCXXXXXX (sin guión)
        assert result["partner_id"] == "aztrotech"
        assert result["client_name"] == "Juan Pérez"
        assert "wa_link" in result
        assert "BIENVENIDO_" in result["wa_link"]

    def test_requires_partner_id(self):
        result = json.loads(generate("", "Test"))
        assert "error" in result

    def test_requires_client_name(self):
        result = json.loads(generate("aztrotech", ""))
        assert "error" in result

    def test_generates_unique_codes(self):
        codes = set()
        for i in range(10):
            result = json.loads(generate("aztrotech", f"Client {i}"))
            codes.add(result["code"])
        assert len(codes) == 10

    def test_code_expires_in_6_hours(self):
        result = json.loads(generate("aztrotech", "Test"))
        assert "validity_hours" in result
        assert result["validity_hours"] == 6

    def test_default_plan_is_pro(self):
        result = json.loads(generate("aztrotech", "Test"))
        assert result["plan"] == "pro"

    def test_custom_plan(self):
        result = json.loads(generate("aztrotech", "Test", "enterprise"))
        assert result["plan"] == "enterprise"


class TestValidate:
    def test_validates_active_code(self):
        gen = json.loads(generate("aztrotech", "Juan"))
        result = json.loads(validate(gen["code"], "+5216622681111"))
        assert result["valid"] is True
        assert result["tenant_id"] is not None
        assert result["phone"] == "+5216622681111"

    def test_rejects_used_code(self):
        gen = json.loads(generate("aztrotech", "Maria"))
        validate(gen["code"], "+5216622682222")
        result = json.loads(validate(gen["code"], "+5216622683333"))
        assert result["valid"] is False
        assert "ya fue utilizado" in result["reason"]

    def test_rejects_invalid_code(self):
        result = json.loads(validate("SDC-INVALID"))
        assert result["valid"] is False
        assert "no reconocido" in result["reason"]

    def test_rejects_empty_code(self):
        result = json.loads(validate(""))
        assert "reason" in result
        assert result["valid"] is False

    def test_tenant_id_contains_partner_prefix(self):
        gen = json.loads(generate("aztrotech", "Pedro"))
        result = json.loads(validate(gen["code"], "+5216622684444"))
        assert result["tenant_id"].startswith("aztrotech_")

    def test_tenant_id_contains_phone_hash(self):
        gen = json.loads(generate("aztrotech", "Luis"))
        phone = "+5216622685555"
        result = json.loads(validate(gen["code"], phone))
        assert phone[:-4] in result["tenant_id"] or len(result["tenant_id"]) > 15

    def test_activation_creates_routing_entry(self):
        gen = json.loads(generate("aztrotech", "Ana"))
        phone = "+5216622686666"
        validate(gen["code"], phone)
        from scripts.onboarding import detect_tenant
        route = json.loads(detect_tenant(phone))
        assert route["tenant_id"] is not None
        assert route["type"] == "cliente"


class TestListCodes:
    def test_lists_all_codes(self):
        generate("aztrotech", "A")
        generate("aztrotech", "B")
        result = json.loads(list_codes())
        assert result["count"] >= 2

    def test_filters_by_partner(self):
        generate("aztrotech", "C")
        result = json.loads(list_codes("aztrotech"))
        for c in result["codes"]:
            assert c["partner_id"] == "aztrotech"
