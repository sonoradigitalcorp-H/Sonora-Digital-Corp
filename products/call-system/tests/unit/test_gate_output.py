import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pipeline.gate_output import check_response, sanitize

def test_clean_response_passes():
    result = check_response("Claro, te explico cómo funciona el servicio.", "¿cómo funciona?")
    assert result["passed"] == True

def test_markdown_detected():
    result = check_response("Te explico **esto**", "dime")
    assert "contiene_markdown" in result["issues"]

def test_objection_not_handled():
    result = check_response("De acuerdo", "no me interesa")
    assert "objecion_no_manejada" in result["issues"]

def test_objection_handled():
    result = check_response("Entiendo tu punto, déjame explicarte", "no me interesa")
    assert "objecion_no_manejada" not in result["issues"]

def test_sanitize_removes_markdown():
    assert sanitize("**texto**") == "texto"
    assert sanitize("`codigo`") == "codigo"

def test_sanitize_removes_links():
    assert sanitize("[link](url)") == "link"
