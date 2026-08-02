import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pipeline.context import detect_objection, get_niche_for_company

def test_detect_no_objection():
    cat, phrase = detect_objection("¿Cómo están?")
    assert cat is None

def test_detect_price_objection():
    cat, phrase = detect_objection("Está muy caro para mí")
    assert cat == "precio"
    assert "caro" in phrase

def test_detect_no_interest():
    cat, phrase = detect_objection("No me interesa, gracias")
    assert cat == "interes"

def test_detect_satisfied():
    cat, phrase = detect_objection("Ya tengo proveedor")
    assert cat == "satisfecho"

def test_detect_later():
    cat, phrase = detect_objection("Lo pienso y te aviso")
    assert cat == "tiempo"

def test_get_niche_by_company():
    assert get_niche_for_company("Barbería El Rey") == "agencies"
    assert get_niche_for_company("Bufete Jurídico") == "prof_services"
    assert get_niche_for_company("Tacos El Fogón") == "ecommerce"
    assert get_niche_for_company("Música Studio") == "music"
    assert get_niche_for_company("Ferretería López") == "general"
