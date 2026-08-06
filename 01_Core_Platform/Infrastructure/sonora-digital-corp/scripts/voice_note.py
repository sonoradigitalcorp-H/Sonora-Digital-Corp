#!/usr/bin/env python3
"""Pipeline correcto de nota de voz WhatsApp.

TTS → MP3 (edge-tts) → WAV (soundfile, conserva sample rate)
→ resample a 16kHz mono (sox) → OGG/Opus (soundfile) → wacli send voice

NOTA: NO usar ffmpeg del sistema (roto por libva). NO declarar sample
rate distinto al real sin resamplear (produce audio lento/distorsionado).
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WACLI = os.environ.get("WACLI_PATH") or os.path.expanduser("~/.local/bin/wacli")
STORE = os.environ.get("WACLI_STORE") or os.path.expanduser("~/.wacli/accounts/personal")
SOX = os.environ.get("SOX_PATH") or "/usr/bin/sox"


def _run(cmd, timeout=120):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def tts_to_mp3(text: str, out_mp3: str) -> None:
    r = _run(["edge-tts", "--voice", "es-MX-DaliaNeural", "--text", text, "--write-media", out_mp3])
    if r.returncode != 0:
        raise RuntimeError(f"edge-tts failed: {r.stderr}")


def mp3_to_ogg(mp3_path: str, ogg_path: str) -> None:
    import soundfile as sf

    data, sr = sf.read(mp3_path)
    tmp_wav = mp3_path.replace(".mp3", "_raw.wav")
    sf.write(tmp_wav, data, sr)
    # Resample real a 16kHz mono (mantiene velocidad/dureación correctas)
    wav16 = mp3_path.replace(".mp3", "_16k.wav")
    r = _run([SOX, tmp_wav, "-r", "16000", "-c", "1", wav16])
    if r.returncode != 0:
        raise RuntimeError(f"sox resample failed: {r.stderr}")
    data16, _ = sf.read(wav16)
    sf.write(ogg_path, data16, 16000, format="OGG", subtype="OPUS")
    os.unlink(tmp_wav)
    os.unlink(wav16)


def send_voice(to: str, ogg_path: str) -> dict:
    to = to if "@s.whatsapp.net" in to else f"{to}@s.whatsapp.net"
    cmd = [WACLI, "send", "voice", "--file", ogg_path,
           "--to", to, "--post-send-wait", "5s",
           "--store", STORE, "--json"]
    r = _run(cmd)
    out = r.stdout.strip()
    return json.loads(out) if out else {"success": False, "error": r.stderr.strip() or "no output"}


def make_voice_note(text: str, to: str) -> dict:
    """Genera y envía la nota de voz completa."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False, mode="wb") as tmp:
        mp3_path = tmp.name
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    try:
        tts_to_mp3(text, mp3_path)
        mp3_to_ogg(mp3_path, ogg_path)
        return send_voice(to, ogg_path)
    finally:
        for p in (mp3_path, ogg_path):
            try:
                os.unlink(p)
            except FileNotFoundError:
                pass
