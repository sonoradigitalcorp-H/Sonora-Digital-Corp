"""Tests for SDC Payments (Mercado Pago + Bitso + SPEI)."""

import pytest
from src.core.payments import (
    PAYMENT_PROVIDERS, PLANS, MercadoPagoClient, BitsoClient, PaymentOrchestrator
)


class TestPaymentProviders:
    def test_all_providers_defined(self):
        assert "mercadopago" in PAYMENT_PROVIDERS
        assert "bitso" in PAYMENT_PROVIDERS
        assert "spei" in PAYMENT_PROVIDERS

    def test_mercadopago_supports_spei(self):
        assert "spei" in PAYMENT_PROVIDERS["mercadopago"]["supports"]

    def test_bitso_supports_usdc(self):
        assert "usdc" in PAYMENT_PROVIDERS["bitso"]["supports"]

    def test_plan_prices_mxn(self):
        assert PLANS["conquistador"].price_mxn == 780
        assert PLANS["agente_ia"].price_mxn == 1380
        assert PLANS["imperio"].price_mxn == 2980


class TestMercadoPagoClient:
    def test_create_preference_mock(self):
        mp = MercadoPagoClient()
        result = mp.create_preference([{"title": "Test", "quantity": 1, "unit_price": 100}])
        assert result is not None
        assert result["id"].startswith("mock_")
        assert "init_point" in result

    def test_get_payment_no_token(self):
        mp = MercadoPagoClient()
        assert mp.get_payment("123") is None

    def test_webhook_approved(self):
        mp = MercadoPagoClient()
        result = mp.process_webhook({"action": "payment.updated", "data": {"id": "123"}})
        assert result["status"] in ("unknown", "approved", "rejected")

    def test_webhook_created(self):
        mp = MercadoPagoClient()
        result = mp.process_webhook({"action": "payment.created", "data": {"id": "123"}})
        assert result["status"] == "pending"


class TestBitsoClient:
    def test_create_charge(self):
        bitso = BitsoClient()
        result = bitso.create_charge(100, "Test")
        assert result is not None
        assert result["status"] == "pending"
        assert result["amount"] == 100
        assert "USDC" in result["accepted_currencies"]

    def test_create_charge_includes_link(self):
        bitso = BitsoClient()
        result = bitso.create_charge(500)
        assert "payment_link" in result
        assert "bitso.com" in result["payment_link"]


class TestPaymentOrchestrator:
    def test_create_mercadopago_payment(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("conquistador", "mercadopago")
        assert result["plan"] == "conquistador"
        assert result["amount"] == 780
        assert result["status"] == "pending"

    def test_create_bitso_payment(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("agente_ia", "bitso")
        assert result["plan"] == "agente_ia"
        assert result["amount"] == 1380

    def test_adult_multiplier(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("conquistador", "mercadopago", "adulto")
        assert result["amount"] == 1560  # 780 x 2

    def test_get_transaction(self):
        orchestrator = PaymentOrchestrator()
        created = orchestrator.create_payment("imperio", "mercadopago")
        fetched = orchestrator.get_transaction(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]

    def test_get_nonexistent_transaction(self):
        orchestrator = PaymentOrchestrator()
        assert orchestrator.get_transaction("nonexistent") is None

    def test_handle_webhook(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.handle_webhook("mercadopago", {"action": "payment.created", "data": {"id": "1"}})
        assert result["status"] == "pending"

    def test_invalid_plan(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("nonexistent")
        assert "error" in result

    def test_payment_url_included(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("conquistador", "mercadopago")
        assert "payment_url" in result

    def test_bitso_payment_url(self):
        orchestrator = PaymentOrchestrator()
        result = orchestrator.create_payment("conquistador", "bitso")
        assert result["payment_url"] is not None
