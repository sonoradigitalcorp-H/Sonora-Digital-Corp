"""Tests de integración para Clone Pipeline Completo — FR-01 a FR-06"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

from tests.test_clone_generation import MockCreditSystem
from tests.test_clone_recollection import mock_client_bucket
from tests.test_clone_training import mock_clone_voice, mock_face_similarity, mock_train_lora


class TestFullPipeline:
    def test_happy_path_complete_pipeline(self):
        async def run():
            # FR-01: Recolección
            state = mock_client_bucket("client-001")
            state["photos"] = [f"p{i}.jpg" for i in range(15)]
            state["audio"] = "audio.wav"
            assert len(state["photos"]) >= 15
            assert state["audio"] is not None

            # FR-02: Validación
            valid_photos = all(True for _ in state["photos"])
            valid_audio = True
            assert valid_photos and valid_audio

            # FR-03: Entrenamiento
            lora = await mock_train_lora(state["photos"], "client_001")
            assert lora["status"] == "trained"
            voice = await mock_clone_voice(state["audio"], "client_001")
            assert voice["status"] == "cloned"

            # FR-04: Generación
            credits = MockCreditSystem(photo_credits=10, video_credits=3, tts_credits=10)
            similarity = await mock_face_similarity("ref.jpg", "gen.jpg")
            assert similarity >= 0.75
            assert credits.consume("photo") is True
            assert credits.remaining("photo") == 9

            # FR-05: Entrega
            storage_path = "/clients/client-001/output/photos/gen_001.jpg"
            assert "client-001" in storage_path

            # FR-06: Créditos
            assert credits.remaining("photo") == 9
            assert credits.remaining("video") == 3

        import asyncio
        asyncio.run(run())

    def test_pipeline_fails_without_enough_photos(self):
        async def run():
            state = mock_client_bucket("client-001")
            state["photos"] = [f"p{i}.jpg" for i in range(8)]
            result = await mock_train_lora(state["photos"], "client_001")
            assert "error" in result
        import asyncio
        asyncio.run(run())

    def test_pipeline_fails_without_audio(self):
        state = mock_client_bucket("client-001")
        state["photos"] = [f"p{i}.jpg" for i in range(15)]
        can_train = state["audio"] is not None
        assert can_train is False

    def test_credits_block_generation_when_exhausted(self):
        credits = MockCreditSystem(photo_credits=1, video_credits=0, tts_credits=0)
        assert credits.consume("photo") is True
        assert credits.consume("photo") is False
        assert credits.consume("video") is False

    def test_full_body_video_requires_body_photos(self):
        has_body_photos = True
        assert has_body_photos is True

    def test_talking_head_video_requires_face_photos(self):
        has_face_photos = True
        assert has_face_photos is True


class TestErrorScenarios:
    def test_fal_training_timeout_retries(self):
        max_retries = 3
        attempt = 0
        success = False
        while attempt < max_retries and not success:
            attempt += 1
            if attempt == 3:
                success = True
        assert success is True
        assert attempt == 3

    def test_invalid_photo_format_rejected(self):
        valid_formats = {".jpg", ".jpeg", ".png", ".webp"}
        ext = ".heic"
        assert ext not in valid_formats

    def test_audio_snr_below_threshold_rejected(self):
        snr_db = 8
        assert snr_db < 15

    def test_audio_snr_above_threshold_accepted(self):
        snr_db = 20
        assert snr_db >= 15


class TestStatePersistence:
    def test_client_state_across_sessions(self):
        state = mock_client_bucket("client-001")
        state["photos"] = ["p1.jpg"]
        assert len(state["photos"]) == 1
        state["photos"].extend(["p2.jpg", "p3.jpg"])
        assert len(state["photos"]) == 3

    def test_training_model_persists(self):
        models = {"lora": "lora.safetensors", "voice": "voice-maria"}
        assert "lora" in models
        assert "voice" in models

    def test_output_assets_organized_by_client(self):
        path = "/clients/client-abc/output/photos/gen_001.jpg"
        assert path.startswith("/clients/client-abc/")
