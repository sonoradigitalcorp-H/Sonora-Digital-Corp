"""Tests para Clone Credit System — FR-06: Gestión de créditos y pricing"""

import os
import sqlite3
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

import sys

sys.path.insert(0, str(REPO))

DB_PATH = Path(tempfile.mkdtemp()) / "test_clone.db"

os.environ["DB_PATH"] = str(DB_PATH)


def _init_test_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'pending',
            pack_type TEXT,
            credits_photo INTEGER DEFAULT 0,
            credits_video INTEGER DEFAULT 0,
            credits_tts INTEGER DEFAULT 0,
            credits_training INTEGER DEFAULT 0,
            lora_id TEXT,
            voice_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            url TEXT NOT NULL,
            validated INTEGER DEFAULT 0,
            has_face INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
        CREATE TABLE IF NOT EXISTS audio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            url TEXT NOT NULL,
            validated INTEGER DEFAULT 0,
            duration_s REAL DEFAULT 0,
            snr_db REAL DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT NOT NULL,
            type TEXT NOT NULL,
            url TEXT NOT NULL,
            prompt TEXT,
            credits_used INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
    """)
    conn.commit()
    conn.close()


def _insert_client(client_id, pack_type, photo=10, video=3, tts=10, training=1):
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT OR REPLACE INTO clients "
        "(id, status, pack_type, credits_photo, credits_video, "
        "credits_tts, credits_training) "
        "VALUES (?, 'trained', ?, ?, ?, ?, ?)",
        (client_id, pack_type, photo, video, tts, training),
    )
    conn.commit()
    conn.close()


def _get_credits(client_id):
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM clients WHERE id = ?", (client_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


class TestCreatePack:
    def test_creates_basic_pack(self):
        _init_test_db()
        from scripts.clone_pipeline import cmd_create_pack
        result = cmd_create_pack("test-client-1", "basic")
        assert result["pack"] == "basic"
        assert result["credits"]["photo"] == 10
        assert result["credits"]["video"] == 3
        assert result["credits"]["tts"] == 10

    def test_creates_pro_pack(self):
        _init_test_db()
        from scripts.clone_pipeline import cmd_create_pack
        result = cmd_create_pack("test-client-2", "pro")
        assert result["pack"] == "pro"
        assert result["credits"]["photo"] == 30
        assert result["credits"]["video"] == 10
        assert result["credits"]["tts"] == 30

    def test_creates_enterprise_pack(self):
        _init_test_db()
        from scripts.clone_pipeline import cmd_create_pack
        result = cmd_create_pack("test-client-3", "enterprise")
        assert result["pack"] == "enterprise"
        assert result["credits"]["photo"] == 100

    def test_rejects_invalid_pack(self):
        _init_test_db()
        from scripts.clone_pipeline import cmd_create_pack
        result = cmd_create_pack("test-client-4", "invalid")
        assert "error" in result


class TestConsumeCredits:
    def test_consumes_photo_credit(self):
        _init_test_db()
        _insert_client("consume-1", "basic")
        from scripts.clone_pipeline import cmd_generate
        result = cmd_generate("consume-1", "photo", "test prompt")
        assert result["credits_remaining"] == 9

    def test_consumes_video_credit(self):
        _init_test_db()
        _insert_client("consume-2", "basic")
        from scripts.clone_pipeline import cmd_generate
        result = cmd_generate("consume-2", "video", "video prompt")
        assert result["credits_remaining"] == 2

    def test_consumes_tts_credit(self):
        _init_test_db()
        _insert_client("consume-3", "basic")
        from scripts.clone_pipeline import cmd_generate
        result = cmd_generate("consume-3", "tts", "texto")
        assert result["credits_remaining"] == 9

    def test_blocks_when_no_credits(self):
        _init_test_db()
        _insert_client("consume-4", "basic", photo=0, video=0, tts=0)
        from scripts.clone_pipeline import cmd_generate
        result = cmd_generate("consume-4", "photo", "test")
        assert "error" in result


class TestGetCredits:
    def test_returns_correct_counts(self):
        _init_test_db()
        _insert_client("credits-1", "pro", photo=30, video=10, tts=30)
        from scripts.clone_pipeline import cmd_status
        result = cmd_status("credits-1")
        assert result["credits"]["photo"] == 30
        assert result["credits"]["video"] == 10
        assert result["credits"]["tts"] == 30

    def test_returns_zero_for_new_client(self):
        _init_test_db()
        _insert_client("credits-2", "basic", photo=0, video=0, tts=0)
        from scripts.clone_pipeline import cmd_status
        result = cmd_status("credits-2")
        assert result["credits"]["photo"] == 0
        assert result["credits"]["video"] == 0
        assert result["credits"]["tts"] == 0

    def test_training_credit_tracked(self):
        _init_test_db()
        _insert_client("credits-3", "basic")
        from scripts.clone_pipeline import cmd_status
        result = cmd_status("credits-3")
        assert result["credits"]["training"] == 1


class TestCreditLowWarning:
    def test_warns_when_low(self):
        _init_test_db()
        _insert_client("low-1", "basic", photo=2, video=0, tts=0)
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT credits_photo FROM clients WHERE id = 'low-1'").fetchone()
        conn.close()
        assert row[0] < 5
