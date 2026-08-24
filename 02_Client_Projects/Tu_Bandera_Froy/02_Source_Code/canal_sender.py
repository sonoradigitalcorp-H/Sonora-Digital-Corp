#!/usr/bin/env python3
"""canal_sender.py — Publicador automático al canal de Telegram "Tu Bandera Aprende".

Canal: @TuBanderaAprende  (crear manualmente y agregar el bot como administrador)
Bot:   @TBasistente_bot   (mismo token que el bot de atención)

Funciones:
  - post_to_channel(text)     : publica mensaje al canal
  - post_daily_tip()          : extrae chunk de KB, reformatea con LLM → publica
  - post_community_prompt()   : mensaje de apertura para grupos comunitarios

Cron sugerido (ejecutar en VPS):
  0 8 * * * /opt/hermes/venv/bin/python3 /opt/hermes/tubandera/canal_sender.py --daily >> /var/log/canal_tubandera.log 2>&1
  0 20 * * * /opt/hermes/venv/bin/python3 /opt/hermes/tubandera/canal_sender.py --community >> /var/log/canal_tubandera.log 2>&1

Setup (una vez):
  1. Crea canal @TuBanderaAprende desde la app de Telegram (Roberto lo hace).
  2. Agrega @TBasistente_bot como administrador con permiso "Publicar mensajes".
  3. Copia el chat_id del canal (usa --get-id para obtenerlo).
  4. Pon CANAL_CHAT_ID en el .env del servicio.
"""

import os
import sys
import json
import random
import glob
import argparse
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

# ─── Config ──────────────────────────────────────────────────────────────────
TOKEN         = os.environ.get("TELEGRAM_TUBANDERA_TOKEN")
CANAL_CHAT_ID = os.environ.get("CANAL_CHAT_ID", "")          # ej: "-1001234567890"
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
KB_PATH       = os.environ.get("KB_PATH", "/opt/hermes/tubandera/kb")
API_URL       = f"https://api.telegram.org/bot{TOKEN}"

# Hashtags canónicos del canal
HASHTAGS = "#adicciones #recuperacion #TuBanderaAC #familia #12pasos"

# ─── API Telegram helpers ─────────────────────────────────────────────────────
def _tg_post(endpoint: str, body: dict) -> dict:
    url = f"{API_URL}/{endpoint}"
    data = json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[canal] Error TG API: {e}", flush=True)
        return {}


def post_to_channel(text: str, parse_mode: str = "HTML") -> bool:
    """Publica mensaje formateado al canal."""
    if not CANAL_CHAT_ID:
        print("[canal] ⚠ CANAL_CHAT_ID no configurado", flush=True)
        return False
    result = _tg_post("sendMessage", {
        "chat_id":    CANAL_CHAT_ID,
        "text":       text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    })
    ok = result.get("ok", False)
    print(f"[canal] {'✅ publicado' if ok else '❌ error'}: {text[:60]}...", flush=True)
    return ok


def get_channel_id() -> None:
    """Imprime chat_id del canal (ejecutar después de mandar un mensaje al canal)."""
    result = _tg_post("getUpdates", {})
    updates = result.get("result", [])
    for u in updates:
        chat = u.get("message", {}).get("chat", {}) or u.get("channel_post", {}).get("chat", {})
        if chat.get("type") in ("channel", "group", "supergroup"):
            print(f"  Chat encontrado: id={chat.get('id')}  title={chat.get('title')}")


# ─── KB loader ────────────────────────────────────────────────────────────────
def _load_random_chunk() -> tuple[str, str]:
    """Devuelve (chunk_text, fuente) aleatorio de la KB."""
    chunks = []
    for path in glob.glob(f"{KB_PATH}/**/*.md", recursive=True):
        try:
            txt = open(path, encoding="utf-8").read()
        except Exception:
            continue
        for block in txt.split("\n## "):
            if block.strip() and len(block.strip()) > 100:
                chunks.append((block.strip(), Path(path).stem))
    if not chunks:
        return "", ""
    return random.choice(chunks)


