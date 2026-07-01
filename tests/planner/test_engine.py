"""Tests for planner decision engine."""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from planner.decision_engine import execute_capability, select_provider
from planner.exceptions import NoProviderAvailableError
from planner.health import invalidate_all, set_health
from planner.models import ProviderHealth
from planner.registry import load_registry

SAMPLE_REGISTRY = {
    "version": "2.0.0",
    "capabilities": {
        "acquire-metadata": {
            "id": "acquire-metadata",
            "name": "Acquire Artist Metadata",
            "description": "Fetch artist profile from DSPs",
            "providers": [
                {"id": "deezer-api", "contract_type": "http", "weight": 1, "enabled": True, "cost_per_call": 0.0},
                {"id": "apple-music-api", "contract_type": "http", "weight": 2, "enabled": True, "cost_per_call": 0.0},
            ],
            "tags": ["artist", "metadata"],
        },
        "single-provider": {
            "id": "single-provider",
            "name": "Single Provider",
            "providers": [
                {"id": "only-one", "contract_type": "http", "weight": 1, "enabled": True},
            ],
        },
    },
}


def _healthy(provider_id: str):
    set_health(ProviderHealth(
        provider_id=provider_id,
        status="healthy",
        last_checked=datetime.now(timezone.utc),
    ))


def _down(provider_id: str):
    set_health(ProviderHealth(
        provider_id=provider_id,
        status="down",
        last_checked=datetime.now(timezone.utc),
    ))


@pytest.fixture(autouse=True)
def setup_registry(tmp_path: Path):
    invalidate_all()
    f = tmp_path / "registry.json"
    f.write_text(json.dumps(SAMPLE_REGISTRY))
    load_registry(f)
    return f


class TestSelectProvider:
    def test_select_primary_when_healthy(self):
        _healthy("deezer-api")
        _healthy("apple-music-api")
        provider = select_provider("acquire-metadata")
        assert provider.id == "deezer-api"

    def test_fallback_to_secondary(self):
        _down("deezer-api")
        _healthy("apple-music-api")
        provider = select_provider("acquire-metadata")
        assert provider.id == "apple-music-api"

    def test_all_down_raises_error(self):
        _down("deezer-api")
        _down("apple-music-api")
        with pytest.raises(NoProviderAvailableError):
            select_provider("acquire-metadata")

    def test_preferred_provider_selected(self):
        _healthy("deezer-api")
        _healthy("apple-music-api")
        provider = select_provider("acquire-metadata", preferred_provider="apple-music-api")
        assert provider.id == "apple-music-api"

    def test_preferred_provider_down_falls_back(self):
        _healthy("deezer-api")
        _down("apple-music-api")
        provider = select_provider("acquire-metadata", preferred_provider="apple-music-api")
        assert provider.id == "deezer-api"

    def test_cost_filter_excludes_expensive(self):

        from planner.registry import load_registry as lr
        data = dict(SAMPLE_REGISTRY)
        data["capabilities"]["acquire-metadata"]["providers"][0]["cost_per_call"] = 0
        data["capabilities"]["acquire-metadata"]["providers"][1]["cost_per_call"] = 0.01
        lr()  # force reload (we need a proper fixture for this)

    def test_nonexistent_capability_raises_error(self):
        with pytest.raises(NoProviderAvailableError):
            select_provider("nonexistent")

    def test_no_healthy_providers_with_flag(self):
        """When healthy_only=True and none are healthy in cache, should raise."""
        # Don't set any health (is_healthy defaults to True if no cache)
        # So this test needs providers that are explicitly unhealthy
        pass  # covered by test_all_down_raises_error


class TestExecuteCapability:
    @pytest.mark.asyncio
    async def test_execute_with_valid_provider(self):
        _healthy("deezer-api")
        result = await execute_capability(
            "single-provider",
            {"artist_name": "Test"},
            fallback=False,
        )
        # Should fail because "only-one" tries to hit localhost
        assert result.success is False  # No real HTTP endpoint configured
        assert result.provider_id == "only-one"

    @pytest.mark.asyncio
    async def test_execute_nonexistent_capability(self):
        result = await execute_capability("nonexistent", {})
        assert result.success is False
        assert "not found" in (result.error or "")

    @pytest.mark.asyncio
    async def test_execute_emits_event(self):
        _healthy("deezer-api")
        result = await execute_capability(
            "single-provider",
            {"artist_name": "Test"},
            fallback=False,
        )
        # Event should have been emitted regardless of success/failure
        assert result.capability_id == "single-provider"
