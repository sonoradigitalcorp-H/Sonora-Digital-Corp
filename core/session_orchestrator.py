"""SessionOrchestrator — unified multi-channel session continuity across Telegram, WhatsApp, Web, and Voice."""

import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional

from src.core.engram import Engram
from src.core.mem_sabe import MemSabe

log = logging.getLogger(__name__)

CHANNELS = {"telegram", "whatsapp", "web", "voice"}

SESSION_TIMEOUT_MINUTES = 30


@dataclass
class ChannelSession:
    user_id: str
    channel: str
    session_id: str
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    context: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    @property
    def is_stale(self, timeout_minutes: int = SESSION_TIMEOUT_MINUTES) -> bool:
        return (time.time() - self.last_activity) > timeout_minutes * 60

    def touch(self) -> None:
        self.last_activity = time.time()


class SessionOrchestrator:
    """Maintains unified sessions across all channels using Engram for persistence and MemSabe for cross-channel context."""

    def __init__(self, engram_instance: Engram, mem_sabe_instance: MemSabe):
        self.engram = engram_instance
        self.mem_sabe = mem_sabe_instance
        self._active_sessions: dict[str, ChannelSession] = {}
        self._identity_map: dict[str, str] = {}

    def _query_by_tag_prefix(self, prefix: str) -> list[dict]:
        try:
            rows = self.engram._conn.execute(
                "SELECT * FROM memories WHERE tag LIKE ? ORDER BY created_at DESC",
                (f"{prefix}%",),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def _load_identity_map(self) -> dict[str, str]:
        identities = self._query_by_tag_prefix("identity:")
        mapping: dict[str, str] = {}
        for mem in identities:
            tag = mem.get("tag", "")
            if tag.startswith("identity:"):
                parts = tag.split(":", 2)
                if len(parts) == 3:
                    mapping[f"{parts[1]}:{parts[2]}"] = mem.get("spec_id", "")
        return mapping

    def _memories_for_user(self, unified_user_id: str) -> list[dict]:
        return self.engram.get_by_spec(unified_user_id)

    def _save_identity_link(self, unified_user_id: str, channel: str, channel_user_id: str) -> None:
        tag = f"identity:{channel}:{channel_user_id}"
        self.engram.store_learning(
            spec_id=unified_user_id,
            tag=tag,
            summary=f"Identity link: {channel}/{channel_user_id} -> {unified_user_id}",
            context=json.dumps({"unified_user_id": unified_user_id, "channel": channel, "channel_user_id": channel_user_id}),
            importance="high",
            layer="customer",
        )

    def identify_user(
        self,
        channel_user_id: str,
        channel: str,
        phone: Optional[str] = None,
        email: Optional[str] = None,
    ) -> str:
        """Resolve a channel-specific user ID to a unified user ID across all channels."""
        identity_key = f"{channel}:{channel_user_id}"
        if identity_key in self._identity_map:
            return self._identity_map[identity_key]

        persisted = self._load_identity_map()
        if identity_key in persisted:
            unified_id = persisted[identity_key]
            self._identity_map[identity_key] = unified_id
            return unified_id

        if phone:
            phone_key = f"phone:{phone}"
            if phone_key in persisted:
                unified_id = persisted[phone_key]
                self._identity_map[identity_key] = unified_id
                self._save_identity_link(unified_id, channel, channel_user_id)
                return unified_id

        if email:
            email_key = f"email:{email}"
            if email_key in persisted:
                unified_id = persisted[email_key]
                self._identity_map[identity_key] = unified_id
                self._save_identity_link(unified_id, channel, channel_user_id)
                return unified_id

        unified_id = str(uuid.uuid4())
        self._identity_map[identity_key] = unified_id
        self._save_identity_link(unified_id, channel, channel_user_id)
        if phone:
            self._save_identity_link(unified_id, "phone", phone)
        if email:
            self._save_identity_link(unified_id, "email", email)

        self.engram.store_learning(
            spec_id=unified_id,
            tag=f"user_profile:{channel}",
            summary=f"New user identified via {channel} ({channel_user_id})",
            context=json.dumps({
                "unified_user_id": unified_id,
                "first_channel": channel,
                "channel_user_id": channel_user_id,
                "phone": phone,
                "email": email,
            }),
            importance="high",
            layer="customer",
        )
        return unified_id

    def start_session(
        self,
        unified_user_id: str,
        channel: str,
        metadata: Optional[dict] = None,
    ) -> ChannelSession:
        """Start or resume a session on a given channel, loading cross-channel context automatically."""
        channel = channel.lower()
        if channel not in CHANNELS:
            raise ValueError(f"Unknown channel '{channel}'. Must be one of: {CHANNELS}")

        session_key = f"{unified_user_id}:{channel}"
        existing = self._active_sessions.get(session_key)

        if existing and not existing.is_stale:
            existing.touch()
            if metadata:
                existing.metadata.update(metadata)
            return existing

        session_id = str(uuid.uuid4())
        cross_channel = self.get_cross_channel_context(unified_user_id)

        session = ChannelSession(
            user_id=unified_user_id,
            channel=channel,
            session_id=session_id,
            context=cross_channel,
            metadata=metadata or {},
        )
        self._active_sessions[session_key] = session

        self.engram.store_learning(
            spec_id=unified_user_id,
            tag=f"session:{channel}",
            summary=f"Session started on {channel} (session_id={session_id})",
            context=json.dumps({
                "action": "session_start",
                "channel": channel,
                "session_id": session_id,
                "metadata": metadata,
            }),
            importance="medium",
            layer="working",
        )
        return session

    def get_cross_channel_context(self, unified_user_id: str) -> dict:
        """Retrieve complete cross-channel context for a user.

        Uses direct spec_id lookup (not FTS5) because user IDs are UUIDs
        that don't tokenize well in full-text search.
        """
        memories = self._memories_for_user(unified_user_id)

        channel_details: dict[str, dict] = {}
        topics: list[str] = []
        pending: list[str] = []
        preferences: dict[str, Any] = {}
        channel_set: set[str] = set()
        last_interactions: dict[str, Optional[dict]] = {}

        for mem in memories:
            tag = mem.get("tag", "")
            if ":" in tag:
                prefix = tag.split(":", 1)[0]
                value = tag.split(":", 1)[1] if len(tag.split(":", 1)) > 1 else ""
                if prefix in CHANNELS:
                    channel_set.add(prefix)
                if prefix == "interaction" and value in CHANNELS:
                    ch = value
                    channel_set.add(ch)
                    if ch not in channel_details:
                        channel_details[ch] = {"memory_count": 0, "recent": []}
                    channel_details[ch]["memory_count"] += 1
                    channel_details[ch]["recent"].append(mem)
                    last_interactions[ch] = mem

            ctx_str = mem.get("context", "")
            if ctx_str:
                try:
                    ctx_data = json.loads(ctx_str) if isinstance(ctx_str, str) else ctx_str
                    topic = ctx_data.get("topic")
                    if topic and topic not in topics:
                        topics.append(topic)
                    pend = ctx_data.get("pending")
                    if pend and pend not in pending:
                        pending.append(pend)
                    prefs = ctx_data.get("preferences")
                    if prefs:
                        preferences.update(prefs)
                except (json.JSONDecodeError, TypeError):
                    pass

        return {
            "user_id": unified_user_id,
            "channels": sorted(channel_set),
            "channel_details": channel_details,
            "memory_count": len(memories),
            "topics": topics,
            "pending": pending,
            "preferences": preferences,
            "last_interactions": {
                ch: (details["recent"][0] if details.get("recent") else None)
                for ch, details in channel_details.items()
            },
        }

    def record_interaction(
        self,
        unified_user_id: str,
        channel: str,
        message: str,
        response: str,
        topic: Optional[str] = None,
        intent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> str:
        """Record an interaction on any channel, storing it in Engram with full channel metadata."""
        channel = channel.lower()
        now = datetime.now(timezone.utc).isoformat()

        meta = {
            "timestamp": now,
            "channel": channel,
            "topic": topic,
            "intent": intent,
            **(metadata or {}),
        }

        mem_id = self.engram.store_learning(
            spec_id=unified_user_id,
            tag=f"interaction:{channel}",
            summary=message[:300],
            context=json.dumps({
                "action": "interaction",
                "channel": channel,
                "message": message[:500],
                "response": response[:500],
                "topic": topic,
                "intent": intent,
                "metadata": meta,
                "timestamp": now,
            }),
            importance="medium",
            layer="working",
        )

        session_key = f"{unified_user_id}:{channel}"
        session = self._active_sessions.get(session_key)
        if session:
            session.touch()
            session.context["last_topic"] = topic or session.context.get("last_topic")
            session.context["last_intent"] = intent or session.context.get("last_intent")
            session.context["interaction_count"] = session.context.get("interaction_count", 0) + 1

        return str(mem_id)

    def get_recent_history(
        self,
        unified_user_id: str,
        channels: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Retrieve recent interaction history for a user, optionally filtered by channels."""
        memories = self._memories_for_user(unified_user_id)
        filtered: list[dict] = []
        for mem in memories:
            tag = mem.get("tag", "")
            if tag.startswith("interaction:"):
                ch = tag.split(":", 1)[1] if ":" in tag else ""
                if channels is None or ch in channels:
                    filtered.append(mem)
                    if len(filtered) >= limit:
                        break
        return filtered

    def close_session(self, unified_user_id: str, channel: str) -> None:
        """Close a session on a given channel and persist state to Engram."""
        channel = channel.lower()
        session_key = f"{unified_user_id}:{channel}"
        session = self._active_sessions.pop(session_key, None)

        summary_parts = [f"Session closed on {channel}"]
        interaction_count = 0
        last_topic = None
        session_id = None
        if session:
            interaction_count = session.context.get("interaction_count", 0)
            summary_parts.append(f"({interaction_count} interactions)")
            last_topic = session.context.get("last_topic")
            if last_topic:
                summary_parts.append(f"last topic: {last_topic}")
            session_id = session.session_id

        self.engram.store_learning(
            spec_id=unified_user_id,
            tag=f"session:{channel}",
            summary=" — ".join(summary_parts),
            context=json.dumps({
                "action": "session_close",
                "channel": channel,
                "session": {
                    "session_id": session_id,
                    "interaction_count": interaction_count,
                    "last_topic": last_topic,
                },
            }),
            importance="low",
            layer="working",
        )

    def cleanup_stale_sessions(self, timeout_minutes: int = SESSION_TIMEOUT_MINUTES) -> int:
        """Remove and persist stale sessions that have exceeded the timeout."""
        stale_keys = [
            key for key, session in self._active_sessions.items()
            if session.is_stale(timeout_minutes)
        ]
        for key in stale_keys:
            unified_id, channel = key.rsplit(":", 1)
            self.close_session(unified_id, channel)
        if stale_keys:
            log.info("Cleaned up %d stale sessions (timeout=%dmin)", len(stale_keys), timeout_minutes)
        return len(stale_keys)

    def link_identities(
        self,
        primary_id: str,
        secondary_id: str,
        primary_channel: str,
        secondary_channel: str,
    ) -> bool:
        """Link two channel-specific identities as the same user.

        If both already have different unified IDs, merges secondary into primary.
        """
        primary_key = f"{primary_channel}:{primary_id}"
        secondary_key = f"{secondary_channel}:{secondary_id}"

        persisted = self._load_identity_map()
        primary_unified = persisted.get(primary_key)
        secondary_unified = persisted.get(secondary_key)

        if primary_unified and secondary_unified and primary_unified != secondary_unified:
            target_id = primary_unified
            old_id = secondary_unified

            old_memories = self._memories_for_user(old_id)
            for mem in old_memories:
                mem_id = mem.get("id")
                if mem_id:
                    try:
                        self.engram._conn.execute(
                            "UPDATE memories SET spec_id=? WHERE id=?", (target_id, mem_id)
                        )
                        self.engram._conn.commit()
                    except Exception:
                        pass

            self._save_identity_link(target_id, secondary_channel, secondary_id)
            self._identity_map[secondary_key] = target_id

            self.engram.store_learning(
                spec_id=target_id,
                tag="identity:merge",
                summary=f"Merged identity {old_id} into {target_id} ({primary_channel}/{primary_id} <-> {secondary_channel}/{secondary_id})",
                context=json.dumps({
                    "action": "merge_identities",
                    "target_id": target_id,
                    "merged_id": old_id,
                    "primary": {"channel": primary_channel, "id": primary_id},
                    "secondary": {"channel": secondary_channel, "id": secondary_id},
                }),
                importance="high",
                layer="customer",
            )
            log.info("Merged %s -> %s for link %s <-> %s", old_id, target_id, primary_key, secondary_key)
            return True

        target_id = primary_unified or secondary_unified or str(uuid.uuid4())

        if not primary_unified:
            self._save_identity_link(target_id, primary_channel, primary_id)
            self._identity_map[primary_key] = target_id
        if not secondary_unified:
            self._save_identity_link(target_id, secondary_channel, secondary_id)
            self._identity_map[secondary_key] = target_id

        self.engram.store_learning(
            spec_id=target_id,
            tag="identity:link",
            summary=f"Linked identities: {primary_channel}/{primary_id} <-> {secondary_channel}/{secondary_id}",
            context=json.dumps({
                "action": "link_identities",
                "primary": {"channel": primary_channel, "id": primary_id},
                "secondary": {"channel": secondary_channel, "id": secondary_id},
                "unified_user_id": target_id,
            }),
            importance="high",
            layer="customer",
        )
        log.info("Linked %s (%s) <-> %s (%s) -> %s", primary_channel, primary_id, secondary_channel, secondary_id, target_id)
        return True

    def get_active_sessions(self, unified_user_id: Optional[str] = None) -> list[dict]:
        """List active sessions, optionally filtered by user."""
        sessions_list: list[dict] = []
        for key, session in self._active_sessions.items():
            if unified_user_id and session.user_id != unified_user_id:
                continue
            sessions_list.append({
                "user_id": session.user_id,
                "channel": session.channel,
                "session_id": session.session_id,
                "started_at": session.started_at,
                "last_activity": session.last_activity,
                "is_stale": session.is_stale(),
                "interaction_count": session.context.get("interaction_count", 0),
            })
        return sessions_list

    def update_user_preferences(
        self,
        unified_user_id: str,
        preferences: dict[str, Any],
    ) -> None:
        """Store user preferences detected from any channel."""
        self.engram.store_learning(
            spec_id=unified_user_id,
            tag="user_preferences",
            summary=f"User preferences updated: {json.dumps(preferences)[:300]}",
            context=json.dumps({
                "action": "update_preferences",
                "preferences": preferences,
            }),
            importance="high",
            layer="customer",
        )
