import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from pipeline.gate_input import check_input

def test_valid_text_passes():
    result = check_input("Hola, me interesa el servicio")
    assert result["passed"] == True

def test_short_text_fails():
    result = check_input("a")
    assert result["passed"] == False
    assert "corto" in result["reason"]

def test_long_text_truncates():
    result = check_input("a" * 600)
    assert result["passed"] == False
    assert result["action"] == "truncate"

def test_spam_ignored():
    result = check_input("hoooolaaaaa asd test")
    assert result["passed"] == False
    assert result["action"] == "ignore"

def test_escalation_detected():
    result = check_input("Quiero hablar con un humano")
    assert result["passed"] == False
    assert result["action"] == "escalate_to_human"

def test_abuse_warns():
    result = check_input("Esto es una mierda")
    assert result["action"] == "warn_and_continue"
