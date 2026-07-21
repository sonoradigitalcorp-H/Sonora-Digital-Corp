from pytest_bdd import scenario

from tests.steps.clone_person_steps import *


@scenario("clone-person.feature", "Client places a clone order with valid inputs")
def test_clone_order_valid():
    pass


@scenario("clone-person.feature", "Training completes successfully")
def test_training_completes():
    pass


@scenario("clone-person.feature", "Training rejected without consent")
def test_training_rejected_no_consent():
    pass
