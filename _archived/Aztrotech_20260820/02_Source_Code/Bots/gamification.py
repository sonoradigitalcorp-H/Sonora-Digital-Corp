"""Gamificación Play & Learn to Earn — sistema de puntos, badges, affiliate para Aztrotech.

Paquetes (determinado, por contrato, precios fijos del OKF):
  1. Starter AI Agent    $999 USD  → 1000 pts/mes activos
  2. Growth AI Agent     $1999 USD → 2500 pts/mes + CRM
  3. Enterprise AI Agent $3999 USD → 5000 pts/mes + 3D + voice clone

Points earned:
  - Lead generado: +5 pts (cold), +10 (warm), +25 (hot)
  - Survey completado: +3 pts
  - Cita agendada: +15 pts
  - Cita asistida: +50 pts
  - Venta cerrada: +100 pts
  - Referido con conversión: +100 pts

Affiliate:
  - Cada lead hot calificado → código único → 5% cashback en próximo paquete
  - Referidos con tracking de cookies 30 días

Usage:
    from gamification import GamificationEngine
    gam = GamificationEngine()
    gam.award_points(user_id, 25, "hot_lead")
    badge = gam.check_badges(user_id)
    affiliate_link = gam.generate_referral_link(user_id)
"""
import json
import hashlib
import logging
import shortuuid
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

import asyncpg

logger = logging.getLogger(__name__)

# Config desde sdc_config o fallback
try:
    from sdc_config import get_config
    _db_url = get_config().database_url
except (ImportError, ModuleNotFoundError):
    _db_url = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")

# Points por acción
POINTS = {
    "cold_lead": 5,
    "warm_lead": 10,
    "hot_lead": 25,
    "survey_completed": 3,
    "cita_agendada": 15,
    "cita_asistida": 50,
    "venta_cerrada": 100,
    "referido_convertido": 100,
    "engagement_0.5": 5,
    "engagement_0.7": 10,
    "engagement_0.9": 15,
}

# Badges (desbloqueados por milestone)
BADGES = {
    "lead_miner": {"name": "⛏️ Lead Miner", "threshold": 10, "desc": "Generaste 10 leads"},
    "conversion_king": {"name": "👑 Conversion King", "threshold": 50, "desc": "50 leads generados"},
    "hot_streak": {"name": "🔥 Hot Streak", "threshold": 5, "desc": "5 leads hot consecutivos"},
    "trusted_advisor": {"name": "🤝 Trusted Advisor", "threshold": 100, "desc": "100 pts totales"},
    "growth_hacker": {"name": "🚀 Growth Hacker", "threshold": 250, "desc": "250 pts totales"},
    "sales_machine": {"name": "💰 Sales Machine", "threshold": 500, "desc": "500 pts totales"},
    "affiliate_pro": {"name": "🔗 Affiliate Pro", "threshold": 1, "desc": "Generaste tu primer referido", "metric": "referrals"},
}

# Paquetes con precios fijos (del OKF)
PAQUETES = {
    "starter": {
        "nombre": "Starter AI Agent",
        "precio_usd": 999,
        "precio_mxn": 18000,
        "puntos_mensuales": 1000,
        "features": ["Empleado Digital 24/7", "Auto-respuesta + captura leads básica", "Panel web simple", "Setup 5 días"],
        "affiliate_pct": 0.05,
    },
    "growth": {
        "nombre": "Growth AI Agent",
        "precio_usd": 1999,
        "precio_mxn": 36000,
        "puntos_mensuales": 2500,
        "features": ["Todo Starter", "WhatsApp Business API + Instagram + Messenger", "CRM + scoring automático", "Landing page personalizada", "Soporte 24/7 con voz"],
        "affiliate_pct": 0.05,
    },
    "enterprise": {
        "nombre": "Enterprise AI Agent",
        "precio_usd": 3999,
        "precio_mxn": 72000,
        "puntos_mensuales": 5000,
        "features": ["Todo Growth", "Agentes multi-nicho", "Voz clonada oficial", "Landing page 3D", "Pipeline voz completo", "Soporte dedicado + entrenamiento"],
        "affiliate_pct": 0.05,
    },
}


@dataclass
class UserGamification:
    internal_user_id: str
    puntos_totales: int = 0
    badges: List[str] = field(default_factory=list)
    paquete_actual: Optional[str] = None
    referidos: List[str] = field(default_factory=list)
    referral_code: Optional[str] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)


