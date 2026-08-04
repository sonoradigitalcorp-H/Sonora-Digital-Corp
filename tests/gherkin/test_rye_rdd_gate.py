from pytest_bdd import scenario
from tests.steps.rye_rdd_gate_steps import *


@scenario("rye-rdd-gate.feature", "Commit autorizado con recibo RDD válido")
def test_rdd_gate_commit_authorized():
    pass


@scenario("rye-rdd-gate.feature", "Commit bloqueado por hallazgo crítico")
def test_rdd_gate_commit_blocked_critical():
    pass


@scenario("rye-rdd-gate.feature", "Kill switch desactiva el gate")
def test_rdd_gate_killswitch():
    pass


@scenario("rye-rdd-gate.feature", "Commit sin recibo es rechazado")
def test_rdd_gate_commit_no_receipt():
    pass
