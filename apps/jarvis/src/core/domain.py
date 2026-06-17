from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskProfile(str, Enum):
    EXPLORADOR = "explorador"
    CONQUISTADOR = "conquistador"
    AGENTE_IA = "agente_ia"
    IMPERIO = "imperio"


class PaymentProvider(str, Enum):
    MERCADO_PAGO = "mercadopago"
    BITSO = "bitso"
    SPEI = "spei"


class PaymentCurrency(str, Enum):
    MXN = "MXN"
    USD = "USD"
    USDC = "USDC"
    BTC = "BTC"
    USDT = "USDT"


class Niche(str, Enum):
    MUSICA = "musica"
    FITNESS = "fitness"
    CREATIVO = "creativo"
    EDUCACION = "educacion"
    ECOMMERCE = "ecommerce"
    ADULTO = "adulto"
    GENERAL = "general"


class OnboardingStep(str, Enum):
    BIENVENIDA = "bienvenida"
    PERSONA = "persona"
    NECESIDADES = "necesidades"
    PLAN = "plan"
    CONFIRMACION = "confirmacion"


@dataclass(frozen=True)
class SPEIAccount:
    bank: str
    clabe: str
    holder: str
    currency: str
    payment_type: str = "spei"


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    price_mxn: int
    price_usd: int
    features: tuple[str, ...] = ()


@dataclass(frozen=True)
class PaymentResult:
    status: str
    plan: str
    provider: str
    niche: str
    reference: Optional[str] = None
    created_at: str = ""


@dataclass(frozen=True)
class Transaction:
    tx_id: str
    plan: str
    provider: str
    amount: float
    currency: str
    status: str
    created_at: datetime