class GamificationEngine:
    """Gestiona puntos, badges, affiliate links, paquetes."""

    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._init_tables()

    def _init_tables(self):
        """Create gamification tables if not exist (non-blocking, will be created via SQL too)."""
        pass  # Tables created via SQL migration

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(_db_url, min_size=1, max_size=5)
        return self._pool

    async def award_points(
        self,
        internal_user_id: str,
        points: int,
        reason: str,
        platform: str = "telegram",
    ) -> int:
        """Award points to a user for a specific action."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            # Get or create user record
            row = await conn.fetchrow(
                "SELECT puntos_totales, badges, referral_code FROM user_gamification WHERE internal_user_id = $1",
                internal_user_id,
            )
            if row:
                new_total = (row["puntos_totales"] or 0) + points
                badges = row["badges"] or []
                ref_code = row["referral_code"] or self._generate_referral_code(internal_user_id)
                await conn.execute(
                    """UPDATE user_gamification
                       SET puntos_totales = $1, last_updated = NOW()
                       WHERE internal_user_id = $2""",
                    new_total, internal_user_id,
                )
            else:
                new_total = points
                badges = []
                ref_code = self._generate_referral_code(internal_user_id)
                await conn.execute(
                    """INSERT INTO user_gamification
                       (internal_user_id, puntos_totales, badges, referral_code, created_at, last_updated)
                       VALUES ($1, $2, $3, $4, NOW(), NOW())""",
                    internal_user_id, new_total, json.dumps(badges), ref_code,
                )

            # Log the point event
            await conn.execute(
                """INSERT INTO points_log (internal_user_id, points, reason, platform, awarded_at)
                   VALUES ($1, $2, $3, $4, NOW())""",
                internal_user_id, points, reason, platform,
            )

            # Check for new badges
            new_badges = await self.check_badges(internal_user_id, new_total, reason)

        return new_total

    def _generate_referral_code(self, internal_user_id: str) -> str:
        """Generate unique referral code from user ID."""
        prefix = hashlib.md5(internal_user_id.encode()).hexdigest()[:4].upper()
        suffix = shortuuid.ShortUUID().random(length=4).upper()
        return f"{prefix}-{suffix}"

    async def check_badges(
        self,
        internal_user_id: str,
        puntos_totales: int,
        trigger_reason: str = None,
    ) -> List[str]:
        """Check if user has unlocked new badges."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT badges FROM user_gamification WHERE internal_user_id = $1",
                internal_user_id,
            )
            current_badges = set(json.loads(row["badges"] or "[]")) if row else set()

            # Get lead count for this user
            lead_count = await conn.fetchval(
                """SELECT COUNT(DISTINCT c.id) FROM conversations c
                   WHERE c.internal_user_id = $1::uuid""",
                internal_user_id,
            ) or 0

            new_badges = []

            # Badge checks
            if lead_count >= BADGES["lead_miner"]["threshold"] and "lead_miner" not in current_badges:
                new_badges.append("lead_miner")
            if lead_count >= BADGES["conversion_king"]["threshold"] and "conversion_king" not in current_badges:
                new_badges.append("conversion_king")
            if puntos_totales >= BADGES["trusted_advisor"]["threshold"] and "trusted_advisor" not in current_badges:
                new_badges.append("trusted_advisor")
            if puntos_totales >= BADGES["growth_hacker"]["threshold"] and "growth_hacker" not in current_badges:
                new_badges.append("growth_hacker")
            if puntos_totales >= BADGES["sales_machine"]["threshold"] and "sales_machine" not in current_badges:
                new_badges.append("sales_machine")

            if new_badges:
                all_badges = current_badges | set(new_badges)
                await conn.execute(
                    "UPDATE user_gamification SET badges = $1, last_updated = NOW() WHERE internal_user_id = $2",
                    json.dumps(list(all_badges)), internal_user_id,
                )
                for b in new_badges:
                    logger.info(f"Badge unlocked: {b} for user {internal_user_id}")

        return new_badges

    def generate_referral_link(self, internal_user_id: str, paquete: str = "starter") -> str:
        """Genera enlace de afiliado para compartir."""
        pool = None  # Sync method
        code = self._generate_referral_code(internal_user_id)
        base_url = os.getenv("SDC_BASE_URL", "https://aztrotech.mx")
        return f"{base_url}/ref/{code}?paquete={paquete}"

    async def get_user_status(self, internal_user_id: str) -> Dict[str, Any]:
        """Get gamification status for a user."""
        pool = await self._get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """SELECT u.*, ui.display_name, ui.business_name, ui.lead_type, ui.lead_confidence
                   FROM user_gamification u
                   LEFT JOIN user_identities ui ON ui.internal_id = u.internal_user_id::uuid
                   WHERE u.internal_user_id = $1""",
                internal_user_id,
            )
            if not row:
                return {"puntos_totales": 0, "badges": [], "paquete_actual": None, "referral_code": None}

            badges = json.loads(row["badges"] or "[]")
            badge_details = [BADGES.get(b, {"name": b, "desc": b}) for b in badges]
            ref_code = row["referral_code"]
            ref_link = f"https://aztrotech.mx/ref/{ref_code}?paquete=starter" if ref_code else None

            # Calculate next badge threshold
            next_threshold = None
            for key, badge in BADGES.items():
                if key.startswith("lead_") or key == "conversion_king":
                    continue
                if badge["threshold"] > row["puntos_totales"] and not next_threshold:
                    next_threshold = badge["threshold"]

            return {
                "puntos_totales": row["puntos_totales"] or 0,
                "badges": badge_details,
                "paquete_actual": row["paquete_actual"],
                "referral_code": ref_code,
                "referral_link": ref_link,
                "next_badge_at": next_threshold,
                "points_to_next": next_threshold - (row["puntos_totales"] or 0) if next_threshold else 0,
                "nombre": row["display_name"],
                "business": row["business_name"],
            }

    def get_paquetess(self) -> Dict[str, Any]:
        """Return all available packages with prices (from OKF)."""
        return PAQUETES


def create_gamification_engine() -> GamificationEngine:
    return GamificationEngine()
