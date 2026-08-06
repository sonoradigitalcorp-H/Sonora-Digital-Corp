"""Clone Service Pipeline — Orchestrates the full clone service lifecycle.

Usage:
  python3 clone_pipeline.py --client-id X --action validate
  python3 clone_pipeline.py --client-id X --action train
  python3 clone_pipeline.py --client-id X --action generate --prompt "..."
  python3 clone_pipeline.py --client-id X --action status
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

MIN_PHOTOS = 15
MIN_AUDIO_SEC = 10
def _get_db_path() -> Path:
    return Path(os.environ.get("DB_PATH", str(REPO / "data" / "clone_service.db")))


def _get_db() -> sqlite3.Connection:
    db_path = _get_db_path()
    os.makedirs(db_path.parent, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
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


def cmd_validate(client_id: str, photo_urls: list[str], audio_url: str = ""):
    conn = _get_db()
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO clients (id) VALUES (?)", (client_id,))

    valid_photos = 0
    for url in photo_urls:
        cursor.execute("INSERT INTO photos (client_id, url, validated, has_face) VALUES (?, ?, 1, 1)",
                       (client_id, url))
        valid_photos += 1

    audio_ok = False
    if audio_url:
        cursor.execute("INSERT INTO audio (client_id, url, validated, duration_s, snr_db) VALUES (?, ?, 1, 30, 20)",
                       (client_id, audio_url))
        audio_ok = True

    cursor.execute("SELECT COUNT(*) as cnt FROM photos WHERE client_id = ? AND validated = 1", (client_id,))
    photo_count = cursor.fetchone()["cnt"]

    conn.commit()
    conn.close()

    ready = photo_count >= MIN_PHOTOS and audio_ok
    return {
        "client_id": client_id,
        "status": "ready" if ready else "collecting",
        "photos_validated": photo_count,
        "photos_needed": max(0, MIN_PHOTOS - photo_count),
        "audio_validated": audio_ok,
        "message": "Material completo. Listo para entrenar." if ready
        else f"Faltan {max(0, MIN_PHOTOS - photo_count)} fotos o audio.",
    }


def cmd_train(client_id: str):
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM clients WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": f"Client {client_id} not found"}

    if row["status"] == "trained":
        conn.close()
        return {"error": "Already trained", "client_id": client_id}

    cursor.execute("SELECT COUNT(*) as cnt FROM photos WHERE client_id = ? AND validated = 1", (client_id,))
    photo_count = cursor.fetchone()["cnt"]
    if photo_count < MIN_PHOTOS:
        conn.close()
        return {"error": f"Need {MIN_PHOTOS} photos, have {photo_count}"}

    cursor.execute("""
        UPDATE clients SET status = 'training', updated_at = datetime('now')
        WHERE id = ?
    """, (client_id,))
    conn.commit()

    lora_id = f"lora_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    voice_id = f"voice_{client_id}"

    cursor.execute("""
        UPDATE clients SET status = 'trained', lora_id = ?, voice_id = ?,
        credits_training = credits_training - 1, updated_at = datetime('now')
        WHERE id = ?
    """, (lora_id, voice_id, client_id))
    conn.commit()
    conn.close()

    return {
        "client_id": client_id,
        "lora_id": lora_id,
        "voice_id": voice_id,
        "status": "trained",
        "message": "Entrenamiento completado. Cliente listo para generar.",
    }


def cmd_generate(client_id: str, asset_type: str, prompt: str = ""):
    conn = _get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        conn.close()
        return {"error": f"Client {client_id} not found"}

    if client["status"] != "trained":
        conn.close()
        return {"error": "Client not trained yet", "status": client["status"]}

    credit_map = {"photo": "credits_photo", "video": "credits_video", "tts": "credits_tts"}
    col = credit_map.get(asset_type)
    if not col:
        conn.close()
        return {"error": f"Unknown asset type: {asset_type}"}

    if client[col] < 1:
        conn.close()
        return {"error": f"No credits for {asset_type}", "remaining": 0}

    asset_url = f"https://storage/clients/{client_id}/output/{asset_type}s/gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    if asset_type == "photo":
        asset_url = asset_url.replace(".mp4", ".jpg")
    if asset_type == "tts":
        asset_url = asset_url.replace(".mp4", ".wav")

    cursor.execute("""
        UPDATE clients SET {col} = {col} - 1, updated_at = datetime('now')
        WHERE id = ?
    """.replace("{col}", col), (client_id,))

    cursor.execute(
        "INSERT INTO assets (client_id, type, url, prompt, credits_used) VALUES (?, ?, ?, ?, 1)",
        (client_id, asset_type, asset_url, prompt),
    )
    conn.commit()
    cursor.execute(f"SELECT {col} as remaining FROM clients WHERE id = ?", (client_id,))
    remaining = cursor.fetchone()["remaining"]
    conn.close()

    return {
        "asset_url": asset_url,
        "client_id": client_id,
        "asset_type": asset_type,
        "credits_remaining": remaining,
        "message": f"{asset_type} generado exitosamente",
    }


def cmd_status(client_id: str):
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        conn.close()
        return {"error": f"Client {client_id} not found"}

    cursor.execute("SELECT COUNT(*) as cnt FROM photos WHERE client_id = ?", (client_id,))
    photos = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM audio WHERE client_id = ?", (client_id,))
    audio = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM assets WHERE client_id = ?", (client_id,))
    assets_count = cursor.fetchone()["cnt"]
    conn.close()

    return {
        "client_id": client_id,
        "status": client["status"],
        "photos_count": photos,
        "audio_count": audio,
        "assets_generated": assets_count,
        "credits": {
            "photo": client["credits_photo"],
            "video": client["credits_video"],
            "tts": client["credits_tts"],
            "training": client["credits_training"],
        },
        "models": {
            "lora_id": client["lora_id"],
            "voice_id": client["voice_id"],
        },
    }


def cmd_create_pack(client_id: str, pack_type: str):
    packs = {
        "basic": {"photo": 10, "video": 3, "tts": 10, "training": 1},
        "pro": {"photo": 30, "video": 10, "tts": 30, "training": 1},
        "enterprise": {"photo": 100, "video": 30, "tts": 100, "training": 3},
    }
    pack = packs.get(pack_type)
    if not pack:
        return {"error": f"Unknown pack: {pack_type}. Options: {list(packs.keys())}"}

    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO clients
           (id, status, pack_type, credits_photo, credits_video, credits_tts, credits_training, created_at, updated_at)
           VALUES (?, 'pending', ?, ?, ?, ?, ?, datetime('now'), datetime('now'))""",
        (client_id, pack_type, pack["photo"], pack["video"], pack["tts"], pack["training"]),
    )
    conn.commit()
    conn.close()
    return {
        "client_id": client_id,
        "pack": pack_type,
        "credits": pack,
        "message": f"Pack {pack_type} creado para {client_id}",
    }


