"""Gamification Engine [FR1, FR2, FR3, FR9] — quests, niveles, rewards, leaderboard."""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any

log = logging.getLogger("sonora.engine.gamification")

# ─── Quest Configurations ───

QUEST_CONFIGS: dict[str, dict] = {
    "quest-trivia-001": {
        "title": "Trivia del día",
        "category": "play",
        "frequency": "daily",
        "beat_reward": 3,
        "xp_reward": 10,
        "requirements": {"answers_correct_min": 3, "total_questions": 5},
    },
    "quest-daily-001": {
        "title": "Trivia diaria",
        "category": "play",
        "frequency": "daily",
        "beat_reward": 3,
        "xp_reward": 10,
        "requirements": {"answers_correct_min": 3, "total_questions": 5},
    },
    "quest-referral-001": {
        "title": "Invita amigos",
        "category": "work",
        "frequency": "weekly",
        "beat_reward": 15,
        "xp_reward": 50,
        "requirements": {"referrals_count": 3},
    },
    "quest-learn-video-001": {
        "title": "Detrás de cámaras",
        "category": "learn",
        "frequency": "weekly",
        "beat_reward": 10,
        "xp_reward": 30,
        "requirements": {"progress_pct": 100},
    },
    "quest-share-001": {
        "title": "Comparte en redes",
        "category": "work",
        "frequency": "daily",
        "beat_reward": 5,
        "xp_reward": 15,
        "requirements": {"platforms": 2},
    },
    "quest-quiz-001": {
        "title": "Quiz semanal",
        "category": "play",
        "frequency": "weekly",
        "beat_reward": 8,
        "xp_reward": 25,
        "requirements": {"score_min": 70},
    },
}

# ─── Level Configuration ───

LEVEL_THRESHOLDS = [
    {"level": "bronze", "tier": 1, "xp_required": 0, "benefits": ["daily_quests", "basic_badge"]},
    {"level": "silver", "tier": 2, "xp_required": 100, "benefits": ["daily_quests", "silver_badge", "exclusive_content"]},
    {"level": "gold", "tier": 3, "xp_required": 300, "benefits": ["daily_quests", "gold_badge", "priority_support", "early_access"]},
    {"level": "platinum", "tier": 4, "xp_required": 1000, "benefits": ["all_gold", "platinum_badge", "meet_greet", "custom_content", "revenue_share"]},
]

# In-memory stores (in production: Hasura/PostgreSQL)
_completions: dict[str, set[str]] = {}  # tenant:user:quest_id -> set of dates
_pool_balances: dict[str, int] = {}
_leaderboard_data: dict[str, list[dict]] = {}


class QuestEngine:
    """FR1: Validates and completes quests, calculates rewards."""

    def get_quest_config(self, quest_id: str) -> dict | None:
        return QUEST_CONFIGS.get(quest_id)

    def complete_quest(
        self, tenant_id: str, user_id: str, quest_id: str,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        quest = self.get_quest_config(quest_id)
        if not quest:
            return {"status": "error", "message": "Quest not found"}

        completion_key = f"{tenant_id}:{user_id}:{quest_id}"
        today = datetime.now().strftime("%Y-%m-%d")

        if completion_key not in _completions:
            _completions[completion_key] = set()

        # Check for duplicate (frequency-based)
        if quest["frequency"] == "daily" and today in _completions[completion_key]:
            return {"status": "already_completed", "beat_reward": 0, "xp_reward": 0}

        if quest["frequency"] == "weekly":
            week = datetime.now().strftime("%Y-W%W")
            if week in _completions[completion_key]:
                return {"status": "already_completed", "beat_reward": 0, "xp_reward": 0}

        # Check pool balance
        pool = self.get_pool_balance(tenant_id)
        if pool < quest["beat_reward"]:
            return {"status": "pool_exhausted", "beat_reward": 0, "xp_reward": 0}

        # Deduct from pool
        self.set_pool_balance(tenant_id, pool - quest["beat_reward"])

        # Record completion
        freq_key = today if quest["frequency"] == "daily" else datetime.now().strftime("%Y-W%W")
        _completions[completion_key].add(freq_key)

        return {
            "status": "completed",
            "beat_reward": quest["beat_reward"],
            "xp_reward": quest["xp_reward"],
            "category": quest["category"],
        }

    def get_pool_balance(self, tenant_id: str) -> int:
        return _pool_balances.get(tenant_id, 1000000)

    def set_pool_balance(self, tenant_id: str, balance: int):
        _pool_balances[tenant_id] = balance

    def check_pool_level(self, tenant_id: str):
        pool = self.get_pool_balance(tenant_id)
        if pool < 100:
            log.warning(f"Pool low for {tenant_id}: {pool} $BEAT remaining")


class LevelSystem:
    """FR2: XP-based level progression with benefits."""

    def get_level(self, xp: int) -> dict:
        current = LEVEL_THRESHOLDS[0]
        for level in reversed(LEVEL_THRESHOLDS):
            if xp >= level["xp_required"]:
                current = level
                break
        return {
            "level": current["level"],
            "tier": current["tier"],
            "xp_required": current["xp_required"],
        }

    def add_xp(self, current_xp: int, xp_gained: int) -> dict[str, Any]:
        old_level = self.get_level(current_xp)
        new_xp = current_xp + xp_gained
        new_level = self.get_level(new_xp)
        return {
            "total_xp": new_xp,
            "xp_gained": xp_gained,
            "old_level": old_level["level"],
            "new_level": new_level["level"],
            "leveled_up": old_level["tier"] != new_level["tier"],
        }

    def get_level_benefits(self, level_name: str) -> list[str]:
        for level in LEVEL_THRESHOLDS:
            if level["level"] == level_name:
                return level["benefits"]
        return []


class Leaderboard:
    """FR9: Per-tenant leaderboard by XP and $BEAT."""

    def record_completion(self, tenant_id: str, user_id: str, xp: int, beat: int):
        if tenant_id not in _leaderboard_data:
            _leaderboard_data[tenant_id] = {}

        if user_id not in _leaderboard_data[tenant_id]:
            _leaderboard_data[tenant_id][user_id] = {"xp": 0, "beat": 0}

        _leaderboard_data[tenant_id][user_id]["xp"] += xp
        _leaderboard_data[tenant_id][user_id]["beat"] += beat

    def get_top(self, tenant_id: str, metric: str = "xp", limit: int = 5) -> list[dict]:
        entries = _leaderboard_data.get(tenant_id, {})
        sorted_users = sorted(
            entries.items(),
            key=lambda x: x[1].get(metric, 0),
            reverse=True,
        )[:limit]

        return [
            {
                "rank": i + 1,
                "user_id": uid,
                metric: data.get(metric, 0),
                "xp": data.get("xp", 0),
                "beat": data.get("beat", 0),
            }
            for i, (uid, data) in enumerate(sorted_users)
        ]
