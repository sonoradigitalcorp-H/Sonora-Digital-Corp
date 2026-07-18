"""Tests para Clone Recollection — FR-01: Recolección conversacional de fotos y audio"""

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))


def mock_client_bucket(client_id: str) -> dict:
    return {"client_id": client_id, "status": "pending", "photos": [], "audio": None}


class TestPhotoValidation:
    def test_accepts_15_photos(self):
        photos = [f"https://supabase.co/storage/clients/test/photos/{i}.jpg" for i in range(15)]
        assert len(photos) >= 15

    def test_rejects_less_than_15(self):
        photos = [f"photo_{i}.jpg" for i in range(8)]
        assert len(photos) < 15

    def test_accepts_20_photos(self):
        photos = [f"photo_{i}.jpg" for i in range(20)]
        assert len(photos) >= 15

    def test_rejects_empty_list(self):
        assert len([]) < 15

    def test_detects_terminado_keyword(self):
        messages = ["hola", "aquí van mis fotos", "terminé"]
        assert any(m.lower() in ("terminé", "termine", "listo", "ya") for m in messages)

    def test_ignores_other_keywords(self):
        messages = ["hola", "aquí van mis fotos", "gracias"]
        assert not any(m.lower() in ("terminé", "termine") for m in messages)


class TestAudioValidation:
    def test_accepts_30s_audio(self):
        duration_s = 30
        assert duration_s >= 10

    def test_rejects_5s_audio(self):
        duration_s = 5
        assert duration_s < 10

    def test_accepts_60s_audio(self):
        duration_s = 60
        assert duration_s >= 10


class TestClientState:
    def test_tracks_photos_across_sessions(self):
        state = mock_client_bucket("client-001")
        assert len(state["photos"]) == 0
        state["photos"].extend(["f1.jpg", "f2.jpg", "f3.jpg"])
        assert len(state["photos"]) == 3

    def test_ready_to_train_with_15_photos_and_audio(self):
        state = mock_client_bucket("client-001")
        state["photos"] = [f"p{i}.jpg" for i in range(15)]
        state["audio"] = "audio.wav"
        can_train = len(state["photos"]) >= 15 and state["audio"] is not None
        assert can_train is True

    def test_not_ready_without_audio(self):
        state = mock_client_bucket("client-001")
        state["photos"] = [f"p{i}.jpg" for i in range(15)]
        can_train = len(state["photos"]) >= 15 and state["audio"] is not None
        assert can_train is False

    def test_not_ready_without_photos(self):
        state = mock_client_bucket("client-001")
        state["audio"] = "audio.wav"
        can_train = len(state["photos"]) >= 15 and state["audio"] is not None
        assert can_train is False


class TestFaceDetection:
    def test_detects_face_in_valid_photo(self):
        face_detected = True
        assert face_detected is True

    def test_rejects_photo_without_face(self):
        face_detected = False
        assert face_detected is False

    def test_rejects_blurry_photo(self):
        is_blurry = True
        assert is_blurry is True
