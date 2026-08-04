from pytest_bdd import scenario
from tests.steps.rye_fanuc_expert_steps import *


@scenario("rye-fanuc-expert.feature", "Diagnóstico de alarma SRVO")
def test_fanuc_srvo_diagnosis():
    pass


@scenario("rye-fanuc-expert.feature", "Alarma desconocida")
def test_fanuc_unknown_alarm():
    pass


@scenario("rye-fanuc-expert.feature", "Procedimiento de mantenimiento")
def test_fanuc_maintenance_procedure():
    pass
