"""Tests for Mysticverse (spec 010) — Digital twin, KYC, gamification."""

import pytest
from src.core.mysticverse import DigitalTwinPipeline, TelegramBotManager, KYCManager
from src.core.gamification import GamificationEngine, get_engine, LEVELS, BADGES, XP_RULES


class TestDigitalTwinPipeline:
    def test_create_twin(self):
        pipeline = DigitalTwinPipeline()
        twin = pipeline.create({
            "name": "Creadora Test",
            "photos": ["photo1.jpg", "photo2.jpg"],
            "voice_samples": ["voice1.mp3"],
            "personality": {"tono": "coqueto", "idioma": "es"},
        })
        assert twin["status"] == "processing"
        assert twin["creator_name"] == "Creadora Test"
        assert len(twin["photos"]) == 2

    def test_create_twin_generates_id(self):
        pipeline = DigitalTwinPipeline()
        twin = pipeline.create({"name": "Test"})
        assert len(twin["id"]) == 8

    def test_get_twin(self):
        pipeline = DigitalTwinPipeline()
        created = pipeline.create({"name": "Test"})
        fetched = pipeline.get(created["id"])
        assert fetched is not None
        assert fetched["id"] == created["id"]

    def test_get_nonexistent_twin(self):
        pipeline = DigitalTwinPipeline()
        assert pipeline.get("nonexistent") is None

    def test_update_step(self):
        pipeline = DigitalTwinPipeline()
        twin = pipeline.create({"name": "Test"})
        assert pipeline.update_step(twin["id"], "face_trained", True) is True
        updated = pipeline.get(twin["id"])
        assert updated["steps"]["face_trained"] is True

    def test_all_steps_complete_activates_twin(self):
        pipeline = DigitalTwinPipeline()
        twin = pipeline.create({"name": "Test"})
        for step in twin["steps"]:
            pipeline.update_step(twin["id"], step, True)
        assert pipeline.get(twin["id"])["status"] == "active"

    def test_list_by_creator(self):
        pipeline = DigitalTwinPipeline()
        pipeline.create({"name": "Ana"})
        pipeline.create({"name": "Ana"})
        pipeline.create({"name": "Betty"})
        anas = pipeline.list_by_creator("Ana")
        assert len(anas) == 2


class TestTelegramBotManager:
    def test_register_bot(self):
        manager = TelegramBotManager()
        bot = manager.register("twin_1", "123456:ABC-DEF", {
            "username": "CreadoraBot",
            "pricing": {"messages": "free", "photos": "$9.99"},
        })
        assert bot["status"] == "active"
        assert bot["twin_id"] == "twin_1"

    def test_get_bot(self):
        manager = TelegramBotManager()
        bot = manager.register("twin_1", "token", {})
        assert manager.get(bot["id"]) is not None


class TestKYCManager:
    def test_verify_age(self):
        kyc = KYCManager()
        result = kyc.verify_age("creator_1", {"type": "passport"})
        assert result["status"] == "age_verified"
        assert result["age_verified"] is True

    def test_full_kyc_flow(self):
        kyc = KYCManager()
        r = kyc.verify_age("creator_1", {"type": "id_card"})
        kyc.verify_identity(r["id"], {"selfie": "selfie.jpg"})
        kyc.sign_consent(r["id"], "digital_sig")
        assert kyc.is_verified("creator_1") is True

    def test_not_verified(self):
        kyc = KYCManager()
        assert kyc.is_verified("unknown") is False

    def test_get_record(self):
        kyc = KYCManager()
        r = kyc.verify_age("c1", {"type": "passport"})
        assert kyc.get(r["id"]) is not None


class TestGamificationEngine:
    def test_initial_state(self):
        engine = GamificationEngine()
        player = engine.get_or_create_player("p1", "TestPlayer")
        assert player["level"] == 1
        assert player["xp"] == 0

    def test_add_xp(self):
        engine = GamificationEngine()
        result = engine.add_xp("p1", 100, "test")
        assert result["xp_added"] == 100
        assert result["total_xp"] == 100

    def test_level_up_at_100_xp(self):
        engine = GamificationEngine()
        engine.add_xp("p1", 100)
        player = engine.get_player("p1")
        assert player["level"] >= 2

    def test_level_up_at_700_xp(self):
        engine = GamificationEngine()
        engine.add_xp("p1", 700)
        player = engine.get_player("p1")
        assert player["level"] >= 4

    def test_level_8_at_12000_xp(self):
        engine = GamificationEngine()
        engine.add_xp("p1", 12000)
        player = engine.get_player("p1")
        assert player["level"] == 8

    def test_award_badge(self):
        engine = GamificationEngine()
        result = engine.award_badge("p1", "primer_mensaje")
        assert "badge" in result
        assert result["badge"]["name"] == "Primer Paso"

    def test_no_duplicate_badges(self):
        engine = GamificationEngine()
        engine.award_badge("p1", "primer_mensaje")
        result = engine.award_badge("p1", "primer_mensaje")
        assert "error" in result

    def test_daily_login(self):
        engine = GamificationEngine()
        result = engine.daily_login("p1")
        assert result["streak"] == 1
        assert result["xp_added"] >= 50

    def test_daily_login_streak(self):
        engine = GamificationEngine()
        import time
        p = engine.get_or_create_player("p1")
        p["last_login"] = time.time() - 100000
        r1 = engine.daily_login("p1")
        assert r1["streak"] == 1
        p["last_login"] = time.time() - 100000
        r2 = engine.daily_login("p1")
        assert r2["streak"] == 2

    def test_streak_badge_at_7(self):
        engine = GamificationEngine()
        p = engine.get_or_create_player("p1")
        import time
        for i in range(7):
            p["last_login"] = time.time() - 100000
            engine.daily_login("p1")
        player = engine.get_player("p1")
        assert "streak_7" in player["badges"]

    def test_leaderboard_order(self):
        engine = GamificationEngine()
        engine.add_xp("p1", 100)
        engine.add_xp("p2", 500)
        engine.add_xp("p3", 50)
        lb = engine.get_leaderboard()
        assert lb[0]["id"] == "p2"
        assert lb[1]["id"] == "p1"
        assert lb[2]["id"] == "p3"

    def test_track_action_adds_xp(self):
        engine = GamificationEngine()
        result = engine.track_action("p1", "chat_message")
        assert result["xp_added"] == XP_RULES["chat_message"]

    def test_track_action_awards_badge(self):
        engine = GamificationEngine()
        result = engine.track_action("p1", "first_message")
        assert "badge" in result

    def test_get_all_badges(self):
        engine = GamificationEngine()
        badges = engine.get_all_badges("p1")
        assert len(badges) == len(BADGES)
        for b in badges:
            assert "id" in b
            assert "awarded" in b

    def test_level_info(self):
        engine = GamificationEngine()
        info = engine.get_level_info(1)
        assert info["name"] == "Novato"
        info = engine.get_level_info(8)
        assert info["name"] == "Leyenda"
        info = engine.get_level_info(99)
        assert info is None

    def test_singleton(self):
        e1 = get_engine()
        e2 = get_engine()
        assert e1 is e2
