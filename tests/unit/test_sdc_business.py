"""Tests for SDC Business Layer (spec 009)."""

import pytest
from src.core.sdc_business import (
    PLANS, list_plans, get_plan, calculate_price, recommend_plan,
    get_features, get_nicho_profile, SDCOnboarding, SDCCustomer,
    ADULT_MULTIPLIER, NICHO_PROFILES,
)


class TestPlans:
    def test_all_plans_defined(self):
        assert "explorador" in PLANS
        assert "conquistador" in PLANS
        assert "agente_ia" in PLANS
        assert "imperio" in PLANS

    def test_plan_prices(self):
        assert PLANS["explorador"]["price"] == 0
        assert PLANS["conquistador"]["price"] == 39
        assert PLANS["agente_ia"]["price"] == 69
        assert PLANS["imperio"]["price"] == 149

    def test_list_plans(self):
        plans = list_plans()
        assert len(plans) == 4
        assert all("id" in p for p in plans)

    def test_get_plan_valid(self):
        plan = get_plan("conquistador")
        assert plan is not None
        assert plan["name"] == "Conquistador"

    def test_get_plan_invalid(self):
        assert get_plan("nonexistent") is None

    def test_plan_features(self):
        for plan_id in PLANS:
            plan = get_plan(plan_id)
            assert len(plan["features"]) >= 3
            assert "limits" in plan


class TestPricing:
    def test_base_price(self):
        assert calculate_price("explorador") == 0
        assert calculate_price("conquistador") == 39
        assert calculate_price("agente_ia") == 69
        assert calculate_price("imperio") == 149

    def test_adult_multiplier(self):
        assert ADULT_MULTIPLIER == 2.0
        assert calculate_price("conquistador", "adulto") == 78
        assert calculate_price("agente_ia", "adulto") == 138
        assert calculate_price("imperio", "adulto") == 298

    def test_adult_explorador_stays_free(self):
        assert calculate_price("explorador", "adulto") == 0

    def test_other_nichos_no_multiplier(self):
        for nicho in ("musica", "fitness", "educacion", "ecommerce", "creativo"):
            assert calculate_price("conquistador", nicho) == 39


class TestRecommendPlan:
    def test_empresa_receives_imperio(self):
        assert recommend_plan("empresa", "vender") == "imperio"
        assert recommend_plan("empresa", "todo") == "imperio"

    def test_todo_needs_agente_ia(self):
        assert recommend_plan("persona", "todo") == "agente_ia"

    def test_vender_needs_conquistador(self):
        assert recommend_plan("persona", "vender") == "conquistador"
        assert recommend_plan("persona", "contenido") == "conquistador"
        assert recommend_plan("persona", "web") == "conquistador"

    def test_explorar_is_explorador(self):
        assert recommend_plan("persona", "explorar") == "explorador"
        assert recommend_plan("persona", "otro") == "explorador"
        assert recommend_plan("persona", "") == "explorador"


class TestFeatures:
    def test_adult_features_include_multiplier(self):
        features = get_features("conquistador", "adulto")
        assert "adult_multiplier_x2" in features

    def test_general_features_no_multiplier(self):
        features = get_features("conquistador", "musica")
        assert "adult_multiplier_x2" not in features

    def test_imperio_has_white_label(self):
        features = get_features("imperio")
        assert "white_label" in features

    def test_explorador_has_limited_features(self):
        features = get_features("explorador")
        assert "mystic_basic" in features
        assert "mystic_247" not in features


class TestNichoProfiles:
    def test_all_nichos_defined(self):
        expected = ("musica", "fitness", "educacion", "ecommerce", "creativo", "adulto", "empresa")
        for n in expected:
            assert n in NICHO_PROFILES, f"Missing nicho: {n}"

    def test_adult_has_multiplier(self):
        assert NICHO_PROFILES["adulto"]["multiplier"] == ADULT_MULTIPLIER

    def test_nicho_profile_has_skills(self):
        for nicho in NICHO_PROFILES:
            assert "skills" in NICHO_PROFILES[nicho]
            assert isinstance(NICHO_PROFILES[nicho]["skills"], list)

    def test_get_profile_valid(self):
        profile = get_nicho_profile("musica")
        assert "skills" in profile
        assert "agents" in profile

    def test_get_profile_invalid_returns_empty(self):
        profile = get_nicho_profile("nonexistent")
        assert profile == {"skills": [], "agents": []}


class TestSDCCustomer:
    def test_create_customer_in_memory(self):
        crm = SDCCustomer()
        customer = crm.create({
            "nombre": "Test User",
            "email": "test@test.com",
            "telefono": "+123456789",
            "tipo": "persona",
            "nicho": "musica",
            "plan": "conquistador",
        })
        assert customer is not None
        assert customer["nombre"] == "Test User"
        assert customer["email"] == "test@test.com"
        assert customer["plan"] == "conquistador"
        assert customer["status"] == "trial"

    def test_customer_has_id(self):
        crm = SDCCustomer()
        customer = crm.create({"nombre": "Test"})
        assert customer["id"] is not None
        assert len(customer["id"]) > 0

    def test_get_nonexistent_customer(self):
        crm = SDCCustomer()
        assert crm.get("nonexistent") is None


class TestSDCOnboarding:
    def test_full_onboarding_persona_musica(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "persona",
            "nicho": "musica",
            "necesidad": "vender",
            "nombre": "Artist Name",
            "email": "artist@test.com",
        })
        assert result["status"] == "onboarded"
        assert result["customer_id"] is not None
        assert result["plan"] == "conquistador"
        assert result["price"] == 39
        assert result["plan_name"] == "Conquistador"
        assert "mystic_247" in result["features"]

    def test_onboarding_empresa(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "empresa",
            "nicho": "musica",
            "necesidad": "automatizar",
            "nombre": "ABE MUSIC",
        })
        assert result["plan"] == "imperio"
        assert result["price"] == 149

    def test_onboarding_adult_multiplier(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "persona",
            "nicho": "adulto",
            "necesidad": "vender",
            "nombre": "Creadora",
        })
        assert result["price"] == 78  # 39 x 2

    def test_onboarding_todo_agente_ia(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "persona",
            "nicho": "general",
            "necesidad": "todo",
        })
        assert result["plan"] == "agente_ia"
        assert result["price"] == 69

    def test_onboarding_explorador_default(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "persona",
            "nicho": "general",
            "necesidad": "",
        })
        assert result["plan"] == "explorador"
        assert result["price"] == 0

    def test_onboarding_has_nicho_profile(self):
        onboarding = SDCOnboarding()
        result = onboarding.process({
            "tipo": "persona",
            "nicho": "adulto",
            "necesidad": "vender",
        })
        assert "nicho_profile" in result
        assert result["nicho_profile"]["multiplier"] == 2.0
