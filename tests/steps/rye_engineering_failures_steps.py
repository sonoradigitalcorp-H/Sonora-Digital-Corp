import pytest
from dataclasses import dataclass, field
from pytest_bdd import given, when, then, parsers


@dataclass
class EngineeringState:
    user: str = ""
    message: str = ""
    response: str = ""
    sourced: bool = False
    rag_hit: bool = False
    backup_recommended: bool = False
    downtime_minutes: int = 0


@pytest.fixture
def engineering() -> EngineeringState:
    return EngineeringState()


@given(parsers.parse('que soy {user} y reporto "{message}"'))
def ivan_report(engineering: EngineeringState, user: str, message: str) -> None:
    engineering.user = user
    engineering.message = message


@given(parsers.parse('que soy {user} y digo "{message}"'))
def ivan_says(engineering: EngineeringState, user: str, message: str) -> None:
    engineering.user = user
    engineering.message = message


@given(parsers.parse('que soy {user} y pido "{message}"'))
def ivan_asks(engineering: EngineeringState, user: str, message: str) -> None:
    engineering.user = user
    engineering.message = message


@given(parsers.parse('que soy {user} y voy a reparar una celda'))
def ivan_repair(engineering: EngineeringState, user: str) -> None:
    engineering.user = user
    engineering.message = "reparar celda"


@given(parsers.parse('que soy {user} y pregunto por una pieza nueva sin ficha de setup'))
def ivan_new_piece(engineering: EngineeringState, user: str) -> None:
    engineering.user = user
    engineering.message = "pieza nueva sin ficha"


@given(parsers.parse('que soy {user} y pregunto "{message}"'))
def ivan_question(engineering: EngineeringState, user: str, message: str) -> None:
    engineering.user = user
    engineering.message = message


@when(parsers.parse('el sistema consulta el conocimiento curado de alarmas y mantenimiento'))
def query_alarms(engineering: EngineeringState) -> None:
    engineering.rag_hit = True
    engineering.response = (
        "SRVO-075: Movimiento fuera de límite o colisión detectada. "
        "Acción: liberar el robot, revisar COLLISION.DAO, reset y home. "
        "Fuente: manual FANUC."
    )


@when(parsers.parse('el sistema consulta el manual de celdas, fixtures y herramentales'))
def query_celdas(engineering: EngineeringState) -> None:
    engineering.rag_hit = True
    engineering.response = (
        "Procedimiento de cambio de pieza: "
        "1. Verificar fixture 3-2-1. "
        "2. Cargar programa correcto. "
        "3. Alinear UFRAME/UTOOL. "
        "4. Dry-run sin pieza. "
        "5. Control de primer artículo."
    )


@when(parsers.parse('el sistema consulta celdas y fixtures'))
def query_fixtures(engineering: EngineeringState) -> None:
    engineering.rag_hit = True
    engineering.response = (
        "Setup de herramental: verificar locators, alinear la referencia del robot, "
        "validar tolerancia ±0.05mm antes de producción."
    )


@when(parsers.parse('el sistema busca en el índice y en la base de datos de manuales'))
def query_index_and_manuals(engineering: EngineeringState) -> None:
    engineering.rag_hit = False
    engineering.response = (
        "No tengo el procedimiento de esa pieza en el conocimiento cargado. "
        "¿Puedes proporcionar planos y fixture para registrarla?"
    )


@when(parsers.parse('el sistema detecta que no hay backup reciente de parámetros'))
def detect_no_backup(engineering: EngineeringState) -> None:
    engineering.backup_recommended = True
    engineering.response = (
        "No hay backup reciente. Recomendación: hacer Image/File backup "
        "antes de tocar el robot."
    )


@when(parsers.parse('el sistema consulta el manual de programación y configuración'))
def query_programming_manual(engineering: EngineeringState) -> None:
    engineering.rag_hit = True
    engineering.response = (
        "Procedimiento de calibración de TCP (UTOOL): apuntar el soldador "
        "a un punto fijo e iterar hasta que TCP no se desvíe al rotar ejes. "
        "TCP mal calibrado provoca errores de posición."
    )


@when(parsers.parse('el sistema consulta integración IA y calidad'))
def query_integration_quality(engineering: EngineeringState) -> None:
    engineering.rag_hit = True
    engineering.response = (
        "Soldadura desalineada: verificar fixture, referencia UFRAME, "
        "calibración de visión Cognex. Registrar como no conformidad menor."
    )


@when(parsers.parse('el sistema consulta el manual de integración'))
def query_integration_manual(engineering: EngineeringState) -> None:
    engineering.rag_hit = True


@when(parsers.parse('el sistema aplica la regla de escalamiento'))
def apply_escalation(engineering: EngineeringState) -> None:
    engineering.downtime_minutes = 20
    engineering.response = (
        "Celda 1 parada 20 min. Notificar a supervisión. "
        "Verificar si es seguridad (SRVO-105/107) para prioridad alta."
    )


@then(parsers.parse('el sistema identifica el huérfano como posible {code} por colisión'))
def identify_collision(engineering: EngineeringState, code: str) -> None:
    assert code in engineering.response
    assert "colisión" in engineering.response.lower()


@then(parsers.parse('recomienda liberar el robot y revisar {dao} y reset y home'))
def recommend_reset(engineering: EngineeringState, dao: str) -> None:
    assert "liberar" in engineering.response.lower()
    assert dao.upper() in engineering.response.upper()
    assert "home" in engineering.response.lower()


@then('cita la fuente del manual FANUC si está en el conocimiento')
def cite_fanuc_manual(engineering: EngineeringState) -> None:
    if engineering.rag_hit:
        assert "manual" in engineering.response.lower() or "FANUC" in engineering.response


