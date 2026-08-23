#!/usr/bin/env python3
"""telegram_bot_tubandera.py — Bot Oficial de Tu Bandera A.C. con aislamiento por tenant y sesiones independientes.

- Cada usuario inicia su conversación desde cero (no se comparte contexto).
- Se añade la columna `tenant_id` en la base SQLite para aislar datos.
- El tenant se lee de la variable de entorno `TENANT_ID` (valor típicamente "tu-bandera").
- No se guarda historial de mensajes entre usuarios.
"""

import os
import sys
import json
import time
import re
import sqlite3
import argparse
import urllib.request
import urllib.parse
import subprocess
import tempfile
from pathlib import Path
from datetime import datetime

# Import scoring utilities (already present in project)
import tubandera_scoring

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "02_Source_Code"))

# ---------------------------------------------------
# Configuración
# ---------------------------------------------------
TOKEN = os.environ.get("TELEGRAM_TUBANDERA_TOKEN") or "8952534489:AAGvk9yc-Xgrn7JCzB0Ja2tvwgp-lIHMjpk"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY") or "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Tenant identifier – must be unique per client (e.g., "tu-bandera")
TENANT_ID = os.environ.get("TENANT_ID") or "tu-bandera"

# WhatsApp notification (Roberto Lara)
ROBERTO_LARA_WA = os.environ.get("ROBERTO_WA") or "5216623645186@s.whatsapp.net"
WACLI_STORE = os.environ.get("WACLI_STORE") or "/home/mystic/.wacli"

# ---------------------------------------------------
# Base de datos (añadida columna tenant_id)
# ---------------------------------------------------
DB_DIR = BASE_DIR / "03_Infrastructure"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "tu_bandera_leads.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tu_bandera_familias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id TEXT NOT NULL,
            user_id TEXT,
            username TEXT,
            full_name TEXT,
            perfil TEXT,
            urgencia TEXT,
            mensaje TEXT,
            respuesta TEXT,
            telefono_contacto TEXT,
            notificado_roberto BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

def save_lead(user_id, username, full_name, perfil, urgencia, mensaje, respuesta, telefono="", notificado=False):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tu_bandera_familias (tenant_id, user_id, username, full_name, perfil, urgencia, mensaje, respuesta, telefono_contacto, notificado_roberto) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (TENANT_ID, str(user_id), username or "", full_name or "", perfil, urgencia, mensaje, respuesta, telefono, 1 if notificado else 0)
    )
    conn.commit()
    conn.close()

# ---------------------------------------------------
# Notificaciones a Roberto Lara via wacli
# ---------------------------------------------------
def notify_roberto_lara(full_name, phone_or_user, perfil, urgencia, servicio, mensaje_original):
    note_text = tubandera_scoring.format_roberto_notification(
        full_name=full_name,
        phone_or_user=phone_or_user,
        perfil=perfil,
        urgencia=urgencia,
        servicio_requerido=servicio,
        mensaje_original=mensaje_original
    )
    cmd = [
        "wacli", "send", "text",
        "--store", WACLI_STORE,
        "--to", ROBERTO_LARA_WA,
        "--message", note_text
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"⚠ Error enviando notificación WhatsApp: {e}", flush=True)
        return False

# ---------------------------------------------------
# Utilidades de audio
# ---------------------------------------------------
def clean_for_tts(text: str) -> str:
    # Remove emojis and exclamation marks (canonical rule)
    text = re.sub(r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\u2600-\u27BF]", "", text)
    text = text.replace("!", ".")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def text_to_ogg(text: str, out_ogg: Path) -> bool:
    clean_text = clean_for_tts(text)
    if not clean_text:
        return False
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        mp3_path = tmp_mp3.name
    try:
        # Generate mp3 via edge-tts
        cmd_tts = [
            "edge-tts",
            "--voice", "es-MX-DaliaNeural",
            "--text", clean_text,
            "--write-media", mp3_path,
            "--rate=+2%",
            "--pitch=+2Hz"
        ]
        subprocess.run(cmd_tts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        # Convert to OGG Opus
        cmd_ff = [
            "ffmpeg", "-y", "-i", mp3_path,
            "-c:a", "libopus", "-b:a", "24k",
            str(out_ogg)
        ]
        subprocess.run(cmd_ff, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        return out_ogg.exists() and out_ogg.stat().st_size > 0
    except Exception as e:
        print(f"⚠ Error generando voz TTS: {e}", flush=True)
        return False
    finally:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)

# ---------------------------------------------------
# LLM integration (OpenRouter)
# ---------------------------------------------------
def call_llm(user_message: str, user_name: str, perfil: str, urgencia_eval: dict) -> str:
    system_prompt = f"""Eres el Asistente Oficial y Especialista en Orientación Clínica, Psicológica y Psiquiátrica de Tu Bandera A.C. (Roberto Lara).\n\nREGLAS DE ORO:\n1. NUNCA des recetas médicas ni juicios de valor.\n2. Ofrecemos DIAGNÓSTICO GRATUITO mediante preguntas básicas.\n3. Resalta los servicios: TRASLADOS 24/7, TRATAMIENTO INTEGRAL, PLÁTICAS PREVENTIVAS.\n4. Si el perfil es INSTITUCION, ofrece pláticas.\n5. Menciona siempre que el CEO Roberto Lara puede contactar al usuario si es urgente.\n\nContexto actual:\n- Usuario: '{user_name}'\n- Perfil: '{perfil}'\n- Evaluación de urgencia: '{urgencia_eval['urgencia']}' (motivo: {urgencia_eval['motivo']})\n\nResponde en español, tono empático y profesional, máximo 2‑3 párrafos, sin emojis ni signos de exclamación."""
    payload = {
        "model": "deepseek/deepseek-v4-flash-0731",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.6
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data.get("choices"):
                return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"⚠ LLM error: {e}", flush=True)
    return (
        f"Hola, buenas tardes. Bienvenido a Tu Bandera A.C. Ofrecemos diagnóstico gratuito sin juicios de valor y un espacio sano para acompañar a familiares y personas que salen del centro de rehabilitación. ¿En qué podemos ayudarte hoy?Traslados 24/7 y atención integral. Por favor comparte tu teléfono para que Roberto Lara pueda contactarte.")

# ---------------------------------------------------
# Envío a Telegram
# ---------------------------------------------------
def tg_send_text(chat_id: int, text: str):
    safe_text = clean_for_tts(text)  # sanitizar antes de enviar
    url = f"{API_URL}/sendMessage"
    body = json.dumps({"chat_id": chat_id, "text": safe_text}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"✗ Error enviando texto a Telegram: {e}", flush=True)

def tg_send_voice(chat_id: int, ogg_path: Path):
    if not ogg_path.exists():
        return
    url = f"{API_URL}/sendVoice"
    try:
        if "requests" in sys.modules:
            import requests
            with open(ogg_path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"voice": f}, timeout=20)
            print(f"🔊 Nota de voz enviada a Telegram {chat_id}", flush=True)
        else:
            subprocess.run([
                "curl", "-s", "-F", f"chat_id={chat_id}",
                "-F", f"voice=@{ogg_path}", url
            ], stdout=subprocess.DEVNULL, timeout=25)
    except Exception as e:
        print(f"⚠ Error enviando nota de voz: {e}", flush=True)

