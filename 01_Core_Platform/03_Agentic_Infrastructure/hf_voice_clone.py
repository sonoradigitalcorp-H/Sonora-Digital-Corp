#!/usr/bin/env python3
"""hf_voice_clone.py — Regenera voz clonada de César via F5-TTS (space HF E2-F5-TTS).

Corre 100% en la nube (Gradio API), NO usa RAM local ni XTTS.
Uso:
    python3 hf_voice_clone.py --text "Hola César, soy tu asistente"
    python3 hf_voice_clone.py --text "..." --bot aztroc --chat 5738935134
"""
import argparse, os, subprocess, sys
from pathlib import Path

from gradio_client import Client, handle_file

SPACE = "mrfakename/E2-F5-TTS"
DEFAULT_REF = "/tmp/opencode/voz/cesar_clon/cesar_voice_clon.ogg"
DEFAULT_REF_TEXT = "El la voz de Cesar. Hay que hablar espanol mexicano claro."
FFMPEG = "/home/mystic/.local/lib/python3.10/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
voice_reply_py = Path(os.path.abspath(__file__)).parent / "voice_reply.py"


def to_ogg(wav_path: str, out: str) -> str:
    subprocess.run([FFMPEG, "-y", "-i", wav_path, "-c:a", "libopus", "-b:a", "24k", out],
                   capture_output=True, text=True, timeout=60)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True)
    ap.add_argument("--ref", default=DEFAULT_REF)
    ap.add_argument("--ref-text", default=DEFAULT_REF_TEXT)
    ap.add_argument("--rm-silence", action="store_true", default=False)
    ap.add_argument("--bot", choices=["aztroc", "rye"])
    ap.add_argument("--chat")
    ap.add_argument("--out", default="/tmp/voz_cesar.ogg")
    a = ap.parse_args()

    if not os.path.exists(a.ref):
        sys.exit(f"ERROR referencia no existe: {a.ref}")

    print("[1/3] Conectando al space E2-F5-TTS en la nube...")
    client = Client(SPACE, verbose=False)

    print("[2/2] Generando voz de César (F5-TTS)...")
    result = client.predict(
        ref_audio=handle_file(a.ref),
        ref_text=a.ref_text,
        gen_text=a.text,
        remove_silence=a.rm_silence,
        api_name="/predict",
    )

    wav_path = result if isinstance(result, str) else (result or "")
    print(f"   generado: {wav_path}")

    print("[3/3] Convirtiendo y enviando...")
    ogg = to_ogg(str(wav_path), str(Path(a.out)))

    if a.bot and a.chat:
        subprocess.run([sys.executable, str(voice_reply_py), "--bot", a.bot,
                        "--chat", a.chat, "--file", ogg], check=True)
    print(f"LISTO: {ogg}")


if __name__ == "__main__":
    main()