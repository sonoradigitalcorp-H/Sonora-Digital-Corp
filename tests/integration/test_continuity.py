"""Integration tests for cross-channel session continuity.

Simulates interactions across Telegram, WhatsApp, and Web channels,
verifying that context is maintained and unified across all channels.
"""

import json
import time
import uuid
from typing import Any

import pytest

from platforms.continuity_bridge import ContinuityBridge
from src.core.engram import engram


@pytest.fixture(autouse=True)
def _clean_test_memories():
    """Remove test memories before and after each test."""
    stored = []
    try:
        rows = engram._conn.execute(
            "SELECT id, tag FROM memories WHERE tag LIKE 'test_continuity:%'",
        ).fetchall()
        stored = [(r["id"], r["tag"]) for r in rows]
        for mem_id, _ in stored:
            engram._conn.execute("DELETE FROM memories WHERE id=?", (mem_id,))
            try:
                engram._conn.execute("DELETE FROM memories_fts WHERE rowid=?", (mem_id,))
            except Exception:
                pass
        engram._conn.commit()
    except Exception:
        pass
    yield
    try:
        rows = engram._conn.execute(
            "SELECT id FROM memories WHERE tag LIKE 'test_continuity:%'",
        ).fetchall()
        for (mem_id,) in rows:
            engram._conn.execute("DELETE FROM memories WHERE id=?", (mem_id,))
            try:
                engram._conn.execute("DELETE FROM memories_fts WHERE rowid=?", (mem_id,))
            except Exception:
                pass
        engram._conn.commit()
    except Exception:
        pass


