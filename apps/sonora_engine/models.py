"""Pydantic data models for Sonora OS [FR3, FR9]."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TenantPlan(str, Enum):
    LANZAMIENTO = "lanzamiento"
    CRECIMIENTO = "crecimiento"
    ILIMITADO = "ilimitado"
    ENTERPRISE = "enterprise"


class UserRole(str, Enum):
    PLATFORM_ADMIN = "platform_admin"
    CLIENT_ADMIN = "client_admin"
    ARTIST = "artist"
    FAN = "fan"


class GreetingStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAID = "paid"
    GENERATING = "generating"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"
    REFUNDED = "refunded"


class TransactionType(str, Enum):
    EARN_BEAT = "earn_beat"
    BURN_BEAT = "burn_beat"
    TRANSFER_BEAT = "transfer_beat"
    STRIPE_PAYMENT = "stripe_payment"
    STRIPE_PAYOUT = "stripe_payout"
    REWARD = "reward"
    REFERRAL = "referral"


class QuestCategory(str, Enum):
    PLAY = "play"
    WORK = "work"
    LEARN = "learn"


class QuestFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


@dataclass
class Tenant:
    slug: str
    name: str
    plan: TenantPlan = TenantPlan.LANZAMIENTO
    is_active: bool = True
    beat_supply: int = 0
    config: dict = field(default_factory=dict)
    branding: dict = field(default_factory=lambda: {"primary_color": "#6366f1", "logo_url": None})
    pricing_config: dict = field(default_factory=lambda: {
        "beat_per_usd": 10,
        "greeting_beat_cost": 50,
        "greeting_usd_cost": 5,
    })


@dataclass
class User:
    tenant_id: str
    display_name: str
    email: str | None = None
    phone: str | None = None
    role: UserRole = UserRole.FAN
    is_active: bool = True

    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("email_or_phone: User must have email or phone")


@dataclass
class Greeting:
    tenant_id: str
    artist_id: str
    fan_id: str
    message: str
    status: GreetingStatus = GreetingStatus.PENDING_PAYMENT
    beat_cost: int = 0
    usd_cost: float = 0.0
    ai_generated: bool = False


@dataclass
class TokenTransaction:
    tenant_id: str
    user_id: str
    transaction_type: TransactionType
    amount: int
    balance_after: int
    reference_type: str | None = None
    reference_id: str | None = None
