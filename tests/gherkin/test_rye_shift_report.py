from pytest_bdd import scenario
from tests.steps.rye_shift_report_steps import *


@scenario("rye-shift-report.feature", "Reporte de turno completo")
def test_shift_report_complete():
    pass


@scenario("rye-shift-report.feature", "Reporte de turno sin datos")
def test_shift_report_no_data():
    pass


@scenario("rye-shift-report.feature", "Turno sin especificar")
def test_shift_report_ask_cell():
    pass
