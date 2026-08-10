#!/usr/bin/env python3
"""voice_reply.py — Envía notas de voz a Telegram o WhatsApp.

Pipeline (SIN XTTS, SIN procesos pesados):
    texto → edge-tts → MP3 → imageio ffmpeg → OGG (OPUS 24kbps) → API

Voces por defecto:
    Telegram (aztroc/rye): es-MX-DaliaNeural (femenino, amable, natural)
    WhatsApp (--whatsapp): es-MX-JorgeNeural (masculino, serio, pausado)

Uso:
    # Telegram (Dalia)
    python3 voice_reply.py --bot aztroc --chat 5738935134 --text "Hola"
    # WhatsApp (Jorge)
    python3 voice_reply.py --bot aztroc --chat 5216623538272 --text "Hola" --whatsapp
    # Archivo externo
    python3 voice_reply.py --bot aztroc --chat 5738935134 --file /path/audio.ogg
    # Custom style
    python3 voice_reply.py --bot aztroc --chat 5738935134 --text "Hola" --style "rate=-5%,pitch=+3Hz"
"""
import argparse, os, subprocess, sys, tempfile
from pathlib import Path

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except (ImportError, Exception):
    FFMPEG = "/home/mystic/.local/lib/python3.10/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

SECRETS = Path.home() / ".openclaw" / "secrets"

# bot -> token file
BOTS = {
    "aztroc": "telegram-aztroc.token",  # @Aztro_tech_bot (César)
    "rye": "telegram-rye.token",        # @RyE_production_bot (Iván)
}

# bot -> voz + ajustes por defecto (edge-tts mexicanas)
# Telegram: voz femenina suave (DaliaNeural) — Telegram TTS malea voces masculinas
# WhatsApp: voz masculina serio (JorgeNeural) — mejor en WhatsApp
DEFAULT_VOICE = {
    "aztroc": "es-MX-DaliaNeural",  # femenino suave para Telegram
    "rye": "es-MX-DaliaNeural",     # femenino mexicano (Iván)
}

DEFAULT_STYLE = {
    "aztroc": {"rate": "-10%", "pitch": "+5Hz"},  # natural, amable
    "rye": {"rate": "-10%", "pitch": "+5Hz"},
}

# WhatsApp override: hombre serio
WHATSAPP_VOICE = "es-MX-JorgeNeural"
WHATSAPP_STYLE = {"rate": "-20%", "pitch": "+8Hz"}

# Muletillas coloquiales para sonar más natural en español
FILLERS = ["Pues ", "Entonces ", "Oye ", "Mira ", "A ver "]


def add_fillers(text: str, bot: str = "aztroc") -> str:
    """Añade muletilla inicial para sonar más natural y menos robótico."""
    import random
    return random.choice(FILLERS) + text


def _token(bot: str) -> str:
    tf = SECRETS / BOTS[bot]
    if not tf.exists():
        sys.exit(f"ERROR: token no existe para {bot}: {tf}")
    return tf.read_text().strip()


def text_to_ogg(text: str, voice: str, out: Path, style: dict = None) -> str:
    """edge-tts -> MP3 -> imageio ffmpeg -> OGG opus (ligero, sin modelo local)."""
    mp3 = out.with_suffix(".mp3")
    cmd = ["edge-tts", "--voice", voice, "--text", text, "--write-media", str(mp3)]
    if style:
        if "rate" in style:
            cmd.append(f"--rate={style['rate']}")
        if "pitch" in style:
            cmd.append(f"--pitch={style['pitch']}")
    r = subprocess.run(cmd,
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        sys.exit(f"ERROR edge-tts: {r.stderr[:200]}")
    r = subprocess.run([FFMPEG, "-y", "-i", str(mp3), "-c:a", "libopus", "-b:a", "24k", str(out)],
                       capture_output=True, text=True, timeout=60)
    if not out.exists() or out.stat().st_size == 0:
        sys.exit(f"ERROR ffmpeg: {r.stderr[-300:]}")
    return str(out)


def send_telegram_voice(bot: str, chat_id: str, audio_path: str) -> bool:
    """sendVoice por Telegram bot API."""
    import requests, json
    url = f"https://api.telegram.org/bot{_token(bot)}/sendVoice"
    try:
        with open(audio_path, "rb") as f:
            r = requests.post(url, data={"chat_id": chat_id}, files={"voice": f}, timeout=60)
        d = r.json()
        if d.get("ok"):
            print(f"[OK] {bot} -> {chat_id}: {audio_path}")
            return True
        print(f"[FAIL] {d.get('description')}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def send_wacli_voice(audio_path: str, chat: str) -> bool:
    """Send voice note via wacli (WhatsApp)."""
    to = chat if "@s.whatsapp.net" in chat else f"{chat}@s.whatsapp.net"
    result = subprocess.run(
        ["/home/mystic/.local/bin/wacli", "send", "voice",
         "--store", str(Path.home() / ".config/wacli"),
         "--to", to, "--file", audio_path],
        capture_output=True, text=True, timeout=30,
    )
    return result.returncode == 0 and "Sent" in result.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bot", required=True, choices=list(BOTS))
    ap.add_argument("--chat", required=True, help="chat_id Telegram o número WhatsApp (521...)")
    ap.add_argument("--text", help="texto a decir")
    ap.add_argument("--voice", help="voz edge-tts (default por bot)")
    ap.add_argument("--style", help="estilo: rate and/or pitch (e.g. 'rate=-10%,pitch=+5Hz')")
    ap.add_argument("--no-fillers", action="store_true", help="no añadir muletillas")
    ap.add_argument("--whatsapp", action="store_true", help="usar voz de hombre serio para WhatsApp")
    ap.add_argument("--file", help="ya tienes audio (ogg)", dest="audio_file")
    ap.add_argument("--out", default="/tmp/voz_r.ogg", help="ruta ogg salida")
    a = ap.parse_args()

    voice = a.voice or (WHATSAPP_VOICE if a.whatsapp else DEFAULT_VOICE[a.bot])
    style = WHATSAPP_STYLE if a.whatsapp else DEFAULT_STYLE[a.bot]
    if a.style:
        style = {}
        for pair in a.style.split(","):
            k, v = pair.split("=", 1)
            style[k.strip()] = v.strip()
    out = Path(a.out)

    if a.audio_file:
        audio = a.audio_file
    elif a.text:
        text = a.text
        if not a.no_fillers:
            text = add_fillers(text, a.bot)
        audio = text_to_ogg(text, voice, out, style)
    else:
        ap.error("necesitas --text o --file")

    ok = send_wacli_voice(audio, a.chat) if a.whatsapp else send_telegram_voice(a.bot, a.chat, audio)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()