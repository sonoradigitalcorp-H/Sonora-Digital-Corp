"""Onboarding flow for Agent Galaxy backend.

Manages the QR-based onboarding session:
1. Client requests onboarding → receives session_id + QR data
2. User scans QR on phone and enters phone number
3. Client completes onboarding → tenant created, agents assigned

Sessions expire after a configurable timeout (default: 10 minutes).
"""

import logging
import os
import time
import uuid
from typing import Optional

from events import GalaxyEvent, event_logger
from models import OnboardingStartResponse, OnboardingCompleteResponse, Tenant
from tenant import TenantStore, tenant_store

log = logging.getLogger("galaxy.onboarding")

SESSION_EXPIRY_SECONDS = int(os.getenv("GALAXY_ONBOARDING_EXPIRY", "600"))


class OnboardingManager:
    """Manages onboarding sessions with in-memory storage and expiry."""

    def __init__(self, store: Optional[TenantStore] = None):
        self.store = store or tenant_store
        self._sessions: dict[str, dict] = {}

    def start_session(self) -> OnboardingStartResponse:
        """Create a new onboarding session.

        Returns:
            Session ID, QR payload, and expiration timestamp.
        """
        session_id = str(uuid.uuid4())
        qr_data = f"https://wa.me/qr/{session_id[:16]}"
        expires_at = time.time() + SESSION_EXPIRY_SECONDS

        self._sessions[session_id] = {
            "session_id": session_id,
            "qr_data": qr_data,
            "expires_at": expires_at,
            "status": "pending",
            "created_at": time.time(),
        }

        event_logger.emit(GalaxyEvent(
            event_type="galaxy_onboarding_started",
            data={"session_id": session_id},
        ))

        log.info(f"Onboarding session started: {session_id}")
        return OnboardingStartResponse(
            session_id=session_id,
            qr_data=qr_data,
            expires_at=str(expires_at),
            status="pending",
        )

    def complete_session(
        self,
        session_id: str,
        phone: str,
        name: str = "",
        plan: str = "explorador",
    ) -> OnboardingCompleteResponse:
        """Complete an onboarding session by creating a tenant.

        Args:
            session_id: The onboarding session to complete.
            phone: Customer phone number.
            name: Customer display name.
            plan: Selected plan tier.

        Returns:
            Tenant ID and assigned agents.

        Raises:
            ValueError: If session is invalid or expired.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")
        if session["status"] != "pending":
            raise ValueError(f"Session already processed: {session_id}")
        if time.time() > session["expires_at"]:
            del self._sessions[session_id]
            raise ValueError(f"Session expired: {session_id}")

        tenant = self.store.create(phone=phone, plan=plan, name=name)
        session["status"] = "completed"
        session["tenant_id"] = tenant.id

        event_logger.emit(GalaxyEvent(
            event_type="galaxy_onboarding_completed",
            tenant_id=tenant.id,
            data={
                "session_id": session_id,
                "phone": phone,
                "plan": plan,
                "agents": tenant.agents,
            },
        ))

        log.info(f"Onboarding completed: session={session_id} tenant={tenant.id}")
        return OnboardingCompleteResponse(
            tenant_id=tenant.id,
            status="active",
            agents=tenant.agents,
            message=f"Bienvenido a tu galaxia, {name or 'explorador'}! Tienes {len(tenant.agents)} agentes activos.",
        )

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session details."""
        session = self._sessions.get(session_id)
        if not session:
            return None
        if time.time() > session["expires_at"]:
            del self._sessions[session_id]
            return None
        return session

    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count of removed sessions."""
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now > s["expires_at"]]
        for sid in expired:
            del self._sessions[sid]
        if expired:
            log.info(f"Cleaned up {len(expired)} expired onboarding sessions")
        return len(expired)


onboarding_manager = OnboardingManager()