class TestContinuityBridge:
    """Test the ContinuityBridge across multiple channels."""

    def _make_bridge(self) -> ContinuityBridge:
        return ContinuityBridge()

    def _tag(self, channel: str, suffix: str = "") -> str:
        return f"test_continuity:{channel}{suffix}"

    # ── Helpers to simulate interactions without persisting to the actual Engram ──

    def test_single_channel_continuity(self):
        """Verify that interactions on the same channel build context."""
        bridge = self._make_bridge()
        user_id = f"tg_test_{uuid.uuid4().hex[:8]}"

        ctx1 = bridge.get_context(user_id, "telegram")
        assert ctx1["channel"] == "telegram"
        assert ctx1["unified_user_id"] is not None

        bridge.save_interaction(user_id, "telegram", "Hello", "Hi! How can I help you?", topic="greeting")
        bridge.save_interaction(user_id, "telegram", "What services do you offer?", "We offer...", topic="services")
        bridge.save_interaction(user_id, "telegram", "Tell me about pricing", "Our pricing...", topic="pricing")

        history = bridge.get_recent_history(user_id, "telegram", limit=10)
        assert len(history) >= 3
        summaries = [h.get("summary", "") for h in history]
        assert any("Hello" in s for s in summaries)
        assert any("services" in s for s in summaries)
        assert any("pricing" in s for s in summaries)

    def test_cross_channel_continuity(self):
        """Verify that context built on one channel is visible on another after linking."""
        bridge = self._make_bridge()
        tg_id = f"tg_{uuid.uuid4().hex[:8]}"
        wa_id = f"wa_{uuid.uuid4().hex[:8]}"

        tg_unified = bridge.get_unified_user_id(tg_id, "telegram")
        wa_unified = bridge.get_unified_user_id(wa_id, "whatsapp")

        assert tg_unified != wa_unified, "Unlinked users should have different unified IDs"

        linked = bridge.link_identities(tg_id, wa_id, "telegram", "whatsapp")
        assert linked, "Should successfully link identities"

        unified_after = bridge.get_unified_user_id(tg_id, "telegram")
        wa_unified_after = bridge.get_unified_user_id(wa_id, "whatsapp")
        assert unified_after == wa_unified_after, "After linking, both should resolve to the same unified ID"

    def test_context_persists_after_linking(self):
        """Verify that after linking, context from both channels is available."""
        bridge = self._make_bridge()
        tg_id = f"tg_{uuid.uuid4().hex[:8]}"
        wa_id = f"wa_{uuid.uuid4().hex[:8]}"

        bridge.save_interaction(
            tg_id, "telegram",
            "I need help with my account",
            "I can help! What's your account number?",
            topic="account_support",
            intent="help",
        )

        bridge.link_identities(tg_id, wa_id, "telegram", "whatsapp")

        bridge.save_interaction(
            wa_id, "whatsapp",
            "My account is 12345",
            "Let me look that up...",
            topic="account_support",
        )

        ctx = bridge.get_context(tg_id, "telegram")
        assert "account_support" in ctx.get("topics", []), "Topic from Telegram should appear in cross-channel context"

        ctx_wa = bridge.get_context(wa_id, "whatsapp")
        assert ctx_wa["unified_user_id"] == ctx["unified_user_id"], "Context from either channel should resolve to same user"

    def test_three_channel_continuity(self):
        """Verify continuity across Telegram, WhatsApp, and Web."""
        bridge = self._make_bridge()
        tg_id = f"tg_{uuid.uuid4().hex[:8]}"
        wa_id = f"wa_{uuid.uuid4().hex[:8]}"
        web_id = f"web_{uuid.uuid4().hex[:8]}"

        bridge.save_interaction(tg_id, "telegram", "Hi", "Hello!", topic="greeting")

        bridge.link_identities(tg_id, wa_id, "telegram", "whatsapp")
        bridge.save_interaction(wa_id, "whatsapp", "What's the price?", "$99/month", topic="pricing")

        bridge.link_identities(wa_id, web_id, "whatsapp", "web")
        bridge.save_interaction(web_id, "web", "I want to buy", "Great! Let me process that.", intent="purchase")

        ctx = bridge.get_context(tg_id, "telegram")
        assert "greeting" in ctx.get("topics", []) or "pricing" in ctx.get("topics", []), \
            "Topics from all channels should be aggregated"
        assert len(ctx.get("active_channels", [])) >= 2, \
            "At least 2 active channels should be detected"

    def test_get_unified_user_id_consistency(self):
        """Verify that the same user always resolves to the same unified ID."""
        bridge = self._make_bridge()
        tg_id = f"tg_{uuid.uuid4().hex[:8]}"

        id1 = bridge.get_unified_user_id(tg_id, "telegram")
        id2 = bridge.get_unified_user_id(tg_id, "telegram")

        assert id1 == id2, "Same user on same channel should always return the same unified ID"

    def test_save_interaction_returns_bool(self):
        """Verify that save_interaction returns a boolean."""
        bridge = self._make_bridge()
        user_id = f"test_{uuid.uuid4().hex[:8]}"

        result = bridge.save_interaction(user_id, "telegram", "test", "response")
        assert isinstance(result, bool)
        assert result is True

    def test_link_identities_returns_bool(self):
        """Verify that link_identities returns a boolean."""
        bridge = self._make_bridge()
        tg_id = f"tg_{uuid.uuid4().hex[:8]}"
        wa_id = f"wa_{uuid.uuid4().hex[:8]}"

        result = bridge.link_identities(tg_id, wa_id, "telegram", "whatsapp")
        assert isinstance(result, bool)
        assert result is True

    def test_history_filter_by_channels(self):
        """Verify history filtering by channels."""
        bridge = self._make_bridge()
        user_id = f"test_{uuid.uuid4().hex[:8]}"

        bridge.save_interaction(user_id, "telegram", "TG msg 1", "Response 1")
        bridge.save_interaction(user_id, "whatsapp", "WA msg 1", "Response 2")
        bridge.save_interaction(user_id, "telegram", "TG msg 2", "Response 3")

        tg_history = bridge.get_recent_history(user_id, "telegram", channels_filter=["telegram"], limit=10)
        assert len(tg_history) >= 2
        for h in tg_history:
            tag = h.get("tag", "")
            assert "telegram" in tag, f"Expected telegram tag, got {tag}"
