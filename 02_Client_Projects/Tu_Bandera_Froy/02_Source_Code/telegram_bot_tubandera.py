#!/usr/bin/env python3
"""telegram_bot_tubandera.py — Bot Oficial EXCLUSIVO de Tu Bandera A.C.

Bot Username: @TBasistente_bot
CEO: Roberto Lara (WhatsApp: 6623645186)

Capacidades:
1. Especialista en orientación clínica, psicológica y psiquiátrica (sin prescripciones médicos ni juicios de valor).
2. Diagnóstico Gratuito preliminar de urgencia (Atención Inmediata, Alta, Moderada).
3. Clasificación de contactos: DIRECTO | FAMILIAR | INSTITUCION.
4. Servicios destacados:
   - Traslados 24/7 (vamos por el usuario a donde sea que esté o traslados centro a centro).
   - Tratamiento integral (Psicológico, Psiquiátrico, 12 Pasos NA, Apoyo Espiritual).
   - Costos y servicios variables según el caso.
5. Notificación automática en tiempo real a Roberto Lara por WhatsApp (vía wacli) al calificar leads calientes o traslados.
6. Respuestas DUALES en TEXTO y VOZ (edge-tts es-MX-DaliaNeural).
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

sys.path.insert(0, "/opt/hermes/tubandera")
from guards import is_injection
try:
    from personas_db import init as pdb_init, registrar_usuario, get_usuario, guardar_lead
except Exception:
    pdb_init = registrar_usuario = get_usuario = guardar_lead = None

from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    requests = None

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "02_Source_Code"))

import tubandera_scoring  # noqa: E402

DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "tu_bandera_leads.db"

TOKEN = os.environ.get("TELEGRAM_TUBANDERA_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# CEO Contact
ROBERTO_LARA_WA = "5216623645186@s.whatsapp.net"
WACLI_STORE = str(Path.home() / ".wacli")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tu_bandera_familias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )
    """)
    conn.commit()
    conn.close()


def save_lead(user_id, username, full_name, perfil, urgencia, mensaje, respuesta, telefono="", notificado=False):
    """Persiste en Supabase (fuente única de leads). Fallback: sqlite local en data/ si falla."""
    nombre = full_name or username or f"TG {user_id}"
    tel = telefono or (username or f"TG {user_id}")
    try:
        pdb_init()
        guardar_lead(user_id, nombre, tel, perfil, urgencia, mensaje, respuesta,
                     canal="telegram", estado="nuevo")
        return
    except Exception as e:
        print(f"[tubandera] Supabase save_lead fallo, fallback sqlite: {e}", flush=True)
    # Fallback local
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tu_bandera_familias (user_id, username, full_name, perfil, urgencia, mensaje, respuesta, telefono_contacto, notificado_roberto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(user_id), username or "", full_name or "", perfil, urgencia, mensaje, respuesta, telefono, 1 if notificado else 0))
    conn.commit()
    conn.close()


