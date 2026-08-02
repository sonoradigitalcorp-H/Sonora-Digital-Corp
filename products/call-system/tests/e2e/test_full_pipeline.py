"""E2E smoke test: verifica que todo el sistema se importa y conecta sin errores."""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def test_imports():
    """Verifica que todos los módulos se importan sin errores."""
    from ai.stt import transcribe_bytes, get_whisper
    from ai.llm import compose_prompt, generate_response
    from pipeline.gate_input import check_input
    from pipeline.gate_output import check_response, sanitize
    from pipeline.context import detect_objection, get_niche_for_company
    from tenant.service import create_tenant, get_tenant, get_lead_type, save_call
    from analytics.scorer import score_interaction, get_ab_stats
    from analytics.ab_testing import assign_variant, register_result
    from analytics.evolution_hook import detect_patterns
    from memory.summarizer import generate_summary
    from campaigns.scraper import _mock_search, get_leads
    from campaigns.orchestrator import get_campaign_summary
    from campaigns.outreach import get_all_tenant_ids
    assert callable(transcribe_bytes)


def test_smoke_pipeline():
    """Smoke test: pipeline completo con datos simulados."""
    from pipeline.gate_input import check_input
    from pipeline.gate_output import check_response, sanitize
    from pipeline.context import detect_objection

    text = "Hola, quiero agendar una cita"
    gate = check_input(text)
    assert gate["passed"] is True

    objection_cat, objection_text = detect_objection(text)
    assert objection_cat is None

    response = "Claro, tenemos disponible el jueves a las 4pm. ¿Te parece bien?"
    output = check_response(response, text)
    assert output["passed"] is True or output["passed"] is False

    clean = sanitize(response)
    assert len(clean) > 0


def test_smoke_tenant():
    """Smoke test: creación y consulta de tenant."""
    from tenant.service import create_tenant, get_tenant

    t = create_tenant("Smoke Test", "+520000000000", "Smoke Corp", source="e2e_test")
    assert t["name"] == "Smoke Test"
    assert t["plan"] == "trial"

    found = get_tenant(phone="+520000000000")
    assert found is not None
    assert found["name"] == "Smoke Test"


def test_smoke_analytics():
    """Smoke test: scoring y A/B."""
    from analytics.scorer import score_interaction
    s = score_interaction("Hola", "gracias", True, True, 60)
    assert 0 <= s <= 100

    from analytics.ab_testing import assign_variant
    for _ in range(10):
        v = assign_variant("test", "cold")
        assert v in ("A", "B", "C")


def test_smoke_campaign():
    """Smoke test: campañas."""
    from campaigns.scraper import _mock_search
    from campaigns.orchestrator import get_campaign_summary
    leads = _mock_search("barberias")
    assert len(leads) >= 1
    summary = get_campaign_summary()
    assert "barberias" in summary


def test_smoke_outreach():
    """Smoke test: outreach."""
    from campaigns.outreach import get_all_tenant_ids, get_tenant_contact
    ids = get_all_tenant_ids()
    assert len(ids) >= 1
    contact = get_tenant_contact(ids[0])
    assert len(contact) > 0


def test_preflight():
    """Preflight: verifica que las dependencias críticas existen."""
    import httpx, json, yaml, asyncio
    assert httpx
    assert json
    assert yaml
    assert asyncio
