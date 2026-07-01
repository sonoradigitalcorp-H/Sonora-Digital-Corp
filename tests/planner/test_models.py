"""Tests for planner Pydantic models."""
import pytest
from pydantic import ValidationError

from planner.models import Capability, CapabilityResult, ProviderHealth, ProviderRef, RegistrySchema


class TestProviderRef:
    def test_defaults(self):
        p = ProviderRef(id="test", contract_type="http")
        assert p.weight == 1
        assert p.enabled is True
        assert p.rate_limit == 10
        assert p.cost_per_call == 0.0

    def test_weight_must_be_positive(self):
        with pytest.raises(ValidationError):
            ProviderRef(id="test", contract_type="http", weight=0)

    def test_contract_type_validation(self):
        with pytest.raises(ValidationError):
            ProviderRef(id="test", contract_type="invalid")


class TestCapability:
    def test_minimal_valid(self):
        c = Capability(
            id="test-cap",
            name="Test",
            providers=[ProviderRef(id="p1", contract_type="http")],
        )
        assert c.id == "test-cap"
        assert len(c.providers) == 1

    def test_missing_providers(self):
        with pytest.raises(ValidationError):
            Capability(id="test", name="Test", providers=[])

    def test_duplicate_provider_ids(self):
        with pytest.raises(ValidationError, match="Duplicate provider IDs"):
            Capability(
                id="test",
                name="Test",
                providers=[
                    ProviderRef(id="p1", contract_type="http"),
                    ProviderRef(id="p1", contract_type="http"),
                ],
            )

    def test_non_sequential_weights(self):
        with pytest.raises(ValidationError, match="sequential"):
            Capability(
                id="test",
                name="Test",
                providers=[
                    ProviderRef(id="p1", contract_type="http", weight=1),
                    ProviderRef(id="p2", contract_type="http", weight=3),
                ],
            )

    def test_sequential_weights_valid(self):
        c = Capability(
            id="test",
            name="Test",
            providers=[
                ProviderRef(id="p1", contract_type="http", weight=1),
                ProviderRef(id="p2", contract_type="http", weight=2),
            ],
        )
        assert len(c.providers) == 2


class TestRegistrySchema:
    def test_empty_registry(self):
        rs = RegistrySchema()
        assert rs.capabilities == {}
        assert rs.version == "2.0.0"

    def test_with_capabilities(self):
        rs = RegistrySchema(
            capabilities={
                "test": Capability(
                    id="test",
                    name="Test",
                    providers=[ProviderRef(id="p1", contract_type="http")],
                )
            }
        )
        assert len(rs.capabilities) == 1


class TestProviderHealth:
    def test_valid_health(self):
        from datetime import datetime, timezone
        h = ProviderHealth(
            provider_id="test",
            status="healthy",
            last_checked=datetime.now(timezone.utc),
        )
        assert h.status == "healthy"

    def test_invalid_status(self):
        from datetime import datetime, timezone
        with pytest.raises(ValidationError):
            ProviderHealth(
                provider_id="test",
                status="unknown",
                last_checked=datetime.now(timezone.utc),
            )


class TestCapabilityResult:
    def test_success_result(self):
        r = CapabilityResult(
            capability_id="test",
            provider_id="p1",
            success=True,
            data={"followers": 1000},
            latency_ms=150.0,
        )
        assert r.success is True
        assert r.data["followers"] == 1000

    def test_failure_result(self):
        r = CapabilityResult(
            capability_id="test",
            provider_id="p1",
            success=False,
            error="Something went wrong",
        )
        assert r.success is False
        assert r.error == "Something went wrong"

    def test_default_timestamp(self):
        r = CapabilityResult(
            capability_id="test",
            provider_id="p1",
            success=True,
        )
        assert r.timestamp is not None