# ─── LLM reformateo ──────────────────────────────────────────────────────────
def _llm_reformat_for_channel(raw_text: str, source: str) -> str:
    """Usa OpenRouter para convertir chunk KB en post educativo para el canal."""
    if not OPENROUTER_KEY:
        # fallback: usar texto directo
        return f"📚 <b>Dato del día</b>\n\n{raw_text[:800]}\n\n{HASHTAGS}"

    system = (
        "Eres el editor del canal educativo de Tu Bandera A.C., centro de rehabilitación en México. "
        "Tu tarea: reformatear el fragmento de conocimiento dado en un post breve (máx 280 palabras) "
        "para Telegram. Usa emojis con moderación, lenguaje cálido y sin juicios. "
        "El post debe terminar con una frase de esperanza. Responde SOLO el texto del post, sin comentarios."
    )
    user = f"Fragmento de conocimiento (fuente: {source}):\n\n{raw_text[:1000]}"

    payload = {
        "model": "deepseek/deepseek-v4-flash-0731",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
        "max_tokens": 400,
        "temperature": 0.7,
    }
    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type":  "application/json",
            },
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode())
            content = data["choices"][0]["message"]["content"].strip()
            # Agregar hashtags si no están
            if "#" not in content:
                content += f"\n\n{HASHTAGS}"
            return content
    except Exception as e:
        print(f"[canal] LLM error: {e}", flush=True)
        return f"📚 <b>Dato del día</b>\n\n{raw_text[:600]}\n\n{HASHTAGS}"


# ─── Posts ───────────────────────────────────────────────────────────────────
def post_daily_tip() -> bool:
    """Publica tip educativo diario (chunk KB + LLM reformateo)."""
    chunk, src = _load_random_chunk()
    if not chunk:
        print("[canal] ⚠ KB vacía o no encontrada", flush=True)
        return False

    post_text = _llm_reformat_for_channel(chunk, src)
    date_str = datetime.now().strftime("%d/%m/%Y")
    header = f"🕊️ <b>Tu Bandera A.C. — {date_str}</b>\n\n"
    return post_to_channel(header + post_text)


def post_community_prompt() -> bool:
    """Mensaje de apertura comunitaria para el grupo (20:00 hrs)."""
    prompts = [
        "🌙 Buenas noches a toda la familia Tu Bandera.\n\n¿Cómo estuvo tu día hoy? Recuerda que no estás solo/a en este camino. Estamos aquí. 💙\n\n" + HASHTAGS,
        "🌟 El primer paso es el más valiente. Si tú o alguien que quieres necesita orientación hoy, escríbenos al @TBasistente_bot — sin juicios, sin costo inicial.\n\n" + HASHTAGS,
        "💪 Hoy es un buen día para recordar: la recuperación no es una línea recta. Cada día presente cuenta.\n\nSi necesitas apoyo, Tu Bandera A.C. está contigo. 🕊️\n\n" + HASHTAGS,
        "📖 'Un día a la vez' — el principio más poderoso de los 12 pasos.\n\n¿Qué estás haciendo hoy por tu recuperación o la de tu familia? Cuéntanos. 💬\n\n" + HASHTAGS,
        "🏠 Tu Bandera A.C. — tratamiento integral con enfoque psicológico, psiquiátrico y espiritual.\nServicio de traslados 24/7. Diagnóstico gratuito inicial.\n\n📲 @TBasistente_bot\n\n" + HASHTAGS,
    ]
    # Rotación por día de la semana para no repetir
    idx = datetime.now().weekday() % len(prompts)
    return post_to_channel(prompts[idx])


# ─── CLI ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Canal sender Tu Bandera A.C.")
    parser.add_argument("--daily",     action="store_true", help="Publicar tip educativo diario")
    parser.add_argument("--community", action="store_true", help="Publicar prompt comunitario nocturno")
    parser.add_argument("--get-id",    action="store_true", help="Obtener chat_id del canal/grupo")
    parser.add_argument("--test",      type=str, default="",  help="Publicar mensaje de prueba")
    args = parser.parse_args()

    if not TOKEN:
        print("❌ TELEGRAM_TUBANDERA_TOKEN no configurado", flush=True)
        sys.exit(1)

    if args.get_id:
        get_channel_id()
    elif args.daily:
        post_daily_tip()
    elif args.community:
        post_community_prompt()
    elif args.test:
        post_to_channel(args.test)
    else:
        parser.print_help()
