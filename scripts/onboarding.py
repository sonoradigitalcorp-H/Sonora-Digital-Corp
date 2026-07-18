"""Onboarding System — Códigos de activación + routing + flow + agentic skills.

FR-01: Generación de códigos únicos (SDC-XXXXXX)
FR-02: Validación y activación de códigos
FR-03: Routing por número de teléfono
FR-04: Onboarding flow de 5 pasos
FR-06: Skills agenticas por tipo de tenant
"""

import argparse
import json
import os
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent

CODE_CHARS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 6
CODE_PREFIX = "SDC"
CODE_VALIDITY_HOURS = 6
MIN_PHOTOS = 15
DB_PATH = Path(os.environ.get(
    "ONBOARDING_DB_PATH",
    str(REPO / "data" / "onboarding.db")
))

_SKILLS = {
    "cliente": {
        "openclaw": ["clone-service", "wacli", "gallery"],
        "hermes": ["whatsapp", "notifications"],
        "opencode": ["basic", "clone", "support"],
    },
    "partner": {
        "openclaw": ["clone-service", "wacli", "gallery", "stripe", "supabase", "analytics"],
        "hermes": ["whatsapp", "telegram", "email", "notifications"],
        "opencode": ["basic", "clone", "support", "finance", "security", "admin"],
    },
    "admin": {
        "openclaw": "all",
        "hermes": "all",
        "opencode": "all",
    },
}

_FLOW = {
    1: {"delay": "0s", "message": (
        "¡Bienvenido {client_name}! Soy tu asistente digital de {partner_name}. "
        "Estoy aquí para ayudarte. ¿Por dónde quieres empezar? 🚀"
    )},
    2: {"delay": "5m", "message": (
        "¿Sabías que puedo crear fotos y videos con tu cara? 🎭 "
        "Solo necesito 15 fotos tuyas y 30s de voz. ¿Quieres probar?"
    )},
    3: {"message": (
        "¡Genial! Puedes pedirme:\n"
        "📸 Una foto tuya en cualquier lugar\n"
        "🎬 Un video presentándote\n"
        "🗣 Un mensaje de voz con tu tono"
    )},
    4: {"delay": "24h", "message": (
        "¿Cómo va todo, {client_name}? Recuerda que estoy aquí 24/7. "
        "Si necesitas algo, escríbeme."
    )},
    5: {"delay": "7d", "message": (
        "¡Tu primera semana con nosotros! 🎉\n"
        "📸 Fotos: {photos_count}  🎬 Videos: {videos_count}  "
        "💬 Conversaciones: {chat_count}\n"
        "¿Listo para la siguiente semana? 🚀"
    )},
}


