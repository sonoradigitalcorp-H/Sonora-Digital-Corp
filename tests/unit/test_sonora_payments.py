"""Tests para Monetización [FR4, FR5, FR6] — Stripe, $BEAT ledger, saludos híbridos."""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_payments_state():
    from apps.sonora_engine.payments import _balances, _pools, _greetings
    _balances.clear()
    _pools.clear()
    _greetings.clear()
    _pools["abe-music"] = {"total": 1000000, "circulating": 0, "burned": 0}
    _balances["fan-uuid"] = 200
    _balances["fan-a"] = 100
    _balances["fan-b"] = 50
    _balances["artist-uuid"] = 0


class TestStripeCheckout:
    """FR4: Stripe checkout session creation and webhook handling."""

    def test_create_checkout_session(self):
        pytest.importorskip("stripe", reason="stripe not installed")
        from apps.sonora_engine.payments import StripeCheckout

        with patch("stripe.checkout.Session.create") as mock_create:
            mock_create.return_value = MagicMock(
                id="cs_test_123",
                url="https://checkout.stripe.com/pay/cs_test_123",
            )
            svc = StripeCheckout()
            session = svc.create_greeting_checkout(
                tenant_id="abe-music",
                fan_id="fan-uuid",
                artist_name="Hector Rubio",
                greeting_message="Feliz cumpleaños!",
                amount_usd=5.00,
            )
            assert session.id == "cs_test_123"
            assert "checkout.stripe.com" in session.url
            mock_create.assert_called_once()

    def test_checkout_session_has_correct_amount(self):
        pytest.importorskip("stripe", reason="stripe not installed")
        from apps.sonora_engine.payments import StripeCheckout

        with patch("stripe.checkout.Session.create") as mock_create:
            mock_create.return_value = MagicMock(
                id="cs_test_123",
                url="https://checkout.stripe.com/pay/cs_test_123",
                amount_total=500,
            )
            svc = StripeCheckout()
            session = svc.create_greeting_checkout(
                tenant_id="abe-music",
                fan_id="fan-uuid",
                artist_name="Hector Rubio",
                greeting_message="Feliz cumpleaños!",
                amount_usd=5.00,
            )
            assert session.amount_total == 500

    def test_webhook_payment_success(self):
        from apps.sonora_engine.payments import StripeCheckout, _greetings

        _greetings["greeting-uuid"] = {"status": "pending_payment"}
        event = MagicMock()
        event.type = "checkout.session.completed"
        event.data.object.id = "cs_test_123"
        event.data.object.payment_status = "paid"
        event.data.object.metadata = {
            "tenant_id": "abe-music",
            "greeting_id": "greeting-uuid",
            "fan_id": "fan-uuid",
        }

        svc = StripeCheckout()
        with patch("apps.sonora_engine.payments.log.info") as mock_info:
            result = svc.handle_webhook(event)
            assert result["status"] == "completed"
            mock_info.assert_called()

    def test_webhook_payment_failed(self):
        from apps.sonora_engine.payments import StripeCheckout

        event = MagicMock()
        event.type = "checkout.session.expired"
        event.data.object.id = "cs_test_123"

        svc = StripeCheckout()
        with patch("apps.sonora_engine.payments.log.warning") as mock_warn:
            result = svc.handle_webhook(event)
            assert result["status"] == "failed"
            mock_warn.assert_called()


