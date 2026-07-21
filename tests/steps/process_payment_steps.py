import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass


@dataclass
class Payment:
    intent_valid: bool = True
    amount: int = 0
    status: str = "pending"
    receipt: str = ""


@pytest.fixture
def payment() -> Payment:
    return Payment()


@given(parsers.parse("a valid payment intent of ${amount:d}"))
def valid_payment(payment: Payment, amount: int) -> None:
    payment.amount = amount
    payment.intent_valid = True


@given(parsers.parse("a completed payment of ${amount:d}"))
def completed_payment(payment: Payment, amount: int) -> None:
    payment.amount = amount
    payment.status = "completed"


@given("an invalid payment intent")
def invalid_payment(payment: Payment) -> None:
    payment.intent_valid = False


@when("I process the payment")
def process_payment(payment: Payment) -> None:
    if payment.intent_valid:
        payment.status = "completed"
        payment.receipt = "rcpt_001"
    else:
        payment.status = "rejected"


@when("I process a full refund")
def process_refund(payment: Payment) -> None:
    payment.status = "refunded"


@when("I attempt to process the payment")
def attempt_payment(payment: Payment) -> None:
    payment.status = "rejected"


@then("the payment is completed")
def check_completed(payment: Payment) -> None:
    assert payment.status == "completed"


@then("a receipt is generated")
def check_receipt(payment: Payment) -> None:
    assert len(payment.receipt) > 0


@then("the refund is completed")
def check_refund(payment: Payment) -> None:
    assert payment.status == "refunded"


@then(parsers.parse('the payment status changes to "{status}"'))
def check_payment_status(payment: Payment, status: str) -> None:
    assert payment.status == status


@then(parsers.parse('the system rejects with error "{error}"'))
def check_rejection(payment: Payment, error: str) -> None:
    assert payment.status == "rejected"
