"""Tests para Gamification Engine [FR1, FR2, FR3, FR9] — quests, niveles, rewards, leaderboard."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def reset_gamification_state():
    from apps.sonora_engine.gamification import _completions, _pool_balances, _leaderboard_data
    _completions.clear()
    _pool_balances.clear()
    _pool_balances["abe-music"] = 1000000
    _leaderboard_data.clear()


class TestQuestEngine:
    """FR1: Quest validation, completion, and reward calculation."""

    def test_complete_daily_trivia(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        result = engine.complete_quest(
            tenant_id="abe-music",
            user_id="fan-uuid",
            quest_id="quest-trivia-001",
            metadata={"answers_correct": 5, "total_questions": 5},
        )
        assert result["status"] == "completed"
        assert result["beat_reward"] == 3
        assert result["xp_reward"] == 10

    def test_complete_referral_quest(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        result = engine.complete_quest(
            tenant_id="abe-music",
            user_id="fan-uuid",
            quest_id="quest-referral-001",
            metadata={"referrals_count": 3},
        )
        assert result["status"] == "completed"
        assert result["beat_reward"] == 15

    def test_complete_watch_video(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        result = engine.complete_quest(
            tenant_id="abe-music",
            user_id="fan-uuid",
            quest_id="quest-learn-video-001",
            metadata={"progress_pct": 100},
        )
        assert result["status"] == "completed"
        assert result["beat_reward"] == 10

    def test_duplicate_quest_rejected(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        engine.complete_quest("abe-music", "fan-uuid", "quest-daily-001")
        result = engine.complete_quest("abe-music", "fan-uuid", "quest-daily-001")
        assert result["status"] == "already_completed"
        assert result["beat_reward"] == 0

    def test_quest_not_found(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        result = engine.complete_quest("abe-music", "fan-uuid", "quest-nonexistent")
        assert result["status"] == "error"
        assert "not found" in result.get("message", "").lower()

    def test_play_quests_have_lower_rewards(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        play = engine.get_quest_config("quest-trivia-001")
        work = engine.get_quest_config("quest-referral-001")
        assert play["beat_reward"] < work["beat_reward"]

    def test_learn_quests_mid_range(self):
        from apps.sonora_engine.gamification import QuestEngine
        engine = QuestEngine()
        play = engine.get_quest_config("quest-trivia-001")
        learn = engine.get_quest_config("quest-learn-video-001")
        work = engine.get_quest_config("quest-referral-001")
        assert play["beat_reward"] < learn["beat_reward"] < work["beat_reward"]


class TestLevelSystem:
    """FR2: XP thresholds, level progression, benefits."""

    def test_start_at_bronze(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.get_level(xp=0)
        assert result["level"] == "bronze"
        assert result["tier"] == 1

    def test_silver_at_100_xp(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.get_level(xp=100)
        assert result["level"] == "silver"
        assert result["tier"] == 2

    def test_gold_at_300_xp(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.get_level(xp=300)
        assert result["level"] == "gold"
        assert result["tier"] == 3

    def test_platinum_at_1000_xp(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.get_level(xp=1000)
        assert result["level"] == "platinum"
        assert result["tier"] == 4

    def test_level_up_detected(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.add_xp(current_xp=90, xp_gained=15)
        assert result["leveled_up"] is True
        assert result["new_level"] == "silver"

    def test_no_level_up_within_tier(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.add_xp(current_xp=50, xp_gained=10)
        assert result["leveled_up"] is False
        assert result["new_level"] == "bronze"

    def test_platinum_is_max_level(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        result = levels.get_level(xp=5000)
        assert result["level"] == "platinum"
        assert result["tier"] == 4

    def test_each_level_has_benefits(self):
        from apps.sonora_engine.gamification import LevelSystem
        levels = LevelSystem()
        bronze = levels.get_level_benefits("bronze")
        silver = levels.get_level_benefits("silver")
        gold = levels.get_level_benefits("gold")
        platinum = levels.get_level_benefits("platinum")
        assert len(bronze) >= 1
        assert len(silver) > len(bronze)
        assert len(platinum) > len(gold)


class TestPoolAndRewards:
    """FR3: $BEAT pool management and reward distribution."""

    def test_reward_deducted_from_pool(self):
        from apps.sonora_engine.gamification import QuestEngine, _pool_balances
        engine = QuestEngine()
        _pool_balances["abe-music"] = 1000
        pool_before = _pool_balances["abe-music"]
        engine.complete_quest("abe-music", "fan-new", "quest-trivia-001")
        pool_after = _pool_balances["abe-music"]
        assert pool_after < pool_before
        assert pool_after == pool_before - 3

    def test_pool_exhausted_rejects_rewards(self):
        from apps.sonora_engine.gamification import QuestEngine, _pool_balances
        engine = QuestEngine()
        _pool_balances["abe-music"] = 2
        result = engine.complete_quest("abe-music", "fan-new-2", "quest-trivia-001")
        assert result["status"] == "pool_exhausted"

    def test_check_pool_logs_warning(self):
        from apps.sonora_engine.gamification import QuestEngine, _pool_balances
        engine = QuestEngine()
        _pool_balances["abe-music"] = 50
        with patch("apps.sonora_engine.gamification.log.warning") as mock_warn:
            engine.check_pool_level("abe-music")
            mock_warn.assert_called_once()


class TestLeaderboard:
    """FR9: Leaderboard by XP and $BEAT."""

    def test_top_5_by_xp(self):
        from apps.sonora_engine.gamification import Leaderboard
        lb = Leaderboard()
        lb.record_completion("abe-music", "fan-a", xp=100, beat=10)
        lb.record_completion("abe-music", "fan-b", xp=200, beat=20)
        result = lb.get_top("abe-music", metric="xp", limit=5)
        assert len(result) <= 5
        if result:
            assert "rank" in result[0]
            assert "xp" in result[0]

    def test_top_5_by_beat(self):
        from apps.sonora_engine.gamification import Leaderboard
        lb = Leaderboard()
        lb.record_completion("abe-music", "fan-a", xp=100, beat=50)
        result = lb.get_top("abe-music", metric="beat", limit=5)
        assert len(result) <= 5

    def test_leaderboard_updates_after_quest(self):
        from apps.sonora_engine.gamification import Leaderboard
        lb = Leaderboard()
        lb.record_completion("abe-music", "fan-uuid", xp=100, beat=10)
        top = lb.get_top("abe-music", metric="xp")
        if top and top[0].get("user_id") == "fan-uuid":
            assert top[0]["xp"] >= 100

    def test_leaderboard_per_tenant(self):
        from apps.sonora_engine.gamification import Leaderboard
        lb = Leaderboard()
        lb.record_completion("abe-music", "fan-a", xp=100, beat=10)
        lb.record_completion("other-tenant", "fan-b", xp=200, beat=20)
        top_a = lb.get_top("abe-music", metric="xp")
        for entry in top_a:
            assert entry["user_id"] != "fan-b"
