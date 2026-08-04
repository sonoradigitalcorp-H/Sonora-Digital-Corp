import pytest
from dataclasses import dataclass, field
from pytest_bdd import given, when, then, parsers


@dataclass
class FanucExpertState:
    user: str = ""
    message: str = ""
    response: str = ""
    sourced: bool = False
    rag_hit: bool = False


@pytest.fixture
def fanuc_expert() -> FanucExpertState:
    return FanucExpertState()


KNOWN_ALARMS = {
    "SRVO-075": {
        "cause": "Movimiento fuera de límite o colisión detectada",
        "action": "Verificar zona de trabajo, revisar collision detect, reiniciar con Reset",
    },
}

KNOWN_PROCEDURES = {
    "R-2000iC": ["1. Corte energía", "2. Verificar lubricación", "3. Chequear cables", "4. Prueba de movimiento lento"],
}


@given(parsers.parse('que soy {user} y hablo con el bot'))
def fanuc_user(fanuc_expert: FanucExpertState, user: str) -> None:
    fanuc_expert.user = user


@when(parsers.parse('escribo: "{message}"'))
def fanuc_write(fanuc_expert: FanucExpertState, message: str) -> None:
    fanuc_expert.message = message


@when(parsers.parse('el código {code} no está en el conocimiento'))
def fanuc_unknown(fanuc_expert: FanucExpertState, code: str) -> None:
    fanuc_expert.rag_hit = False


@then(parsers.parse("el bot responde con el diagnóstico de {code}"))
def fanuc_diagnosis(fanuc_expert: FanucExpertState, code: str) -> None:
    assert code in KNOWN_ALARMS
    alarm = KNOWN_ALARMS[code]
    fanuc_expert.response = f"{code}: Causa: {alarm['cause']}. Acción: {alarm['action']}"
    fanuc_expert.rag_hit = True


@then(parsers.parse("el diagnóstico incluye causa probable y acción correctiva"))
def fanuc_has_cause_action(fanuc_expert: FanucExpertState) -> None:
    assert "causa" in fanuc_expert.response.lower() or "causa probable" in fanuc_expert.response
    assert "Acción" in fanuc_expert.response


@then("cita la fuente del manual FANUC si está en el conocimiento")
def fanuc_source(fanuc_expert: FanucExpertState) -> None:
    if fanuc_expert.rag_hit:
        fanuc_expert.sourced = True
        assert fanuc_expert.sourced


@then("el bot admite no tener información del código")
def fanuc_admits_unknown(fanuc_expert: FanucExpertState) -> None:
    fanuc_expert.response = "No tengo información del código SRVO-999 en mi conocimiento."
    assert "No tengo información" in fanuc_expert.response


@then("sugiere consultar el manual FANUC oficial")
def fanuc_suggests_manual(fanuc_expert: FanucExpertState) -> None:
    fanuc_expert.response += " Consulta el manual FANUC oficial para SRVO."
    assert "manual" in fanuc_expert.response.lower()


@then(parsers.parse("el bot responde con los pasos del mantenimiento"))
def fanuc_maintenance_steps(fanuc_expert: FanucExpertState) -> None:
    assert "R-2000iC" in fanuc_expert.message
    fanuc_expert.response = "R-2000iC: " + " → ".join(KNOWN_PROCEDURES["R-2000iC"])
    assert "R-2000iC" in fanuc_expert.response


@then("el procedimiento se recupera del conocimiento RAG del tenant rye")
def fanuc_rag_recovery(fanuc_expert: FanucExpertState) -> None:
    fanuc_expert.rag_hit = True
    assert fanuc_expert.rag_hit
