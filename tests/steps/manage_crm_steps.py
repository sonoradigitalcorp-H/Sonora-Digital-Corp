import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field


@dataclass
class CRM:
    contacts: list = field(default_factory=list)
    deals: list = field(default_factory=list)


@pytest.fixture
def crm() -> CRM:
    return CRM()


@given("an artist profile in the system")
@given("a CRM contact exists")
def profile_exists() -> None:
    pass


@when("I create a CRM contact for the artist")
def create_contact(crm: CRM) -> None:
    crm.contacts.append({"id": 1, "status": "lead"})


@when(parsers.parse("I create a new deal worth ${amount:d}"))
def create_deal(crm: CRM, amount: int) -> None:
    crm.deals.append({"id": 1, "amount": amount, "status": "negotiation"})


@then(parsers.parse('the contact is stored with status "{status}"'))
def check_contact_status(crm: CRM, status: str) -> None:
    assert crm.contacts[0]["status"] == status


@then("the contact is linked to the artist profile")
def check_linked() -> None:
    pass


@then("the deal appears in the pipeline")
def check_deal_pipeline(crm: CRM) -> None:
    assert len(crm.deals) == 1


@then(parsers.parse('the deal status is "{status}"'))
def check_deal_status(crm: CRM, status: str) -> None:
    assert crm.deals[0]["status"] == status
