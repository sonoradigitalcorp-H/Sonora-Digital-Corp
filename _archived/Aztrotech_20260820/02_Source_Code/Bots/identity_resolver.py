"""Cross-Canal Identity Resolver — Maps WhatsApp/Telegram/Web to unified internal user."""

import re
import json
import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

import asyncpg
from pydantic import EmailStr

from models.identity import (
    InternalUser, IdentityCreate, IdentityResolutionResult,
    Platform, LeadType, IdentityRow
)

logger = logging.getLogger(__name__)


def _j(value) -> str:
    """Serialize dict/list to JSON string for JSONB columns (asyncpg needs str)."""
    if value is None:
        return None
    return json.dumps(value, ensure_ascii=False, default=str)


class IdentityResolver:
    """Resolves platform-specific IDs to canonical internal users with merge logic."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def resolve_user(
        self,
        platform: Platform,
        platform_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IdentityResolutionResult:
        """
        Resolve or create a canonical internal user.
        
        Strategy:
        1. Exact match on (platform, platform_id)
        2. Fuzzy match on phone_e164 (normalized)
        3. Fuzzy match on email
        4. Create new if no match
        """
        metadata = metadata or {}
        norm_phone = self._normalize_phone(metadata.get("phone")) if metadata.get("phone") else None
        norm_email = metadata.get("email", "").lower().strip() if metadata.get("email") else None

        async with self.pool.acquire() as conn:
            # 1. Exact match
            row = await conn.fetchrow(
                "SELECT * FROM user_identities WHERE platform=$1 AND platform_id=$2 AND merged_into IS NULL",
                platform.value, platform_id
            )
            if row:
                user = self._row_to_user(row)
                await self._touch_user(conn, user.internal_id, metadata)
                return IdentityResolutionResult(user=user, is_new=False, merged=False)

            # 2. Phone match (cross-platform)
            if norm_phone:
                row = await conn.fetchrow(
                    """SELECT * FROM user_identities 
                       WHERE phone_e164=$1 AND merged_into IS NULL""",
                    norm_phone
                )
                if row:
                    return await self._merge_into_existing(conn, row, platform, platform_id, metadata, "phone_match")

            # 3. Email match (cross-platform)
            if norm_email:
                row = await conn.fetchrow(
                    """SELECT * FROM user_identities 
                       WHERE email=$1 AND merged_into IS NULL""",
                    norm_email
                )
                if row:
                    return await self._merge_into_existing(conn, row, platform, platform_id, metadata, "email_match")

            # 4. Create new
            return await self._create_new(conn, platform, platform_id, metadata)

    async def _merge_into_existing(
        self,
        conn: asyncpg.Connection,
        existing_row: asyncpg.Record,
        platform: Platform,
        platform_id: str,
        metadata: Dict[str, Any],
        reason: str
    ) -> IdentityResolutionResult:
        """Merge new platform identity into existing canonical user."""
        existing_user = self._row_to_user(existing_row)
        new_internal_id = UUID(existing_row["internal_id"])

        # Insert new identity row pointing to existing canonical
        await conn.execute(
            """INSERT INTO user_identities 
               (internal_id, platform, platform_id, display_name, phone_e164, email, locale, metadata, merged_into)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $1)""",
            new_internal_id, platform.value, platform_id,
            metadata.get("display_name"),
            self._normalize_phone(metadata.get("phone")) if metadata.get("phone") else None,
            metadata.get("email", "").lower().strip() if metadata.get("email") else None,
            metadata.get("locale", "es"),
            _j(metadata),
        )

        # Update canonical user with enriched data
        await self._enrich_user(conn, new_internal_id, metadata)

        user = await self.get_user_by_id(new_internal_id)
        logger.info(f"Merged {platform.value}:{platform_id} into {new_internal_id} (reason: {reason})")
        return IdentityResolutionResult(
            user=user, is_new=True, merged=True, merged_from=new_internal_id
        )

    async def _create_new(
        self,
        conn: asyncpg.Connection,
        platform: Platform,
        platform_id: str,
        metadata: Dict[str, Any]
    ) -> IdentityResolutionResult:
        """Create new canonical user with initial identity."""
        from uuid import uuid4
        internal_id = uuid4()
        norm_phone = self._normalize_phone(metadata.get("phone")) if metadata.get("phone") else None
        norm_email = metadata.get("email", "").lower().strip() if metadata.get("email") else None

        await conn.execute(
            """INSERT INTO user_identities 
               (internal_id, platform, platform_id, display_name, phone_e164, email, locale, metadata)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            internal_id, platform.value, platform_id,
            metadata.get("display_name"),
            norm_phone,
            norm_email,
            metadata.get("locale", "es"),
            _j(metadata),
        )

        user = await self.get_user_by_id(internal_id)
        logger.info(f"Created new user {internal_id} for {platform.value}:{platform_id}")
        return IdentityResolutionResult(user=user, is_new=True, merged=False)

    async def _enrich_user(
        self,
        conn: asyncpg.Connection,
        internal_id: UUID,
        metadata: Dict[str, Any]
    ) -> None:
        """Enrich canonical user profile from conversation metadata."""
        updates = []
        params = [internal_id]
        param_idx = 2

        if metadata.get("business_name"):
            updates.append(f"business_name = ${param_idx}")
            params.append(metadata["business_name"])
            param_idx += 1
        if metadata.get("business_type"):
            updates.append(f"business_type = ${param_idx}")
            params.append(metadata["business_type"])
            param_idx += 1
        if metadata.get("pain_points"):
            updates.append(f"pain_points = ${param_idx}")
            params.append(_j(metadata["pain_points"]))
            param_idx += 1
        if metadata.get("budget_range"):
            updates.append(f"budget_range = ${param_idx}")
            params.append(metadata["budget_range"])
            param_idx += 1
        if metadata.get("timeline"):
            updates.append(f"timeline = ${param_idx}")
            params.append(metadata["timeline"])
            param_idx += 1

        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE user_identities SET {', '.join(updates)} WHERE internal_id = $1"
            await conn.execute(query, *params)

    async def _touch_user(
        self,
        conn: asyncpg.Connection,
        internal_id: UUID,
        metadata: Dict[str, Any]
    ) -> None:
        """Update last_interaction and conversation_count."""
        await conn.execute(
            """UPDATE user_identities 
               SET conversation_count = conversation_count + 1,
                   last_interaction = NOW(),
                   updated_at = NOW()
               WHERE internal_id = $1""",
            internal_id
        )
        await self._enrich_user(conn, internal_id, metadata)

    async def get_user_by_id(self, internal_id: UUID) -> Optional[InternalUser]:
        """Fetch canonical user by internal_id."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_identities WHERE internal_id = $1 AND merged_into IS NULL",
                internal_id
            )
            if row:
                return self._row_to_user(row)
        return None

    async def get_user_by_platform(self, platform: Platform, platform_id: str) -> Optional[InternalUser]:
        """Fetch canonical user by platform identity."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM user_identities WHERE platform = $1 AND platform_id = $2 AND merged_into IS NULL",
                platform.value, platform_id
            )
            if row:
                return self._row_to_user(row)
        return None

    async def merge_users(self, primary_id: UUID, secondary_id: UUID, reason: str = "manual") -> InternalUser:
        """Manually merge two canonical users (primary absorbs secondary)."""
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Update secondary's identities to point to primary
                await conn.execute(
                    "UPDATE user_identities SET merged_into = $1 WHERE internal_id = $2 OR merged_into = $2",
                    primary_id, secondary_id
                )
                # Merge enriched data (primary wins, but fill gaps from secondary)
                primary = await self.get_user_by_id(primary_id)
                secondary = await self.get_user_by_id(secondary_id)
                if secondary:
                    await self._merge_enriched_data(conn, primary_id, secondary)
        return await self.get_user_by_id(primary_id)

    async def _merge_enriched_data(
        self,
        conn: asyncpg.Connection,
        primary_id: UUID,
        secondary: InternalUser
    ) -> None:
        """Fill gaps in primary from secondary."""
        updates = []
        params = [primary_id]
        param_idx = 2

        fields = [
            ("business_name", secondary.business_name),
            ("business_type", secondary.business_type),
            ("pain_points", secondary.pain_points),
            ("budget_range", secondary.budget_range),
            ("timeline", secondary.timeline),
        ]
        for field, value in fields:
            if value and not getattr(await self.get_user_by_id(primary_id), field, None):
                updates.append(f"{field} = ${param_idx}")
                params.append(value)
                param_idx += 1

        if updates:
            updates.append("updated_at = NOW()")
            query = f"UPDATE user_identities SET {', '.join(updates)} WHERE internal_id = $1"
            await conn.execute(query, *params)

    def _row_to_user(self, row: asyncpg.Record) -> InternalUser:
        """Convert DB row to InternalUser model."""
        def _parse_json(value, default):
            if value is None:
                return default
            if isinstance(value, (dict, list)):
                return value
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return default
        return InternalUser(
            internal_id=row["internal_id"],
            platform=Platform(row["platform"]),
            platform_id=row["platform_id"],
            display_name=row["display_name"],
            phone_e164=row["phone_e164"],
            email=row["email"],
            locale=row["locale"],
            metadata=_parse_json(row["metadata"], {}) or {},
            merged_into=row["merged_into"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            lead_type=LeadType(row["lead_type"]) if row["lead_type"] else None,
            lead_confidence=row["lead_confidence"] or 0.0,
            business_name=row["business_name"],
            business_type=row["business_type"],
            pain_points=_parse_json(row["pain_points"], []),
            budget_range=row["budget_range"],
            timeline=row["timeline"],
            preferred_contact=row["preferred_contact"],
            conversation_count=row["conversation_count"] or 0,
            last_interaction=row["last_interaction"],
        )

    @staticmethod
    def _normalize_phone(phone: Optional[str]) -> Optional[str]:
        """Normalize phone to E.164 format (+521XXXXXXXXXX for Mexico)."""
        if not phone:
            return None
        digits = re.sub(r"\D", "", phone)
        # Mexico: 52 + 1 + 10 digits = 13 digits
        if digits.startswith("521") and len(digits) == 13:
            return f"+{digits}"
        if digits.startswith("52") and len(digits) == 12:
            return f"+{digits}"
        if digits.startswith("1") and len(digits) == 11:  # US/Canada
            return f"+{digits}"
        if len(digits) == 10 and digits.startswith(("662", "663", "664")):  # Mexico local
            return f"+521{digits}"
        return f"+{digits}" if digits else None


# Factory function for easy initialization
async def create_identity_resolver(database_url: str) -> IdentityResolver:
    """Create IdentityResolver with connection pool."""
    pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    return IdentityResolver(pool)