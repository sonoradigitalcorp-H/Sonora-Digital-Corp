from pytest_bdd import scenario
from tests.steps.process_payment_steps import *


@scenario("process-payment.feature", "Process successful payment")
def test_process_payment():
    pass


@scenario("process-payment.feature", "Process refund")
def test_process_refund():
    pass


@scenario("process-payment.feature", "Reject invalid payment")
def test_reject_invalid():
    pass
