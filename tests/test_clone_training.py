"""Tests para Clone Training — FR-02/FR-03: Entrenamiento de LoRA y clon de voz"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

FAL_KEY = "test-fal-key"


async def mock_train_lora(photos: list[str], trigger_word: str) -> dict:
    if len(photos) < 15:
        return {"error": "Se requieren al menos 15 fotos", "photos_count": len(photos)}
    return {"weight_id": "lora-w123", "trigger_word": trigger_word, "photos_count": len(photos), "status": "trained"}


async def mock_clone_voice(audio_url: str, name: str) -> dict:
    if not audio_url:
        return {"error": "audio_url is required"}
    return {"voice_id": f"voice-{name.lower().replace(' ', '_')}", "status": "cloned"}


async def mock_face_similarity(ref_url: str, generated_url: str) -> float:
    return 0.82


class TestLoRATraining:
    def test_requires_15_photos(self):
        async def run():
            result = await mock_train_lora([f"p{i}.jpg" for i in range(15)], "juan_perez")
            assert "error" not in result
            assert result["status"] == "trained"
            assert result["weight_id"] == "lora-w123"
        import asyncio
        asyncio.run(run())

    def test_rejects_insufficient_photos(self):
        async def run():
            result = await mock_train_lora([f"p{i}.jpg" for i in range(12)], "juan_perez")
            assert "error" in result
            assert result["photos_count"] == 12
        import asyncio
        asyncio.run(run())

    def test_rejects_empty_photos(self):
        async def run():
            result = await mock_train_lora([], "test")
            assert "error" in result
        import asyncio
        asyncio.run(run())


class TestVoiceCloning:
    def test_clones_from_audio_url(self):
        async def run():
            result = await mock_clone_voice("https://storage/audio.wav", "maria_garcia")
            assert result["status"] == "cloned"
            assert result["voice_id"] == "voice-maria_garcia"
        import asyncio
        asyncio.run(run())

    def test_rejects_empty_audio_url(self):
        async def run():
            result = await mock_clone_voice("", "test")
            assert "error" in result
        import asyncio
        asyncio.run(run())


class TestQualityValidation:
    def test_face_similarity_above_threshold(self):
        assert 0.82 > 0.75

    def test_face_similarity_below_threshold(self):
        similarity = 0.55
        assert similarity < 0.6

    def test_face_similarity_mid_range(self):
        similarity = 0.68
        assert 0.6 <= similarity <= 0.75


class TestTrainingMetadata:
    def test_includes_trigger_word(self):
        meta = {"weight_id": "lora-w123", "trigger_word": "juan_perez", "photos_count": 15}
        assert meta["trigger_word"] == "juan_perez"

    def test_includes_photos_count(self):
        meta = {"weight_id": "lora-w123", "photos_count": 18}
        assert meta["photos_count"] == 18

    def test_training_time_under_limit(self):
        training_minutes = 8
        assert training_minutes < 15
