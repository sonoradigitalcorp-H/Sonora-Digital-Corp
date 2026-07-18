"""Credit MCP Server — Client pack management and credit consumption for clone service.

FR-06: Gestión de créditos y pricing.
"""

import json
import os
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
DB_PATH = Path(os.environ.get("DB_PATH", str(REPO / "data" / "clone_service.db")))

PACKS = {
    "basic": {"photo": 10, "video": 3, "tts": 10, "training": 1},
    "pro": {"photo": 30, "video": 10, "tts": 30, "training": 1},
    "enterprise": {"photo": 100, "video": 30, "tts": 100, "training": 3},
}


def _get_db() -> sqlite3.Connection:
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
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
    """)
    conn.commit()
    conn.close()


async def create_pack(client_id: str, pack_type: str) -> str:
    if not client_id:
        return json.dumps({"error": "client_id is required"})
    if pack_type not in PACKS:
        return json.dumps({"error": f"Invalid pack. Options: {list(PACKS.keys())}", "client_id": client_id})

    _init_db()
    pack = PACKS[pack_type]
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT OR REPLACE INTO clients
           (id, status, pack_type, credits_photo, credits_video, credits_tts, credits_training, updated_at)
           VALUES (?, 'pending', ?, ?, ?, ?, ?, datetime('now'))""",
        (client_id, pack_type, pack["photo"], pack["video"], pack["tts"], pack["training"]),
    )
    conn.commit()
    conn.close()
    return json.dumps({
        "client_id": client_id,
        "pack": pack_type,
        "credits": pack,
        "status": "active",
        "message": f"Pack {pack_type} activado para {client_id}",
    })


async def consume_credit(client_id: str, asset_type: str) -> str:
    if not client_id:
        return json.dumps({"error": "client_id is required"})
    if asset_type not in ("photo", "video", "tts", "training"):
        return json.dumps({"error": "Invalid asset type. Options: photo, video, tts, training"})

    _init_db()
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    if not client:
        conn.close()
        return json.dumps({"error": f"Client {client_id} not found"})

    col = f"credits_{asset_type}"
    if client[col] < 1:
        conn.close()
        total = sum(client["credits_photo"], client["credits_video"], client["credits_tts"])
        return json.dumps({
            "error": f"No credits for {asset_type}",
            "remaining": 0,
            "client_id": client_id,
            "credits_low": total < 5,
        })

    cursor.execute(f"UPDATE clients SET {col} = {col} - 1, updated_at = datetime('now') WHERE id = ?", (client_id,))
    conn.commit()
    cursor.execute(f"SELECT {col} as remaining FROM clients WHERE id = ?", (client_id,))
    remaining = cursor.fetchone()["remaining"]
    total_remaining = sum(
        cursor.execute("SELECT credits_photo, credits_video, credits_tts FROM clients WHERE id = ?", (client_id,)).fetchone()
    )
    conn.close()

    return json.dumps({
        "consumed": True,
        "asset_type": asset_type,
        "credits_remaining": remaining,
        "credits_low": total_remaining < 5,
        "client_id": client_id,
    })


async def get_credits(client_id: str) -> str:
    if not client_id:
        return json.dumps({"error": "client_id is required"})

    _init_db()
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    client = cursor.fetchone()
    conn.close()

    if not client:
        return json.dumps({"error": f"Client {client_id} not found"})

    total = client["credits_photo"] + client["credits_video"] + client["credits_tts"]
    return json.dumps({
        "client_id": client_id,
        "credits": {
            "photo": client["credits_photo"],
            "video": client["credits_video"],
            "tts": client["credits_tts"],
            "training": client["credits_training"],
        },
        "total": total,
        "pack_type": client["pack_type"],
        "status": client["status"],
    })


MCP_TOOLS = {
    "create_pack": {
        "description": "Create a credit pack for a client",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client identifier"},
                "pack_type": {"type": "string", "enum": ["basic", "pro", "enterprise"], "description": "Pack type"},
            },
            "required": ["client_id", "pack_type"],
        },
        "handler": lambda args: create_pack(args["client_id"], args["pack_type"]),
    },
    "consume_credit": {
        "description": "Consume a credit for asset generation (deducts from client's pack)",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client identifier"},
                "asset_type": {"type": "string", "enum": ["photo", "video", "tts", "training"], "description": "Type of asset to consume credit for"},
            },
            "required": ["client_id", "asset_type"],
        },
        "handler": lambda args: consume_credit(args["client_id"], args["asset_type"]),
    },
    "get_credits": {
        "description": "Get remaining credits for a client",
        "input_schema": {
            "type": "object",
            "properties": {
                "client_id": {"type": "string", "description": "Client identifier"},
            },
            "required": ["client_id"],
        },
        "handler": lambda args: get_credits(args["client_id"]),
    },
}
