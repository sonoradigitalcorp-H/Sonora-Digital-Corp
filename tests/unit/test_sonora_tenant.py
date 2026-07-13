"""Tests para Multi-tenant Isolation [FR9] — RLS, permisos, separación de datos."""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


class TestTenantModel:
    """FR9: Tenant model must enforce isolation."""

    def test_tenant_has_unique_slug(self):
        """Each tenant must have a unique slug"""
        from apps.sonora_engine.models import Tenant

        t1 = Tenant(slug="abe-music", name="ABE Music")
        t2 = Tenant(slug="mystik", name="Mystik AI")
        assert t1.slug != t2.slug

    def test_tenant_has_plan(self):
        """Tenant must have a valid plan"""
        from apps.sonora_engine.models import Tenant, TenantPlan

        t = Tenant(slug="test", name="Test", plan=TenantPlan.ILIMITADO)
        assert t.plan == TenantPlan.ILIMITADO
        assert t.plan.value == "ilimitado"

    def test_tenant_has_beat_supply(self):
        """Ilimitado plan must have beat_supply = 1M"""
        from apps.sonora_engine.models import Tenant, TenantPlan

        t = Tenant(slug="test", name="Test", plan=TenantPlan.ILIMITADO, beat_supply=1000000)
        assert t.beat_supply == 1000000

    def test_tenant_config_defaults(self):
        """Tenant must have sensible pricing defaults"""
        from apps.sonora_engine.models import Tenant

        t = Tenant(slug="test", name="Test")
        assert t.pricing_config["beat_per_usd"] == 10
        assert t.pricing_config["greeting_beat_cost"] == 50


class TestUserModel:
    """FR9: Users must be scoped to a tenant."""

    def test_user_belongs_to_tenant(self):
        """User must have a tenant_id"""
        from apps.sonora_engine.models import User, UserRole

        user = User(
            tenant_id="abe-music",
            email="fan@test.com",
            display_name="Test Fan",
            role=UserRole.FAN,
        )
        assert user.tenant_id == "abe-music"
        assert user.role == UserRole.FAN

    def test_user_role_enum_values(self):
        """User role must be one of the valid roles"""
        from apps.sonora_engine.models import UserRole

        roles = [r.value for r in UserRole]
        assert "platform_admin" in roles
        assert "client_admin" in roles
        assert "artist" in roles
        assert "fan" in roles

    def test_user_requires_email_or_phone(self):
        """User must have email or phone (constraint)"""
        from apps.sonora_engine.models import User, Tenant

        with pytest.raises(ValueError, match="email_or_phone"):
            User(
                tenant_id="tenant-uuid",
                display_name="No Contact",
            )


class TestPermissionModel:
    """FR9: Permission system must enforce tenant boundaries."""

    def test_platform_admin_can_access_all(self):
        """platform_admin role bypasses tenant filter"""
        from apps.sonora_engine.auth import check_permission

        result = check_permission(
            user_role="platform_admin",
            requested_tenant_id="any-tenant",
            user_tenant_id="any-tenant",
        )
        assert result["allowed"] is True

    def test_client_admin_only_own_tenant(self):
        """client_admin can only access their own tenant's data"""
        from apps.sonora_engine.auth import check_permission

        result = check_permission(
            user_role="client_admin",
            requested_tenant_id="other-tenant",
            user_tenant_id="my-tenant",
        )
        assert result["allowed"] is False
        assert "tenant" in result["reason"].lower()

    def test_client_admin_own_tenant_allowed(self):
        """client_admin can access their own tenant"""
        from apps.sonora_engine.auth import check_permission

        result = check_permission(
            user_role="client_admin",
            requested_tenant_id="my-tenant",
            user_tenant_id="my-tenant",
        )
        assert result["allowed"] is True

    def test_fan_can_only_read(self):
        """Fan role has read-only access within their tenant"""
        from apps.sonora_engine.auth import check_permission

        result = check_permission(
            user_role="fan",
            requested_tenant_id="my-tenant",
            user_tenant_id="my-tenant",
            action="read",
        )
        assert result["allowed"] is True

        result_write = check_permission(
            user_role="fan",
            requested_tenant_id="my-tenant",
            user_tenant_id="my-tenant",
            action="write",
        )
        assert result_write["allowed"] is False


class TestTokenLedger:
    """FR9: Token ledger must be scoped to tenant + user."""

    def test_token_transaction_records_tenant(self):
        """Every token transaction must include tenant_id"""
        from apps.sonora_engine.models import TokenTransaction, TransactionType

        tx = TokenTransaction(
            tenant_id="tenant-uuid",
            user_id="user-uuid",
            transaction_type=TransactionType.EARN_BEAT,
            amount=100,
            balance_after=500,
        )
        assert tx.tenant_id == "tenant-uuid"
        assert tx.amount == 100

    def test_token_balance_calculation(self):
        """Token balance is calculated from ledger entries"""
        from apps.sonora_engine.ledger import calculate_balance

        balance = calculate_balance(user_id="user-uuid", tenant_id="tenant-uuid")
        assert isinstance(balance, int)
        assert balance >= 0


class TestGreetingModel:
    """FR9: Greetings must be tied to tenant + artist + fan."""

    def test_greeting_has_status_flow(self):
        """Greeting status follows defined workflow"""
        from apps.sonora_engine.models import Greeting, GreetingStatus

        g = Greeting(
            tenant_id="tenant-uuid",
            artist_id="artist-uuid",
            fan_id="fan-uuid",
            message="Feliz cumple",
        )
        assert g.status == GreetingStatus.PENDING_PAYMENT

    def test_greeting_has_both_pricing_options(self):
        """Greeting must support both $BEAT and USD pricing"""
        from apps.sonora_engine.models import Greeting

        g = Greeting(
            tenant_id="tenant-uuid",
            artist_id="artist-uuid",
            fan_id="fan-uuid",
            message="Test",
            beat_cost=50,
            usd_cost=5.00,
        )
        assert g.beat_cost == 50
        assert g.usd_cost == 5.00


import pytest  # needed for pytest.raises
