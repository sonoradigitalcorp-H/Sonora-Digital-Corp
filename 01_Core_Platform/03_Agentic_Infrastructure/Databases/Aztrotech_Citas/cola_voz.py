#!/usr/bin/env python3
"""cola_voz.py — Procesador de solicitudes de voz encoladas por el agente.

El agente de AztroTech SOLO tiene tool `fs` (no bash). Cuando un cliente pida
voz, el agente NO ejecuta nada: escribe un JSON en voz_pendientes/. Este
procesador (corrido por cron) genera la nota de voz y la envía al chat.

ANTI-REPETIDOS: tabla `enviados` en voz.db guarda un hash de (chat + texto).
Si un mensaje ya se envió a ese chat, NO se vuelve a mandar.

JSON esperado en voz_pendientes/:
    {"chat": "5738935134", "text": "mensaje a decir", "voice": "es-MX-DaliaNeural"}

Uso:
    python3 cola_voz.py process    # consume la cola y manda (cron cada minuto)
    python3 cola_voz.py status     # muestra lo encolado
"""
import argparse, hashlib, json, sqlite3, subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
QUEUE = BASE / "voz_pendientes"
DONE = BASE / "voz_enviadas"
DB = BASE / "voz.db"
VOICE_REPLY = BASE.parent.parent / "voice_reply.py"   # 03_Agentic_Infrastructure/voice_reply.py
DEFAULT_VOICE = "es-MX-DaliaNeural"


def ensure_dirs():
    QUEUE.mkdir(parents=True, exist_ok=True)
    DONE.mkdir(parents=True, exist_ok=True)


def connect():
    c = sqlite3.connect(DB)
    c.execute("""
        CREATE TABLE IF NOT EXISTS enviados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat TEXT, texto_hash TEXT, ts TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chat, texto_hash)
        )
    """)
    c.commit()
    return c


def h(chat, text):
    return hashlib.sha1(f"{chat}|{text}".encode()).hexdigest()


def ya_enviado(c, chat, text):
    return c.execute("SELECT 1 FROM enviados WHERE chat=? AND texto_hash=?",
                     (chat, h(chat, text))).fetchone() is not None


def marcar_enviado(c, chat, text):
    c.execute("INSERT OR IGNORE INTO enviados (chat, texto_hash) VALUES (?,?)",
              (chat, h(chat, text)))
    c.commit()


def process():
    ensure_dirs()
    c = connect()
    pendientes = sorted(QUEUE.glob("*.json"))
    if not pendientes:
        print("[COLA] sin voz pendiente.")
        return 0
    enviados = 0
    for f in pendientes:
        try:
            d = json.loads(f.read_text())
        except Exception as e:
            print(f"[ROTO] {f.name}: {e}")
            f.rename(DONE / f.name)
            continue
        chat = str(d.get("chat", "")).strip()
        text = str(d.get("text", "")).strip()
        voice = d.get("voice", DEFAULT_VOICE)
        if not chat or not text:
            print(f"[INV] {f.name}: falta chat o text. skip")
            continue
        if ya_enviado(c, chat, text):
            print(f"[DUP] {f.name}: ya enviado a {chat}. skip")
            f.rename(DONE / f.name)
            continue
        r = subprocess.run(
            [sys.executable, str(VOICE_REPLY), "--bot", "aztroc",
             "--chat", chat, "--text", text, "--voice", voice],
            capture_output=True, text=True, timeout=90)
        if "OK" in r.stdout:
            marcar_enviado(c, chat, text)
            f.rename(DONE / f.name)
            enviados += 1
            print(f"[OK] {chat}: {text[:50]}...")
        else:
            print(f"[FAIL] {chat}: {r.stdout or r.stderr[:150]}")
    c.close()
    print(f"[COLA] {enviados} audio enviado.")
    return enviados


def status():
    ensure_dirs()
    pend = sorted(QUEUE.glob("*.json"))
    if not pend:
        print("  cola de voz vacía.")
    for f in pend:
        try:
            d = json.loads(f.read_text())
            print(f"  {f.name}: chat={d.get('chat')} text={d.get('text','')[:40]}")
        except Exception:
            print(f"  {f.name}: (roto)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="process",
                    choices=["process", "status"])
    a = ap.parse_args()
    (status if a.cmd == "status" else process)()