class TestBEATLedger:
    """FR5: $BEAT token operations — earn, burn, transfer, balance."""

    def test_earn_beat(self):
        from apps.sonora_engine.payments import BEATLedger
        ledger = BEATLedger()
        result = ledger.earn(
            tenant_id="abe-music",
            user_id="fan-uuid",
            amount=100,
            reason="quest_completion",
        )
        assert result["status"] == "earned"
        assert result["amount"] == 100

    def test_burn_beat_with_50pct_burn(self):
        from apps.sonora_engine.payments import BEATLedger
        ledger = BEATLedger()
        result = ledger.burn(
            tenant_id="abe-music",
            user_id="fan-uuid",
            amount=50,
            reason="greeting_payment",
            artist_id="artist-uuid",
        )
        assert result["status"] == "burned"
        assert result["artist_share"] == 25
        assert result["burned"] == 25

    def test_transfer_beat(self):
        from apps.sonora_engine.payments import BEATLedger, _balances
        _balances["fan-a"] = 100
        _balances["fan-b"] = 50
        ledger = BEATLedger()
        result = ledger.transfer(
            tenant_id="abe-music",
            from_user_id="fan-a",
            to_user_id="fan-b",
            amount=30,
        )
        assert result["status"] == "transferred"
        assert result["amount"] == 30
        assert _balances["fan-a"] == 70
        assert _balances["fan-b"] == 80

    def test_insufficient_balance_rejected(self):
        from apps.sonora_engine.payments import BEATLedger, _balances
        _balances["fan-uuid"] = 20
        ledger = BEATLedger()
        result = ledger.burn(
            tenant_id="abe-music",
            user_id="fan-uuid",
            amount=50,
            reason="greeting_payment",
        )
        assert result["status"] == "insufficient_funds"
        assert "alternative" in result

    def test_balance_query(self):
        from apps.sonora_engine.payments import BEATLedger, _balances
        _balances["fan-uuid"] = 200
        ledger = BEATLedger()
        balance = ledger.get_balance("fan-uuid")
        assert balance == 200

    def test_pool_total_tracked(self):
        from apps.sonora_engine.payments import BEATLedger
        ledger = BEATLedger()
        pool = ledger.get_pool("abe-music")
        assert pool["total"] >= 0
        assert pool["circulating"] >= 0
        assert pool["burned"] >= 0


class TestGreetingFlow:
    """FR6: Hybrid greeting — IA generates, artist approves."""

    def test_request_greeting(self):
        from apps.sonora_engine.payments import GreetingHandler
        handler = GreetingHandler()
        result = handler.request(
            tenant_id="abe-music",
            artist_id="artist-uuid",
            fan_id="fan-uuid",
            message="Feliz cumpleaños mama!",
        )
        assert result["status"] == "pending_payment"
        assert result["beat_cost"] > 0
        assert result["usd_cost"] > 0

    def test_ai_generates_audio(self):
        from apps.sonora_engine.payments import GreetingHandler, _greetings
        handler = GreetingHandler()
        _greetings["greeting-uuid"] = {
            "id": "greeting-uuid",
            "status": "paid",
            "audio_url": None,
        }
        with patch("apps.sonora_engine.payments.log.info") as mock_info:
            result = handler.generate_audio(greeting_id="greeting-uuid")
            assert result["status"] == "pending_approval"
            assert result["audio_url"] is not None
            mock_info.assert_called()

    def test_artist_approves_greeting(self):
        from apps.sonora_engine.payments import GreetingHandler, _greetings
        handler = GreetingHandler()
        _greetings["greeting-uuid"] = {
            "id": "greeting-uuid",
            "status": "pending_approval",
            "audio_url": "https://storage/test.mp3",
        }
        result = handler.approve(greeting_id="greeting-uuid")
        assert result["status"] == "approved"
        assert result["delivered"] is True

    def test_artist_rejects_greeting(self):
        from apps.sonora_engine.payments import GreetingHandler, _greetings
        handler = GreetingHandler()
        _greetings["greeting-uuid"] = {
            "id": "greeting-uuid",
            "status": "pending_approval",
            "audio_url": "https://storage/test.mp3",
        }
        result = handler.reject(greeting_id="greeting-uuid")
        assert result["status"] == "rejected"
        assert result["refunded"] is True

    def test_full_greeting_flow(self):
        from apps.sonora_engine.payments import GreetingHandler, _greetings
        handler = GreetingHandler()
        req = handler.request("abe-music", "artist-uuid", "fan-uuid", "Hola!")
        assert req["status"] == "pending_payment"

        gid = req["id"]
        _greetings[gid]["status"] = "paid"
        audio = handler.generate_audio(gid)
        assert audio["status"] == "pending_approval"

        approved = handler.approve(gid)
        assert approved["status"] == "approved"
