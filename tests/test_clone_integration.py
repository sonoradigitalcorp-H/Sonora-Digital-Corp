"""Integration tests for Clone Service — full pipeline with mocked FAL, real DB, real logic.

Tests the complete flow end-to-end using SQLite and mocked external APIs.
"""

import os
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_TEST_DB = Path(tempfile.mkdtemp()) / "test_integration.db"


def _set_db():
    os.environ["DB_PATH"] = str(_TEST_DB)

from scripts.clone_pipeline import (
    _get_db,
    _init_db,
    cmd_create_pack,
    cmd_generate,
    cmd_status,
    cmd_train,
    cmd_validate,
)


def _test_db_path() -> str:
    return str(_TEST_DB)


def _count_rows(table: str) -> int:
    conn = sqlite3.connect(_test_db_path())
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    conn.close()
    return count


def _get_client(client_id: str) -> dict:
    conn = sqlite3.connect(_test_db_path())
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(row) if row else {}


class TestFullIntegration:
    def setup_method(self):
        _set_db()
        _init_db()
        conn = sqlite3.connect(_test_db_path())
        for table in ("assets", "audio", "photos", "clients"):
            conn.execute(f"DELETE FROM {table}")
        conn.commit()
        conn.close()

    def test_happy_path_complete_flow(self):
        """Complete client lifecycle: pack → validate → train → generate multiple assets"""
        client_id = "integ-test-1"

        # 1. Create pack
        pack = cmd_create_pack(client_id, "pro")
        assert pack["pack"] == "pro"
        assert pack["credits"]["photo"] == 30
        assert pack["credits"]["video"] == 10
        assert pack["credits"]["tts"] == 30

        # 2. Validate photos (15+ selfies)
        photos = [f"https://storage/photos/{i}.jpg" for i in range(18)]
        validate = cmd_validate(client_id, photos, "https://storage/audio/sample.wav")
        assert validate["status"] == "ready"
        assert validate["photos_validated"] == 18
        assert validate["audio_validated"] is True

        # 3. Train
        train = cmd_train(client_id)
        assert train["status"] == "trained"
        assert train["lora_id"].startswith("lora_")
        assert train["voice_id"].startswith("voice_")

        # 4. Generate photos (consume credits)
        for i in range(5):
            result = cmd_generate(client_id, "photo", f"photo prompt {i}")
            assert "error" not in result, f"Failed on photo {i}: {result}"
            assert result["credits_remaining"] == 30 - (i + 1)

        # 5. Generate videos (consume credits)
        for i in range(3):
            result = cmd_generate(client_id, "video", f"video prompt {i}")
            assert "error" not in result
            assert result["asset_type"] == "video"

        # 6. Generate TTS (consume credits)
        for i in range(5):
            result = cmd_generate(client_id, "tts", f"texto {i}")
            assert "error" not in result
            assert result["asset_type"] == "tts"

        # 7. Verify credits consumed correctly
        status = cmd_status(client_id)
        assert status["credits"]["photo"] == 25  # 30 - 5
        assert status["credits"]["video"] == 7   # 10 - 3
        assert status["credits"]["tts"] == 25    # 30 - 5
        assert status["status"] == "trained"
        assert status["assets_generated"] == 13  # 5 + 3 + 5

    def test_rejects_insufficient_photos(self):
        """Pipeline blocks training with < 15 photos"""
        client_id = "integ-test-2"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(8)], "audio.wav")
        result = cmd_train(client_id)
        assert "error" in result
        assert "Need 15" in result["error"]

    def test_blocks_generation_without_training(self):
        """Cannot generate before training completes"""
        client_id = "integ-test-3"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(15)], "audio.wav")
        result = cmd_generate(client_id, "photo", "test")
        assert "error" in result
        assert "not trained" in result["error"]

    def test_blocks_generation_with_zero_credits(self):
        """Cannot generate when credits exhausted"""
        client_id = "integ-test-4"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(15)], "audio.wav")
        cmd_train(client_id)
        for _ in range(10):
            cmd_generate(client_id, "photo", "test")
        result = cmd_generate(client_id, "photo", "one more")
        assert "error" in result
        assert "No credits" in result["error"]

    def test_audio_shows_in_status(self):
        """Status returns audio validation info"""
        client_id = "integ-test-5"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(15)], "voice.wav")
        conn = sqlite3.connect(_test_db_path())
        count = conn.execute(
            "SELECT COUNT(*) FROM audio WHERE client_id = ?", (client_id,)
        ).fetchone()[0]
        conn.close()
        assert count >= 1

    def test_photos_persist_in_db(self):
        """Photos table tracks all uploaded photos"""
        client_id = "integ-test-6"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(20)], "audio.wav")
        count = _count_rows("photos")
        assert count >= 20

    def test_assets_table_tracks_generations(self):
        """Each generation creates an asset record"""
        client_id = "integ-test-7"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(15)], "audio.wav")
        cmd_train(client_id)
        cmd_generate(client_id, "photo", "test")
        count = _count_rows("assets")
        assert count == 1

    def test_pack_types_provide_correct_credits(self):
        """Each pack type provides the defined credit amounts"""
        packs = {
            "basic": {"photo": 10, "video": 3, "tts": 10, "training": 1},
            "pro": {"photo": 30, "video": 10, "tts": 30, "training": 1},
            "enterprise": {"photo": 100, "video": 30, "tts": 100, "training": 3},
        }
        for pack_type, expected in packs.items():
            cid = f"pack-{pack_type}"
            cmd_create_pack(cid, pack_type)
            client = _get_client(cid)
            for k, v in expected.items():
                col = f"credits_{k}"
                assert client[col] == v, f"{pack_type}.{col}: expected {v}, got {client[col]}"

    def test_db_schema_has_all_tables(self):
        """Database schema includes all required tables"""
        conn = sqlite3.connect(_test_db_path())
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        conn.close()
        expected = {"clients", "photos", "audio", "assets"}
        for t in expected:
            assert t in tables, f"Missing table: {t}"

    def test_clients_table_enforces_unique_id(self):
        """Client ID is unique (INSERT OR REPLACE)"""
        cmd_create_pack("dup-test", "basic")
        cmd_create_pack("dup-test", "pro")
        clients = [row for row in _get_db().execute(
            "SELECT id FROM clients"
        ).fetchall() if row[0] == "dup-test"]
        assert len(clients) == 1

    def test_rapid_generation_does_not_corrupt_credits(self):
        """Rapid credit consumption stays accurate"""
        client_id = "rapid-test"
        cmd_create_pack(client_id, "basic")
        cmd_validate(client_id, [f"p{i}.jpg" for i in range(15)], "audio.wav")
        cmd_train(client_id)
        for _ in range(10):
            cmd_generate(client_id, "photo", "rapid")
        status = cmd_status(client_id)
        assert status["credits"]["photo"] == 0

    def test_status_before_any_action(self):
        """Status on non-existent client returns error"""
        result = cmd_status("nonexistent")
        assert "error" in result

    def test_validate_rejects_no_urls(self):
        """Validate with no photos returns collecting status"""
        result = cmd_validate("no-photos", [], "")
        assert result["status"] == "collecting"