def _get_db() -> sqlite3.Connection:
    os.makedirs(DB_PATH.parent, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS codes (
            id TEXT PRIMARY KEY,
            partner_id TEXT NOT NULL,
            client_name TEXT NOT NULL,
            client_phone TEXT DEFAULT '',
            plan TEXT DEFAULT 'pro',
            status TEXT DEFAULT 'active',
            expires_at TEXT NOT NULL,
            activated_at TEXT,
            tenant_id TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS routing (
            phone TEXT PRIMARY KEY,
            tenant_id TEXT NOT NULL,
            type TEXT DEFAULT 'cliente',
            name TEXT DEFAULT '',
            partner_id TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_codes_partner ON codes(partner_id);
        CREATE INDEX IF NOT EXISTS idx_codes_status ON codes(status);
    """)
    conn.commit()
    conn.close()


def _gen_code() -> str:
    return CODE_PREFIX + "".join(random.choice(CODE_CHARS) for _ in range(CODE_LENGTH))


# ---------------------------------------------------------------------------
# Public API — todas sync, retornan JSON string
# ---------------------------------------------------------------------------

def generate(partner_id: str, client_name: str, plan: str = "pro") -> str:
    if not partner_id or not client_name:
        return json.dumps({"error": "partner_id and client_name required"})

    _init_db()
    conn = _get_db()

    code = _gen_code()
    for _ in range(10):
        cursor = conn.execute("SELECT 1 FROM codes WHERE id = ?", (code,))
        if not cursor.fetchone():
            break
        code = _gen_code()
    else:
        conn.close()
        return json.dumps({"error": "could not generate unique code after 10 attempts"})

    expires = (datetime.now() + timedelta(hours=CODE_VALIDITY_HOURS)).isoformat()
    conn.execute(
        """INSERT INTO codes (id, partner_id, client_name, plan, status, expires_at)
           VALUES (?, ?, ?, ?, 'active', ?)""",
        (code, partner_id, client_name, plan, expires),
    )
    conn.commit()
    conn.close()

    wa_link = f"https://wa.me/5216623538272?text=BIENVENIDO_{code}"
    return json.dumps({
        "code": code,
        "partner_id": partner_id,
        "client_name": client_name,
        "plan": plan,
        "expires_at": expires,
        "validity_hours": CODE_VALIDITY_HOURS,
        "wa_link": wa_link,
        "status": "active",
    }, indent=2)


def validate(code: str, phone: str = "") -> str:
    if not code:
        return json.dumps({"valid": False, "reason": "code is required"})

    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM codes WHERE id = ?", (code,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return json.dumps({"valid": False, "reason": "Código no reconocido. Verifica e intenta de nuevo."})

    if row["status"] == "used":
        conn.close()
        return json.dumps({"valid": False, "reason": "Este código ya fue utilizado. Tu asistente te espera."})

    if row["status"] == "expired":
        conn.close()
        return json.dumps({"valid": False, "reason": "Este código expiró. Solicita uno nuevo con tu asesor."})

    expires = datetime.fromisoformat(row["expires_at"])
    if datetime.now() > expires:
        conn.close()
        return json.dumps({"valid": False, "reason": "Tu código expiró. Solicita uno nuevo con tu asesor."})

    if row["status"] != "active":
        conn.close()
        return json.dumps({"valid": False, "reason": "Código no válido"})

    tenant_id = f"{row['partner_id']}_{hash(phone) & 0xFFFFFFFF:08x}" if phone else f"{row['partner_id']}_default"
    now = datetime.now().isoformat()

    conn.execute(
        "UPDATE codes SET status = 'used', client_phone = ?, activated_at = ?, tenant_id = ? WHERE id = ?",
        (phone, now, tenant_id, row["id"]),
    )
    conn.execute(
        "INSERT OR REPLACE INTO routing (phone, tenant_id, type, name, partner_id) VALUES (?, ?, 'cliente', ?, ?)",
        (phone, tenant_id, row["client_name"], row["partner_id"]),
    )
    conn.commit()
    conn.close()

    return json.dumps({
        "valid": True,
        "code": row["id"],
        "tenant_id": tenant_id,
        "client_name": row["client_name"],
        "partner_id": row["partner_id"],
        "plan": row["plan"],
        "phone": phone,
        "activated_at": now,
        "message": "¡Bienvenido! Tu cerebro digital está listo.",
    }, indent=2)


def detect_tenant(phone: str) -> str:
    if not phone:
        return json.dumps({"tenant_id": None, "type": "unknown"})

    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routing WHERE phone = ?", (phone,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return json.dumps({
            "tenant_id": row["tenant_id"],
            "type": row["type"],
            "name": row["name"],
            "partner_id": row["partner_id"],
        }, indent=2, ensure_ascii=False)

    return json.dumps({
        "tenant_id": None,
        "type": "unknown",
        "message": "¡Bienvenido a Sonora Digital Corp! 🚀 ¿Tienes un código de activación? Escríbelo aquí para empezar.",
    }, indent=2, ensure_ascii=False)


def list_codes(partner_id: str = "") -> str:
    conn = _get_db()
    if partner_id:
        rows = conn.execute(
            "SELECT * FROM codes WHERE partner_id = ? ORDER BY created_at DESC",
            (partner_id,),
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM codes ORDER BY created_at DESC").fetchall()
    conn.close()
    return json.dumps({"codes": [dict(r) for r in rows], "count": len(rows)}, indent=2)


def get_flow_step(step: int, client_name: str = "", partner_name: str = "", **kwargs) -> str:
    if step not in _FLOW:
        return json.dumps({"error": "Step must be 1-5"})

    config = _FLOW[step]
    message = config.get("message", "").format(
        client_name=client_name or "cliente",
        partner_name=partner_name or "SDC",
        photos_count=kwargs.get("photos_count", "N/A"),
        videos_count=kwargs.get("videos_count", "N/A"),
        chat_count=kwargs.get("chat_count", "N/A"),
    )

    return json.dumps({
        "step": step,
        "delay": config.get("delay", "0s"),
        "channel": "whatsapp",
        "message": message,
    }, indent=2, ensure_ascii=False)


def get_skills(tenant_type: str = "cliente") -> str:
    skills = _SKILLS.get(tenant_type, _SKILLS["cliente"])
    return json.dumps({
        "tenant_type": tenant_type,
        "skills": skills,
    }, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="SDC Onboarding System")
    subparsers = parser.add_subparsers(dest="command")

    gen = subparsers.add_parser("generate", help="Generate onboarding code")
    gen.add_argument("--partner", required=True)
    gen.add_argument("--client", required=True)
    gen.add_argument("--plan", default="pro", choices=["basic", "pro", "enterprise"])

    val = subparsers.add_parser("validate", help="Validate code")
    val.add_argument("code")
    val.add_argument("--phone", default="")

    det = subparsers.add_parser("detect", help="Detect tenant by phone")
    det.add_argument("phone")

    lst = subparsers.add_parser("list", help="List codes")
    lst.add_argument("--partner", default="")

    flow = subparsers.add_parser("flow", help="Get onboarding flow step")
    flow.add_argument("step", type=int)
    flow.add_argument("--name", default="")
    flow.add_argument("--partner-name", default="")

    skills = subparsers.add_parser("skills", help="Get skills for tenant type")
    skills.add_argument("type", nargs="?", default="cliente", choices=["cliente", "partner", "admin"])

    args = parser.parse_args()

    if args.command == "generate":
        print(generate(args.partner, args.client, args.plan))
    elif args.command == "validate":
        print(validate(args.code, args.phone))
    elif args.command == "detect":
        print(detect_tenant(args.phone))
    elif args.command == "list":
        print(list_codes(args.partner))
    elif args.command == "flow":
        print(get_flow_step(args.step, args.name, args.partner_name))
    elif args.command == "skills":
        print(get_skills(args.type))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
