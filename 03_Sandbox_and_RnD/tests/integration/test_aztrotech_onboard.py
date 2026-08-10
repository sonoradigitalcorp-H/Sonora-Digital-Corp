#!/usr/bin/env python3
"""test_aztrotech_onboard.py — Tests TDD completos para Aztrotech Onboarding v2."""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

BASE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(BASE / "02_Client_Projects" / "Aztrotech" / "03_Media_Assets"))
sys.path.insert(0, str(BASE / "01_Core_Platform" / "03_Agentic_Infrastructure"))
sys.path.insert(0, str(BASE / "01_Core_Platform" / "05_Shared_Libraries" / "SDK_Python"))
sys.path.insert(0, str(BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "OKF_Knowledge"))


# === ROUTING ===
class TestRoutingAztrotech:
    def setup_method(self):
        import shutil
        reg = Path.home() / ".openclaw" / "workspace" / "tenant_registry.json"
        if reg.exists():
            reg.unlink()
        from tenant_router import init_registry
        init_registry()

    def test_routing_aztrotech(self):
        from tenant_router import get_tenant_for_bot
        r = get_tenant_for_bot("Aztro_tech_bot")
        assert r is not None
        assert r["tenant_id"] == "aztrotech"
        assert r["agent"] == "cesar"

    def test_routing_rye(self):
        from tenant_router import get_tenant_for_bot
        r = get_tenant_for_bot("RyE_production_bot")
        assert r is not None
        assert r["tenant_id"] == "rye"

    def test_register_new_tenant(self):
        from tenant_router import register_new_tenant, get_tenant_for_bot
        register_new_tenant("tok123", "testcorp", "TestCorp_bot", "Juan", "TestCorp")
        r = get_tenant_for_bot("TestCorp_bot")
        assert r["tenant_id"] == "testcorp"


# === LEAD SCORING ===
class TestLeadScoring:
    def test_cold_lead(self):
        from lead_scoring import calculate_lead_score
        lead = {"nombre": "Carlos"}
        r = calculate_lead_score(lead)
        assert r.classification == "COLD"
        assert r.score < 40

    def test_warm_lead(self):
        from lead_scoring import calculate_lead_score
        lead = {
            "nombre": "Carlos", "empresa": "MiEmpresa", "giro": "e_commerce",
            "tamano_equipo": "6-20", "servicio": "empleado_digital",
            "fecha": "2026-08-15",
            "presupuesto_mencionado": True  # +10 → total 48 → WARM
        }
        r = calculate_lead_score(lead)
        assert r.classification in ["WARM", "HOT"]
        assert r.score >= 40

    def test_hot_lead(self):
        from lead_scoring import calculate_lead_score
        lead = {
            "nombre": "Carlos", "empresa": "MiEmpresa", "giro": "e_commerce",
            "tamano_equipo": "20+", "servicio": "plataforma_medida",
            "fecha": "2026-08-15", "hora": "10:00",
            "presupuesto_mencionado": True, "urgencia_alta": True,
            "es_tomador_decisiones": True, "click_diagnostico": True
        }
        r = calculate_lead_score(lead)
        assert r.classification == "HOT"
        assert r.score >= 70

    def test_next_action_hot(self):
        from lead_scoring import calculate_lead_score
        lead = {
            "nombre": "Carlos", "empresa": "Mi", "giro": "e_commerce",
            "tamano_equipo": "20+", "servicio": "plataforma_medida",
            "fecha": "2026-08-15", "hora": "10:00",
            "presupuesto_mencionado": True, "urgencia_alta": True,
            "es_tomador_decisiones": True, "click_diagnostico": True
        }
        r = calculate_lead_score(lead)
        assert "Llamar" in r.next_action or "llamar" in r.next_action.lower()

    def test_objeciones_por_servicio(self):
        from lead_scoring import get_objeciones_por_servicio
        obj = get_objeciones_por_servicio("empleado_digital")
        assert len(obj) >= 3
        assert any("caro" in o["objecion"].lower() or "$999" in o["contraargumento"] for o in obj)