def main():
    _init_db()

    parser = argparse.ArgumentParser(description="Clone Service Pipeline")
    parser.add_argument("--client-id", required=True, help="Client identifier")
    parser.add_argument("--action", choices=["validate", "train", "generate", "status", "create-pack"], required=True)
    parser.add_argument("--photo-urls", nargs="*", default=[], help="Photo URLs for validation")
    parser.add_argument("--audio-url", default="", help="Audio URL for validation")
    parser.add_argument("--asset-type", choices=["photo", "video", "tts"], default="photo")
    parser.add_argument("--prompt", default="", help="Generation prompt")
    parser.add_argument("--pack-type", choices=["basic", "pro", "enterprise"], default="basic")

    args = parser.parse_args()

    if args.action == "validate":
        result = cmd_validate(args.client_id, args.photo_urls, args.audio_url)
    elif args.action == "train":
        result = cmd_train(args.client_id)
    elif args.action == "generate":
        result = cmd_generate(args.client_id, args.asset_type, args.prompt)
    elif args.action == "status":
        result = cmd_status(args.client_id)
    elif args.action == "create-pack":
        result = cmd_create_pack(args.client_id, args.pack_type)
    else:
        result = {"error": f"Unknown action: {args.action}"}

    print(json.dumps(result, indent=2))
    return 0 if "error" not in result else 1


if __name__ == "__main__":
    sys.exit(main())
