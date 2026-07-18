"""Tests para Activación Agentica — FR-06: Skills por tipo de tenant"""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(REPO))

from scripts.onboarding import get_skills


class TestAgenticSkills:
    def test_cliente_has_basic_skills(self):
        result = json.loads(get_skills("cliente"))
        skills = result["skills"]
        assert "clone-service" in skills.get("openclaw", [])
        assert "wacli" in skills.get("openclaw", [])
        assert "whatsapp" in skills.get("hermes", [])
        assert len(skills.get("opencode", [])) >= 3

    def test_partner_has_advanced_skills(self):
        result = json.loads(get_skills("partner"))
        skills = result["skills"]
        assert "stripe" in skills.get("openclaw", [])
        assert "supabase" in skills.get("openclaw", [])
        assert "telegram" in skills.get("hermes", [])
        assert len(skills.get("opencode", [])) >= 6

    def test_admin_has_all_skills(self):
        result = json.loads(get_skills("admin"))
        assert result["skills"].get("openclaw") == "all"
        assert result["skills"].get("hermes") == "all"

    def test_skills_include_clone_service(self):
        result = json.loads(get_skills("cliente"))
        assert "clone-service" in result["skills"].get("openclaw", [])

    def test_partner_has_finance_and_security(self):
        result = json.loads(get_skills("partner"))
        opencode = result["skills"].get("opencode", [])
        assert "finance" in opencode
        assert "security" in opencode

    def test_default_is_cliente(self):
        result = json.loads(get_skills())
        assert result["tenant_type"] == "cliente"
