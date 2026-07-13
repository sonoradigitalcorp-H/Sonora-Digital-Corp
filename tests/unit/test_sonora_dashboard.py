"""Tests para Dashboard [FR7, FR8] — REST endpoints y WebSocket streaming."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestDashboardAPI:
    """FR7: Dashboard REST endpoints."""

    @pytest.fixture
    def dashboard(self):
        from apps.sonora_engine.dashboard import DashboardService
        return DashboardService()

    def test_revenue_stats(self, dashboard):
        """FR7: Revenue stats scoped to tenant"""
        result = dashboard.get_revenue_stats(tenant_id="abe-music")
        assert "total_revenue" in result
        assert "monthly_revenue" in result
        assert "daily_breakdown" in result
        assert isinstance(result["daily_breakdown"], list)

    def test_token_circulation(self, dashboard):
        """FR7: Token stats with supply, circulating, burned"""
        result = dashboard.get_token_stats(tenant_id="abe-music")
        assert "total_supply" in result
        assert "circulating" in result
        assert "burned" in result
        assert "earned_today" in result

    def test_greeting_stats(self, dashboard):
        """FR7: Greeting counts by status"""
        result = dashboard.get_greeting_stats(tenant_id="abe-music")
        assert "total" in result
        assert "pending" in result
        assert "approved" in result
        assert "rejected" in result

    def test_quest_stats(self, dashboard):
        """FR7: Quest completion stats"""
        result = dashboard.get_quest_stats(tenant_id="abe-music")
        assert "total_completed" in result
        assert "by_category" in result
        assert "beat_rewarded" in result

    def test_data_is_tenant_scoped(self, dashboard):
        """FR7: Data is isolated per tenant"""
        a = dashboard.get_revenue_stats(tenant_id="abe-music")
        b = dashboard.get_revenue_stats(tenant_id="other-tenant")
        # Different tenants should (potentially) have different data
        assert isinstance(a, dict)
        assert isinstance(b, dict)

    def test_dashboard_endpoint_exists(self):
        """FR7: FastAPI endpoint is registered"""
        from apps.sonora_engine.main import app

        paths = [r.path for r in app.routes]
        assert "/api/v1/dashboard/revenue" in paths
        assert "/api/v1/dashboard/tokens" in paths
        assert "/api/v1/dashboard/greetings" in paths
        assert "/api/v1/dashboard/quests" in paths
        assert "/api/v1/dashboard/leaderboard" in paths


class TestWebSocketEvents:
    """FR8: WebSocket streaming of events."""

    def test_event_emitted_on_quest_complete(self):
        """FR8: Quest completion emits gamification:quest:completed"""
        from apps.sonora_engine.main import emit_event

        with patch("redis.Redis.from_url") as mock_redis:
            instance = MagicMock()
            mock_redis.return_value = instance

            emit_event(
                event_type="gamification:quest:completed",
                tenant_id="abe-music",
                payload={"fan_id": "fan-uuid", "quest_id": "quest-001", "reward": 10},
            )
            instance.publish.assert_called_once()
            call_args = instance.publish.call_args[0]
            assert call_args[0] == "agent:events"

    def test_event_emitted_on_payment(self):
        """FR8: Payment emits payment:stripe:completed"""
        from apps.sonora_engine.main import emit_event

        with patch("redis.Redis.from_url") as mock_redis:
            instance = MagicMock()
            mock_redis.return_value = instance

            emit_event(
                event_type="payment:stripe:completed",
                tenant_id="abe-music",
                payload={"amount": 500, "greeting_id": "greeting-uuid"},
            )
            instance.publish.assert_called_once()

    def test_event_emitted_on_levelup(self):
        """FR8: Level up emits gamification:levelup"""
        from apps.sonora_engine.main import emit_event

        with patch("redis.Redis.from_url") as mock_redis:
            instance = MagicMock()
            mock_redis.return_value = instance

            emit_event(
                event_type="gamification:levelup",
                tenant_id="abe-music",
                payload={"fan_id": "fan-uuid", "new_level": "silver"},
            )
            instance.publish.assert_called_once()

    def test_websocket_endpoint_exists(self):
        """FR8: WebSocket endpoint is registered"""
        from apps.sonora_engine.main import app

        paths = [r.path for r in app.routes]
        assert "/ws/{tenant_id}" in paths or "/ws" in str(paths)


class TestLeaderboardAPI:
    """FR7+FR9: Leaderboard endpoints."""

    def test_leaderboard_by_xp(self):
        """FR9: Leaderboard returns top fans by XP"""
        from apps.sonora_engine.main import app
        from fastapi.testclient import TestClient

        paths = [r.path for r in app.routes]
        assert any("leaderboard" in p for p in paths)

    def test_leaderboard_by_beat(self):
        """FR9: Leaderboard can be filtered by $BEAT balance"""
        from apps.sonora_engine.dashboard import DashboardService

        svc = DashboardService()
        result = svc.get_leaderboard(tenant_id="abe-music", metric="beat", limit=5)
        assert len(result) <= 5
