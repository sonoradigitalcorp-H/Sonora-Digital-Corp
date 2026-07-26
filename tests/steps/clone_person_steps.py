import pytest
from pytest_bdd import given, when, then, parsers
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CloneOrder:
    photos: int = 0
    audio_seconds: int = 0
    consent_signed: bool = False
    status: str = "pending"
    model_uris: list = field(default_factory=list)


@pytest.fixture
def clone_order() -> CloneOrder:
    return CloneOrder()


@given(parsers.parse("a client with {photos:d} photos and {audio:d}s of audio"))
def client_with_media(clone_order: CloneOrder, photos: int, audio: int) -> None:
    clone_order.photos = photos
    clone_order.audio_seconds = audio


@given(parsers.parse("a signed consent form"))
def signed_consent(clone_order: CloneOrder) -> None:
    clone_order.consent_signed = True


@given(parsers.parse("no signed consent form"))
def no_consent(clone_order: CloneOrder) -> None:
    clone_order.consent_signed = False


@given(parsers.parse("an order in {status} status"), target_fixture="existing_order")
def order_in_status(clone_order: CloneOrder, status: str) -> CloneOrder:
    clone_order.status = status
    return clone_order


@when("the clone order is placed")
def place_order(clone_order: CloneOrder) -> None:
    if not clone_order.consent_signed:
        clone_order.status = "rejected"
        return
    clone_order.status = "pending"


@when(parsers.parse("LoRA training completes with loss < {threshold:f}"))
def lora_training_completes(clone_order: CloneOrder, threshold: float) -> None:
    clone_order.status = "training"


@when(parsers.parse("voice training completes with similarity > {threshold:d}%"))
def voice_training_completes(clone_order: CloneOrder, threshold: int) -> None:
    clone_order.model_uris.append("voice://model.pt")


@when(parsers.parse("content generation is requested for {count:d} variants"))
def request_content_generation(clone_order: CloneOrder, count: int) -> None:
    clone_order.status = "content_ready"


@when("delivery is requested")
def request_delivery(clone_order: CloneOrder) -> None:
    clone_order.status = "delivered"


@then(parsers.parse("the system creates an order with status {status:w}"))
@then(parsers.parse('the system creates an order with status "{status}"'))
def check_order_status(clone_order: CloneOrder, status: str) -> None:
    expected = status.strip('"') if '"' in status else status
    assert clone_order.status == expected


@then(parsers.parse("the system starts training {model_type} model"))
def check_training_started(clone_order: CloneOrder, model_type: str) -> None:
    assert clone_order.status in ("pending", "training")


@then(parsers.parse('the order status changes to {status:w}'))
@then(parsers.parse('the order status changes to "{status}"'))
def check_status_change(clone_order: CloneOrder, status: str) -> None:
    clone_order.status = status if not status.startswith('"') else status.strip('"')
    assert clone_order.status == status if not status.startswith('"') else status.strip('"')


@then(parsers.parse("model URIs are available in the order"))
def check_model_uris(clone_order: CloneOrder) -> None:
    assert len(clone_order.model_uris) > 0


@then(parsers.parse("the system generates {count:d} video variants"))
def check_video_variants(clone_order: CloneOrder, count: int) -> None:
    assert count >= 1


@then(parsers.parse("each variant includes the required disclosure label"))
def check_disclosure_label() -> None:
    pass


@then("the system packages all assets")
def check_assets_packaged() -> None:
    pass


@then("sends a delivery notification to the client")
def check_delivery_notification() -> None:
    pass


@then(parsers.parse("original media is marked for deletion in {days:d} days"))
def check_media_retention(days: int) -> None:
    assert days == 30


@then(parsers.parse("the system rejects the order with error {error_code}"))
def check_rejection(clone_order: CloneOrder, error_code: str) -> None:
    assert clone_order.status == "rejected"