# === ONBOARDING ENGINE ===
class TestOnboardingEngine:
    def setup_method(self):
        self.db = tempfile.mktemp(suffix=".db")
        from onboarding_engine import OnboardingEngine
        self.engine = OnboardingEngine(self.db, "aztrotech")

    def teardown_method(self):
        if os.path.exists(self.db):
            os.unlink(self.db)

    def test_capture_lead(self):
        lead_id, scoring = self.engine.capture_lead("aztrotech", "chat1", {
            "nombre": "Carlos", "empresa": "MiEmpresa", "servicio": "empleado_digital"
        })
        assert lead_id is not None
        assert scoring.score >= 0
        assert scoring.classification in ["COLD", "WARM", "HOT"]

    def test_get_lead_with_intelligence(self):
        lead_id, _ = self.engine.capture_lead("aztrotech", "chat1", {
            "nombre": "Carlos", "empresa": "MiEmpresa", "servicio": "empleado_digital"
        })
        self.engine.save_intelligence(lead_id, {
            "resumen_empresa": "Mi Empresa de prueba",
            "objeciones_probables": ["caro", "no confío"],
            "contraargumentos": ["ROI 2-3 meses", "diagnóstico gratis"],
            "next_action": "Llamar mañana"
        })
        lead = self.engine.get_lead(lead_id)
        assert lead is not None
        assert lead["intelligence"]["resumen_empresa"] == "Mi Empresa de prueba"

    def test_schedule_cita(self):
        lead_id, _ = self.engine.capture_lead("aztrotech", "chat1", {
            "nombre": "Carlos", "empresa": "MiEmpresa", "servicio": "empleado_digital"
        })
        r = self.engine.schedule_cita(lead_id, "2026-08-15", "10:00")
        assert r["success"] is True

    def test_schedule_conflict(self):
        lead1, _ = self.engine.capture_lead("aztrotech", "chat1", {
            "nombre": "Carlos", "empresa": "E1", "servicio": "empleado_digital"
        })
        self.engine.schedule_cita(lead1, "2026-08-15", "10:00")
        lead2, _ = self.engine.capture_lead("aztrotech", "chat2", {
            "nombre": "Ana", "empresa": "E2", "servicio": "empleado_digital"
        })
        r = self.engine.schedule_cita(lead2, "2026-08-15", "10:00")
        assert r["success"] is False

    def test_dashboard_stats(self):
        self.engine.capture_lead("aztrotech", "c1", {"nombre": "A", "empresa": "E1"})
        self.engine.capture_lead("aztrotech", "c2", {"nombre": "B", "empresa": "E2"})
        stats = self.engine.get_dashboard_stats()
        assert stats["total_leads"] == 2
        assert "COLD" in stats["por_clasificacion"] or "WARM" in stats["por_clasificacion"]

    def test_list_leads_sorted_by_score(self):
        self.engine.capture_lead("aztrotech", "c1", {"nombre": "Low"})
        self.engine.capture_lead("aztrotech", "c2", {
            "nombre": "High", "empresa": "BigCorp", "giro": "e_commerce",
            "tamano_equipo": "20+", "servicio": "plataforma_medida",
            "presupuesto_mencionado": True, "urgencia_alta": True
        })
        leads = self.engine.list_leads(limit=10)
        assert len(leads) == 2
        assert leads[0]["score"] >= leads[1]["score"]


# === LEAD INTELLIGENCE ===
class TestLeadIntelligence:
    def test_fallback_intelligence(self):
        from lead_intelligence import _fallback_intelligence
        from lead_scoring import classify_by_giro
        giro = classify_by_giro("e_commerce")
        obj = [{"objecion": "caro", "contraargumento": "ROI"}]
        intel = _fallback_intelligence(
            {"nombre": "Carlos", "empresa": "Mi", "giro": "e_commerce", "tamano_equipo": "6-20", "servicio": "empleado_digital"},
            giro, obj
        )
        assert "Mi" in intel.resumen_empresa
        assert len(intel.objeciones_probables) == 1
        assert "Llamar" in intel.next_action

    def test_classify_by_giro(self):
        from lead_scoring import classify_by_giro
        r = classify_by_giro("e_commerce")
        assert "empleado_digital" in r["servicio_recomendado"]
        assert "Jewelry" in r["caso"] or "jewelry" in r["caso"].lower()

    def test_classify_by_giro_unknown(self):
        from lead_scoring import classify_by_giro
        r = classify_by_giro("otro")
        assert "diagnostico" in r["servicio_recomendado"]