# ---------------------------------------------------
# Manejo de sesiones independientes
# ---------------------------------------------------
# Diccionario que almacena el estado de cada usuario (solo para el ciclo actual)
# No se persiste entre reinicios, garantizando que siempre se empieza desde cero.
user_sessions = {}

def process_update(update: dict):
    msg = update.get("message") or update.get("edited_message")
    if not msg or "text" not in msg:
        return
    chat_id = msg["chat"]["id"]
    user_id = msg["from"].get("id")
    user_name = msg["from"].get("first_name", "Amigo")
    username = msg["from"].get("username", "")
    full_name = f"{user_name} {msg['from'].get('last_name', '')}".strip()
    text = msg["text"].strip()

    # --- INICIO DE CONVERSACIÓN: siempre se trata como sesión nueva ---
    # No reutilizamos contexto previo, sólo usamos el mensaje actual.
    perfil = tubandera_scoring.classify_user_profile(text)
    urgencia_eval = tubandera_scoring.evaluate_urgency(text)

    print(f"📩 [{perfil} | {urgencia_eval['urgencia']}] Mensaje de {full_name} (@{username}): {text}", flush=True)

    # Caso /start : mensaje de bienvenida sin historial previo
    if text.startswith("/start"):
        reply = (
            f"Hola {user_name}. Bienvenido al Asistente Oficial de Tu Bandera A.C. Ofrecemos diagnóstico gratuito sin juicios de valor. Puedes solicitar traslados 24/7, información de nuestros servicios o pláticas preventivas. ¿En qué podemos apoyarte hoy?"
        )
        tg_send_text(chat_id, reply)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            ogg_path = Path(tmp_ogg.name)
        if text_to_ogg(reply, ogg_path):
            tg_send_voice(chat_id, ogg_path)
            ogg_path.unlink(missing_ok=True)
        # Guardar lead (aunque sea inicio) para auditoría
        save_lead(user_id, username, full_name, perfil, urgencia_eval["urgencia"], text, reply)
        return

    # Generar respuesta del LLM
    reply = call_llm(text, user_name, perfil, urgencia_eval)
    tg_send_text(chat_id, reply)
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
        ogg_path = Path(tmp_ogg.name)
    if text_to_ogg(reply, ogg_path):
        tg_send_voice(chat_id, ogg_path)
        ogg_path.unlink(missing_ok=True)

    # Intentar extraer teléfono del mensaje
    tel_match = re.search(r"\b\d{10}\b", text)
    tel = tel_match.group(0) if tel_match else username or f"TG ID: {user_id}"

    # Notificar a Roberto Lara si es lead caliente o solicitud de traslado
    notificado = False
    if urgencia_eval["urgencia"] in ["ATENCION_INMEDIATA", "ALTA"] or perfil in ["FAMILIAR", "INSTITUCION"]:
        servicio_desc = "Traslado 24/7 y Atención Inmediata" if urgencia_eval["requiere_traslado"] else ("Pláticas Preventivas" if perfil == "INSTITUCION" else "Diagnóstico Gratuito")
        notificado = notify_roberto_lara(full_name, tel, perfil, urgencia_eval["urgencia"], servicio_desc, text)

    save_lead(user_id, username, full_name, perfil, urgencia_eval["urgencia"], text, reply, tel, notificado)

def run_polling():
    init_db()
    print("🚀 Bot Tu Bandera A.C. activo (sesiones aisladas por usuario) …", flush=True)
    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                for upd in data.get("result", []):
                    offset = upd["update_id"] + 1
                    process_update(upd)
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--poll", action="store_true", help="Iniciar bot en modo Polling")
    args = parser.parse_args()
    if args.poll:
        run_polling()
    else:
        print("Uso: python3 telegram_bot_tubandera.py --poll")
