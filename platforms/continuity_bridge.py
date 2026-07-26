#!/usr/bin/env python3
"""ContinuityBridge — shared bridge that all 4 channels (Telegram, WhatsApp, Web, Voice) import to maintain unified session context.

Usage:
    from platforms.continuity_bridge import ContinuityBridge
    bridge = ContinuityBridge()

    # Get unified context from any channel
    context = bridge.get_context(telegram_user_id, "telegram")

    # Save interaction from any channel
    bridge.save_interaction(telegram_user_id, "telegram", "Hello", "Hi there!")

    # Link two identities
    bridge.link_identities("12345", "+521555010203", "telegram", "whatsapp")
"""

import logging
from typing import Any, Optional

from src.core.engram import engram
from src.core.mem_sabe import MemSabe
from src.core.session_orchestrator import SessionOrchestrator

log = logging.getLogger(__name__)

_orchestrator: Optional[SessionOrchestrator] = None


def _get_orchestrator() -> SessionOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        mem_sabe = MemSabe(engram)
        _orchestrator = SessionOrchestrator(engram, mem_sabe)
    return _orchestrator


class ContinuityBridge:
    """Bridge that all 4 channels import to share context, maintain session continuity, and link identities across platforms."""

    def __init__(self) -> None:
        self.orchestrator = _get_orchestrator()

    def get_context(self, user_identifier: str, channel: str) -> dict:
        """Get unified cross-channel context for a user from any channel.

        :param user_identifier: Channel-specific user identifier (Telegram ID, WhatsApp phone, etc.)
        :param channel: Source channel (telegram, whatsapp, web, voice)
        :return: Dict with unified context including cross-channel history, topics, preferences
        """
        unified_id = self.get_unified_user_id(user_identifier, channel)
        session = self.orchestrator.start_session(unified_id, channel)
        return {
            "unified_user_id": unified_id,
            "session_id": session.session_id,
            "channel": channel,
            "cross_channel_context": session.context,
            "active_channels": session.context.get("channels", []),
            "topics": session.context.get("topics", []),
            "pending": session.context.get("pending", []),
            "preferences": session.context.get("preferences", {}),
        }

    def save_interaction(
        self,
        user_identifier: str,
        channel: str,
        message: str,
        response: str,
        topic: Optional[str] = None,
        intent: Optional[str] = None,
    ) -> bool:
        """Record an interaction from any channel into the unified memory.

        :param user_identifier: Channel-specific user identifier
        :param channel: Source channel
        :param message: User message text
        :param response: System response text
        :param topic: Optional topic classification
        :param intent: Optional intent classification
        :return: True if saved successfully
        """
        try:
            unified_id = self.get_unified_user_id(user_identifier, channel)
            self.orchestrator.record_interaction(
                unified_user_id=unified_id,
                channel=channel,
                message=message,
                response=response,
                topic=topic,
                intent=intent,
            )
            return True
        except Exception as e:
            log.warning("Failed to save interaction for %s on %s: %s", user_identifier, channel, e)
            return False

    def get_unified_user_id(self, user_identifier: str, channel: str) -> str:
        """Resolve any channel-specific identifier to a unified user ID.

        :param user_identifier: Channel-specific identifier
        :param channel: Source channel
        :return: Unified user ID (UUID string)
        """
        return self.orchestrator.identify_user(
            channel_user_id=str(user_identifier),
            channel=channel,
        )

    def link_identities(
        self,
        primary_id: str,
        secondary_id: str,
        primary_channel: str,
        secondary_channel: str,
    ) -> bool:
        """Link two identities from different channels as the same user.

        :param primary_id: First channel user ID
        :param secondary_id: Second channel user ID
        :param primary_channel: First channel name
        :param secondary_channel: Second channel name
        :return: True if linked successfully
        """
        return self.orchestrator.link_identities(
            primary_id=primary_id,
            secondary_id=secondary_id,
            primary_channel=primary_channel,
            secondary_channel=secondary_channel,
        )

    def get_recent_history(
        self,
        user_identifier: str,
        channel: str,
        channels_filter: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get recent interaction history, optionally filtered by channels.

        :param user_identifier: Channel-specific identifier
        :param channel: Source channel for resolution
        :param channels_filter: Optional list of channels to include
        :param limit: Max results
        :return: List of interaction dicts
        """
        unified_id = self.get_unified_user_id(user_identifier, channel)
        return self.orchestrator.get_recent_history(unified_id, channels=channels_filter, limit=limit)