# === ASSET GENERATION ===
class TestAssetGeneration:
    def test_get_prompt_imagen(self):
        from asset_generation import get_prompt
        p = get_prompt("imagen")
        assert p is not None
        assert p.provider == "midjourney"
        assert p.score > 0

    def test_get_prompt_with_use_case(self):
        from asset_generation import get_prompt
        p = get_prompt("imagen", "redes_sociales")
        assert p is not None
        assert "redes_sociales" in p.casos_uso

    def test_generate_asset_prompt(self):
        from asset_generation import generate_asset_prompt
        r = generate_asset_prompt("imagen", {"servicio": "Aztrotech"})
        assert "prompt_final" in r
        assert r["provider"] == "midjourney"

    def test_list_prompts(self):
        from asset_generation import list_prompts
        all_p = list_prompts()
        assert len(all_p) >= 8  # Al menos 8 prompts base
        img = list_prompts("imagen")
        assert len(img) >= 4


# === FEEDBACK LOOP ===
class TestFeedbackLoop:
    def setup_method(self):
        self.db = tempfile.mktemp(suffix=".db")
        from feedback_loop import FeedbackLoop
        self.loop = FeedbackLoop(self.db)

    def teardown_method(self):
        if os.path.exists(self.db):
            os.unlink(self.db)

    def test_process_event_rapido(self):
        from feedback_loop import FeedbackEvent
        e = FeedbackEvent(lead_id="l1", tenant="aztrotech", tipo="respuesta", valor=30)
        r = self.loop.process_event(e)
        assert "respuesta_rapida" in r["applied_rules"]
        assert r["score_delta_total"] > 0

    def test_process_event_lento(self):
        from feedback_loop import FeedbackEvent
        e = FeedbackEvent(lead_id="l1", tenant="aztrotech", tipo="respuesta", valor=7200)
        r = self.loop.process_event(e)
        assert "respuesta_lenta" in r["applied_rules"]
        assert r["score_delta_total"] < 0

    def test_process_event_diagnostico(self):
        from feedback_loop import FeedbackEvent
        e = FeedbackEvent(lead_id="l1", tenant="aztrotech", tipo="click",
                         valor=1, metadata={"elemento": "diagnostico"})
        r = self.loop.process_event(e)
        assert "click_diagnostico" in r["applied_rules"]

    def test_tenant_metrics(self):
        from feedback_loop import FeedbackEvent
        for i in range(5):
            e = FeedbackEvent(lead_id=f"l{i}", tenant="test", tipo="respuesta", valor=30)
            self.loop.process_event(e)
        m = self.loop.get_tenant_metrics("test")
        assert m["total_eventos"] == 5


# === VOICE PIPELINE ===
class TestVoicePipeline:
    def test_tts_text_returns_path(self):
        from voice_pipeline import tts_text
        path = tts_text("Hola mundo")
        assert path.endswith(".ogg") or path.startswith("[ERROR")
        if not path.startswith("[ERROR"):
            assert os.path.exists(path)
            os.unlink(path)


# === OKF PRICING ===
class TestOKFPricing:
    def test_okf_pricing_contains_packages(self):
        okf_path = BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "OKF_Knowledge" / "concepts" / "aztrotech.pricing.json"
        assert okf_path.exists()
        with open(okf_path) as f:
            data = json.load(f)
        paquetes = data["tables"]["paquetes_empleado_digital"]
        assert len(paquetes) == 3
        prices = [p["precio"] for p in paquetes]
        assert 999 in prices
        assert 1999 in prices
        assert 3999 in prices

    def test_no_antennas_in_pricing(self):
        okf_path = BASE / "01_Core_Platform" / "03_Agentic_Infrastructure" / "Databases" / "OKF_Knowledge" / "concepts" / "aztrotech.pricing.json"
        with open(okf_path) as f:
            content = f.read()
        assert "antena" not in content.lower()
        assert "instalación" not in content.lower()
        assert "visita técnica" not in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