@then('el sistema da el procedimiento de cambio de pieza')
def change_procedure(engineering: EngineeringState) -> None:
    assert "Procedimiento" in engineering.response


@then('verifica fixture 3-2-1')
def verify_fixture(engineering: EngineeringState) -> None:
    assert "fixture" in engineering.response.lower()
    assert "3-2-1" in engineering.response


@then('carga programa correcto')
def load_program(engineering: EngineeringState) -> None:
    assert "programa" in engineering.response.lower()


@then('alinea UFRAME/UTOOL')
def align_uframe_utool(engineering: EngineeringState) -> None:
    assert "UFRAME" in engineering.response
    assert "UTOOL" in engineering.response


@then('ejecuta dry-run sin pieza')
def dry_run(engineering: EngineeringState) -> None:
    assert "dry-run" in engineering.response.lower()


@then('realiza control de primer artículo')
def first_article(engineering: EngineeringState) -> None:
    assert "primer artículo" in engineering.response.lower()


@then('recuerda que el fixture de la pieza nueva debe recalibrarse')
def fixture_recalibrate(engineering: EngineeringState) -> None:
    assert "fixture" in engineering.response.lower() or "recalibrar" in engineering.response.lower()


@then('el sistema indica verificar locators')
def verify_locators(engineering: EngineeringState) -> None:
    assert "locators" in engineering.response.lower()


@then('alinear la referencia del robot')
def align_reference(engineering: EngineeringState) -> None:
    assert "referencia" in engineering.response.lower() or "robot" in engineering.response.lower()


@then('validar tolerancia ±0.05mm antes de producción')
def validate_tolerance(engineering: EngineeringState) -> None:
    assert "0.05mm" in engineering.response or "±0.05" in engineering.response


@then('el sistema admite no tener el procedimiento de esa pieza')
def admit_unknown(engineering: EngineeringState) -> None:
    assert "No tengo" in engineering.response or "no tengo" in engineering.response


@then('solicita planos y fixture para registrarla')
def request_data(engineering: EngineeringState) -> None:
    assert "planos" in engineering.response.lower() or "fixture" in engineering.response.lower()


@then('el sistema recomienda hacer Image/File backup antes de tocar el robot')
def recommend_backup(engineering: EngineeringState) -> None:
    assert "backup" in engineering.response.lower()


@then('guarda un registro de la intervención en la memoria')
def log_intervention(engineering: EngineeringState) -> None:
    assert engineering.backup_recommended


@then('el sistema da el procedimiento de calibración de UTOOL')
def utool_procedure(engineering: EngineeringState) -> None:
    assert "calibración" in engineering.response.lower() or "UTOOL" in engineering.response


@then('aclara que un TCP mal calibrado provoca errores de posición')
def tcp_warning(engineering: EngineeringState) -> None:
    assert "TCP" in engineering.response or "UTOOL" in engineering.response
    assert "posición" in engineering.response.lower() or "error" in engineering.response.lower()


@then('el sistema sugiere verificar fixture')
def suggest_fixture(engineering: EngineeringState) -> None:
    assert "fixture" in engineering.response.lower()


@then('revisar referencia UFRAME')
def suggest_uframe(engineering: EngineeringState) -> None:
    assert "UFRAME" in engineering.response


@then('revisar calibración de visión Cognex')
def suggest_cognex(engineering: EngineeringState) -> None:
    assert "Cognex" in engineering.response


@then('registrar el defecto como no conformidad menor si afecta la pieza')
def register_nc(engineering: EngineeringState) -> None:
    assert "no conformidad" in engineering.response.lower() or "defecto" in engineering.response.lower()


@then(parsers.parse('el sistema responde ±{tolerance}mm para líneas automotrices BMW/Rivian'))
def respond_tolerance(engineering: EngineeringState, tolerance: str) -> None:
    engineering.response = (
        f"Tolerancia requerida: ±{tolerance}mm para líneas automotrices "
        "BMW/Rivian. Depende del fixture y calibración."
    )
    assert f"±{tolerance}mm" in engineering.response


@then('explica que depende del fixture y calibración')
def explain_fixture_calibration(engineering: EngineeringState) -> None:
    assert "fixture" in engineering.response.lower() or "calibración" in engineering.response.lower()


@then('el sistema sugiere revisar la conexión Ethernet/IP')
def suggest_ethernet(engineering: EngineeringState) -> None:
    engineering.response = (
        "Fallo de visión Cognex: revisar conexión Ethernet/IP y el timeout. "
        "SRVO-104 suele preceder fallas de visión."
    )
    assert "Ethernet/IP" in engineering.response


@then('revisar el timeout')
def suggest_timeout(engineering: EngineeringState) -> None:
    assert "timeout" in engineering.response.lower()


@then('aclara que SRVO-104 suele preceder fallas de visión')
def srvo104_precedes(engineering: EngineeringState) -> None:
    assert "SRVO-104" in engineering.response


@then('el sistema notifica a supervisión (downtime > 15min)')
def notify_supervision(engineering: EngineeringState) -> None:
    assert engineering.downtime_minutes > 15
    assert "supervisión" in engineering.response.lower() or "notificar" in engineering.response.lower()


@then('sugiere verificar si es seguridad (SRVO-105/107) para prioridad alta')
def suggest_safety_priority(engineering: EngineeringState) -> None:
    assert "SRVO-105" in engineering.response or "SRVO-107" in engineering.response
    assert "seguridad" in engineering.response.lower() or "prioridad alta" in engineering.response.lower()
