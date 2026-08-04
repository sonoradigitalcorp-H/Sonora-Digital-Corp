import json
import pytest
from dataclasses import dataclass, field
from pathlib import Path
from pytest_bdd import given, when, then, parsers

RDD_DIR = Path(__file__).resolve().parent.parent.parent / ".rdd"


@dataclass
class RDDGateState:
    feature: str = ""
    reviews: list = field(default_factory=list)
    receipt: dict | None = None
    blocked_reason: str = ""
    killswitch: dict = field(default_factory=lambda: {"enabled": True, "reason": None})
    attempt_result: str = ""


@pytest.fixture
def rdd_gate() -> RDDGateState:
    return RDDGateState()


def _make_receipt(feature: str, score: int, criticals: int) -> dict:
    return {
        "feature": feature,
        "receipt_id": f"20260803-{hash(feature) % 10000:04d}",
        "aggregated_score": score,
        "critical_issues": criticals,
        "reviews_complete": True,
        "authorization": {
            "allowed_to_commit": score >= 80 and criticals == 0,
            "reason": f"Score: {score}/100, Critical: {criticals}",
        },
    }


@given(parsers.parse('que el pipeline RDD se ejecutó sobre la feature "{feature}"'))
def rdd_pipeline_run(rdd_gate: RDDGateState, feature: str) -> None:
    rdd_gate.feature = feature


@given(parsers.parse("que los 4 lentes de revisión completaron con score {score:d}"))
def rdd_reviews_score(rdd_gate: RDDGateState, score: int) -> None:
    rdd_gate.reviews = [
        {"reviewer": "sdd-engineer", "status": "complete", "score": score},
        {"reviewer": "test-engineer", "status": "complete", "score": score},
        {"reviewer": "frontend-architect", "status": "complete", "score": score},
        {"reviewer": "backend-architect", "status": "complete", "score": score},
    ]


@given("que no hay hallazgos críticos")
def rdd_no_critical(rdd_gate: RDDGateState) -> None:
    rdd_gate.blocked_reason = ""


@given(parsers.parse('que la revisión detectó un hallazgo de severidad {severity}'))
def rdd_critical_finding(rdd_gate: RDDGateState, severity: str) -> None:
    rdd_gate.blocked_reason = f"Hallazgo severidad {severity}"


@given("que el gate RDD está activo")
def rdd_gate_active(rdd_gate: RDDGateState) -> None:
    rdd_gate.killswitch = {"enabled": True, "reason": None}


@given(parsers.parse('que no existe recibo RDD para la feature "{feature}"'))
def rdd_no_receipt(rdd_gate: RDDGateState, feature: str) -> None:
    rdd_gate.feature = feature
    rdd_gate.receipt = None


@when("se genera el recibo RDD")
def rdd_generate_receipt(rdd_gate: RDDGateState) -> None:
    score = rdd_gate.reviews[0]["score"] if rdd_gate.reviews else 0
    criticals = 1 if rdd_gate.blocked_reason else 0
    rdd_gate.receipt = _make_receipt(rdd_gate.feature, score, criticals)


@when("se activa el kill switch en emergencia documentada")
def rdd_activate_killswitch(rdd_gate: RDDGateState) -> None:
    rdd_gate.killswitch = {
        "enabled": False,
        "reason": "emergencia documentada",
        "activated_at": "2026-08-03",
    }


@when("se intenta hacer commit")
def rdd_attempt_commit(rdd_gate: RDDGateState) -> None:
    if rdd_gate.receipt is None:
        rdd_gate.attempt_result = "rejected"
    elif rdd_gate.receipt["authorization"]["allowed_to_commit"]:
        rdd_gate.attempt_result = "committed"
    else:
        rdd_gate.attempt_result = "rejected"


@then(parsers.parse("el recibo contiene receipt_id y aggregated_score {score:d}"))
def rdd_receipt_fields(rdd_gate: RDDGateState, score: int) -> None:
    assert rdd_gate.receipt is not None
    assert "receipt_id" in rdd_gate.receipt
    assert rdd_gate.receipt["aggregated_score"] == score


@then(parsers.parse("el commit queda autorizado (allowed_to_commit = {value})"))
def rdd_commit_authorized(rdd_gate: RDDGateState, value: str) -> None:
    expected = value == "true"
    assert rdd_gate.receipt["authorization"]["allowed_to_commit"] == expected


@then(parsers.parse("el commit queda bloqueado (allowed_to_commit = {value})"))
def rdd_commit_blocked(rdd_gate: RDDGateState, value: str) -> None:
    expected = value == "true"
    assert rdd_gate.receipt["authorization"]["allowed_to_commit"] == expected


@then("el recibo indica la razón del bloqueo")
def rdd_receipt_reason(rdd_gate: RDDGateState) -> None:
    assert rdd_gate.receipt["authorization"]["reason"]


@then("el gate queda desactivado")
def rdd_gate_disabled(rdd_gate: RDDGateState) -> None:
    assert rdd_gate.killswitch["enabled"] is False


@then("se registra la razón y la fecha de activación")
def rdd_killswitch_reason(rdd_gate: RDDGateState) -> None:
    assert rdd_gate.killswitch["reason"]
    assert rdd_gate.killswitch["activated_at"]


@then("el commit es rechazado por el gate")
def rdd_commit_rejected(rdd_gate: RDDGateState) -> None:
    assert rdd_gate.attempt_result == "rejected"