def notify_roberto_lara(full_name: str, phone_or_user: str, perfil: str, urgencia: str, servicio: str, mensaje: str):
    """Envia notificación a Roberto Lara por WhatsApp mediante wacli."""
    note_text = tubandera_scoring.format_roberto_notification(
        full_name=full_name,
        phone_or_user=phone_or_user,
        perfil=perfil,
        urgencia=urgencia,
        servicio_requerido=servicio,
        mensaje_original=mensaje
    )

    print(f"📲 Notificando a Roberto Lara por WhatsApp ({ROBERTO_LARA_WA})...", flush=True)

    wacli_bin = "/home/mystic/wacli" if os.path.exists("/home/mystic/wacli") else "wacli"
    cmd = [
        wacli_bin, "send", "text",
        "--store", WACLI_STORE,
        "--to", ROBERTO_LARA_WA,
        "--message", note_text
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
        if res.returncode == 0:
            print(f"  ✓ Notificación enviada a Roberto Lara con éxito.", flush=True)
            return True
        else:
            print(f"  ⚠ wacli aviso: {res.stderr[:200]}", flush=True)
    except Exception as e:
        print(f"  ⚠ Error enviando aviso wacli a Roberto Lara: {e}", flush=True)
    return False


def clean_for_tts(text: str) -> str:
    text = re.sub(r"<(?:thinking|reasoning)[^>]*>.*?</(?:thinking|reasoning)>", "", text, flags=re.S)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]", "", text)
    text = text.replace("!", ".").replace("¡", "").replace("¿", "").replace("?", ".")
    text = re.sub(r"[*_`#>\-]{1,}", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[.,]{2,}", ".", text)
    return text.strip()


def text_to_ogg(text: str, out_ogg: Path) -> bool:
    text_clean = clean_for_tts(text)
    if not text_clean:
        return False

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
        mp3_path = tmp_mp3.name

    try:
        cmd_tts = [
            "edge-tts",
            "--voice", "es-MX-DaliaNeural",
            "--text", text_clean,
            "--write-media", mp3_path,
            "--rate=+2%",
            "--pitch=+2Hz"
        ]
        subprocess.run(cmd_tts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)

        cmd_ff = [
            FFMPEG, "-y", "-i", mp3_path,
            "-c:a", "libopus", "-b:a", "24k",
            str(out_ogg)
        ]
        subprocess.run(cmd_ff, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        return out_ogg.exists() and out_ogg.stat().st_size > 0
    except Exception as e:
        print(f"  ⚠ Error generando voz TTS: {e}", flush=True)
        return False
    finally:
        if os.path.exists(mp3_path):
            os.remove(mp3_path)


def call_llm(user_message: str, user_name: str, perfil: str, urgencia_eval: dict) -> str:
    # UNIFICADO: delega al endpoint unico (vps_ai_server) con persona tubandera
    # para que Telegram y la web contesten IDENTICO. Inyectamos contexto por usuario.
    contexto = (
        f"[Contexto del contacto] Usuario: {user_name}. "
        f"Perfil clasificado: {perfil}. "
        f"Urgencia: {urgencia_eval['urgencia']} (Motivo: {urgencia_eval['motivo']}). "
        f"Mensaje: {user_message}"
    )
    payload = {
        "person": "tubandera",
        "messages": [{"role": "user", "content": contexto}],
        "max_tokens": 800
    }
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:8643/api/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
            choices = data.get("choices", [])
            if choices:
                msg = choices[0].get("message", {})
                content = msg.get("content", "")
                if content:
                    return content.strip()
    except Exception as e:
        print(f"  ⚠ Fallo endpoint unificado: {e}", flush=True)

    return (
        f"Hola {user_name}. En Tu Bandera A.C. te ofrecemos un Diagnóstico Gratuito inicial sin juicios de valor. "
        f"Contamos con atención psicológica, psiquiátrica y servicio de Traslados 24/7 (vamos por el usuario a donde esté). "
        f"Compártenos tu teléfono de contacto y nuestro equipo clínico se comunicará de inmediato."
    )


def tg_send_text(chat_id: int, text: str):
    url = f"{API_URL}/sendMessage"
    body = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  ✗ Error enviando texto a Telegram: {e}", flush=True)


def tg_send_voice(chat_id: int, ogg_path: Path):
    if not ogg_path.exists():
        return
    url = f"{API_URL}/sendVoice"
    try:
        if requests:
            with open(ogg_path, "rb") as f:
                requests.post(url, data={"chat_id": chat_id}, files={"voice": f}, timeout=20)
            print(f"  🔊 Nota de voz enviada a Telegram chat {chat_id}", flush=True)
        else:
            subprocess.run([
                "curl", "-s", "-F", f"chat_id={chat_id}",
                "-F", f"voice=@{ogg_path}", url
            ], stdout=subprocess.DEVNULL, timeout=25)
    except Exception as e:
        print(f"  ⚠ Error enviando nota de voz: {e}", flush=True)


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
    if is_injection(text):
        tg_send_text(chat_id, "Prefiero acompañarte en lo que necesitas. Cómo te sientes hoy?")
        return
    # GUARDA INJECTION
    # TRAZABILIDAD: tenant_id + reconocimiento
    if registrar_usuario is not None:
        try:
            pdb_init()
            _u = get_usuario(chat_id)
            if not _u:
                _tid = registrar_usuario(chat_id, (full_name or username or str(chat_id)), "")
                print(f"[tubandera] nuevo usuario registrado {_tid}", flush=True)
        except Exception as e:
            print("[tubandera] db err:", e, flush=True)

    # Clasificación y diagnóstico de urgencia
    perfil = tubandera_scoring.classify_user_profile(text)
    urgencia_eval = tubandera_scoring.evaluate_urgency(text)

    print(f"📩 [{perfil} | {urgencia_eval['urgencia']}] Mensaje de {full_name} (@{username}): {text}", flush=True)

    if text.startswith("/start"):
        reply = (
            f"¡Hola {user_name}! Te damos la bienvenida al **Asistente Oficial de Tu Bandera A.C.** 🕊️\n\n"
            f"Ofrecemos orientación clínica, psicológica y psiquiátrica sin juicios de valor:\n"
            f"✅ **Diagnóstico Gratuito Inicial**\n"
            f"🚚 **Servicio de Traslados 24/7** (vamos por el usuario a donde esté o traslados centro a centro)\n"
            f"🧠 **Tratamiento Integral** (Psicológico, Psiquiátrico, 12 Pasos NA y Apoyo Espiritual)\n"
            f"🏫 **Pláticas Preventivas para Instituciones y Empresas**\n\n"
            f"¿En qué podemos apoyarte a ti, a tu familia o a tu institución hoy?"
        )
        tg_send_text(chat_id, reply)
        save_lead(user_id, username, full_name, perfil, urgencia_eval["urgencia"], text, reply)

        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
            ogg_p = Path(tmp_ogg.name)
        if text_to_ogg(reply, ogg_p):
            tg_send_voice(chat_id, ogg_p)
            if ogg_p.exists(): os.remove(ogg_p)
        return

    # Generar respuesta LLM especializada
    reply = call_llm(text, user_name, perfil, urgencia_eval)

    # 1. Enviar TEXTO
    tg_send_text(chat_id, reply)

    # 2. Enviar VOZ
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp_ogg:
        ogg_p = Path(tmp_ogg.name)
    if text_to_ogg(reply, ogg_p):
        tg_send_voice(chat_id, ogg_p)
        if ogg_p.exists(): os.remove(ogg_p)

    # Buscar teléfono en texto si existe
    tel_m = re.search(r"\b\d{10}\b", text)
    tel = tel_m.group(0) if tel_m else (username or f"TG ID: {user_id}")

    # NOTIFICAR A ROBERTO LARA si es urgente, familiar, solicitud de traslado o institución
    notificado = False
    if urgencia_eval["urgencia"] in ["ATENCION_INMEDIATA", "ALTA"] or perfil in ["FAMILIAR", "INSTITUCION"] or urgencia_eval["requiere_traslado"]:
        servicio_desc = "Traslado 24/7 y Atención Inmediata" if urgencia_eval["requiere_traslado"] else ("Pláticas Preventivas" if perfil == "INSTITUCION" else "Internamiento y Diagnóstico Gratuito")
        notificado = notify_roberto_lara(
            full_name=full_name,
            phone_or_user=tel,
            perfil=perfil,
            urgencia=urgencia_eval["urgencia"],
            servicio=servicio_desc,
            mensaje=text
        )

    save_lead(user_id, username, full_name, perfil, urgencia_eval["urgencia"], text, reply, tel, notificado)


def run_polling():
    init_db()
    print(f"🚀 Bot Tu Bandera A.C. (@TBasistente_bot) activo (Notificaciones a Roberto Lara 6623645186)...", flush=True)
    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates?offset={offset}&timeout=20"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode())
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    process_update(update)
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

