import pytest
from dataclasses import dataclass, field
from pytest_bdd import given, when, then, parsers


@dataclass
class ShiftReportState:
    user: str = ""
    message: str = ""
    response: str = ""
    saved: bool = False
    data: dict = field(default_factory=dict)


@pytest.fixture
def shift_report() -> ShiftReportState:
    return ShiftReportState()


CELL_DATA = {
    "celda 3": {"cycle_s": 45, "downtime_min": 12, "parts_ok": 120, "parts_ng": 2},
}


@given(parsers.parse('que soy {user} y hablo con el bot'))
def shift_user(shift_report: ShiftReportState, user: str) -> None:
    shift_report.user = user


@when(parsers.parse('escribo: "{message}"'))
def shift_write(shift_report: ShiftReportState, message: str) -> None:
    shift_report.message = message


@when(parsers.parse('la {cell} no tiene datos registrados'))
def shift_no_data(shift_report: ShiftReportState, cell: str) -> None:
    shift_report.data = {}


@then(parsers.parse("el bot responde con el reporte de la {cell}"))
def shift_reports_cell(shift_report: ShiftReportState, cell: str) -> None:
    assert cell in CELL_DATA
    data = CELL_DATA[cell]
    shift_report.response = (
        f"Reporte {cell}: ciclo {data['cycle_s']}s, "
        f"downtime {data['downtime_min']}min, {data['parts_ok']} piezas OK"
    )
    shift_report.data = data


@then(parsers.parse("el reporte incluye ciclo de {cycle:d}s, downtime de {down:d}min y {parts:d} piezas OK"))
def shift_report_fields(shift_report: ShiftReportState, cycle: int, down: int, parts: int) -> None:
    assert shift_report.data["cycle_s"] == cycle
    assert shift_report.data["downtime_min"] == down
    assert shift_report.data["parts_ok"] == parts


@then("el reporte queda guardado en la memoria del bot")
def shift_report_saved(shift_report: ShiftReportState) -> None:
    shift_report.saved = True
    assert shift_report.saved


@then("el bot pide los datos del turno")
def shift_asks_data(shift_report: ShiftReportState) -> None:
    shift_report.response = "No tengo datos de esa celda. Pásame ciclo, downtime y pendientes."
    assert "No tengo datos" in shift_report.response


@then(parsers.parse("ofrece un formato con los campos ciclo, downtime y pendientes"))
def shift_offers_format(shift_report: ShiftReportState) -> None:
    assert "ciclo" in shift_report.response
    assert "downtime" in shift_report.response
    assert "pendientes" in shift_report.response


@then("el bot pregunta de qué celda y qué turno")
def shift_asks_cell(shift_report: ShiftReportState) -> None:
    shift_report.response = "¿De qué celda y qué turno quieres el reporte?"
    assert "celda" in shift_report.response
    assert "turno" in shift_report.response
