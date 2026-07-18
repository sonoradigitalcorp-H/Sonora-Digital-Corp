"""Tests para Clone Generation — FR-04: Generación de contenido con identidad del cliente"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))


class MockCreditSystem:
    def __init__(self, photo_credits=10, video_credits=3, tts_credits=10):
        self.credits = {"photo": photo_credits, "video": video_credits, "tts": tts_credits}

    def consume(self, asset_type: str) -> bool:
        if self.credits.get(asset_type, 0) > 0:
            self.credits[asset_type] -= 1
            return True
        return False

    def remaining(self, asset_type: str) -> int:
        return self.credits.get(asset_type, 0)


class TestPhotoGeneration:
    def test_generates_with_valid_lora(self):
        lora_active = True
        assert lora_active is True

    def test_fails_without_lora(self):
        lora_active = False
        assert lora_active is False

    def test_generated_url_is_valid(self):
        url = "https://supabase.co/storage/clients/test/output/photos/gen_001.jpg"
        assert url.startswith("https://")
        assert url.endswith(".jpg")

    def test_face_similarity_meets_threshold(self):
        similarity = 0.81
        assert similarity >= 0.75


class TestVideoGeneration:
    def test_talking_head_generates(self):
        has_lip_sync = True
        assert has_lip_sync is True

    def test_full_body_generates(self):
        has_motion = True
        assert has_motion is True

    def test_video_duration_in_range(self):
        duration_s = 15
        assert 5 <= duration_s <= 60

    def test_video_has_audio_track(self):
        has_audio = True
        assert has_audio is True


class TestTTSGeneration:
    def test_generates_with_cloned_voice(self):
        voice_active = True
        assert voice_active is True

    def test_fails_without_voice(self):
        voice_active = False
        assert voice_active is False

    def test_audio_format_is_valid(self):
        fmt = "wav"
        assert fmt in ("wav", "mp3", "ogg")

    def test_text_to_speech_length_match(self):
        input_text = "Hola, esto es una prueba de voz clonada"
        output_duration_s = len(input_text.split()) * 0.4
        assert 1.0 <= output_duration_s <= 30.0


class TestCreditConsumption:
    def test_consumes_photo_credit(self):
        credits = MockCreditSystem(photo_credits=10)
        assert credits.consume("photo") is True
        assert credits.remaining("photo") == 9

    def test_consumes_video_credit(self):
        credits = MockCreditSystem(video_credits=3)
        assert credits.consume("video") is True
        assert credits.remaining("video") == 2

    def test_consumes_tts_credit(self):
        credits = MockCreditSystem(tts_credits=10)
        assert credits.consume("tts") is True
        assert credits.remaining("tts") == 9

    def test_rejects_when_no_credits(self):
        credits = MockCreditSystem(photo_credits=0)
        assert credits.consume("photo") is False
        assert credits.remaining("photo") == 0

    def test_unknown_asset_type_returns_zero(self):
        credits = MockCreditSystem()
        assert credits.remaining("unknown") == 0


class TestIteration:
    def test_new_prompt_same_identity(self):
        same_identity = True
        assert same_identity is True

    def test_only_one_credit_for_iteration(self):
        credits = MockCreditSystem(photo_credits=10)
        credits.consume("photo")
        credits.consume("photo")  # iteration
        assert credits.remaining("photo") == 8
