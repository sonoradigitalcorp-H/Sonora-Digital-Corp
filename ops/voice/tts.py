"""SDC TTS — Text to Speech via edge-tts (Dalia Neural).
On-demand: se prende, procesa, se apaga.
Usage: python3 -m ops.voice.tts "Texto a hablar" [output.wav]

Voice: es-MX-DaliaNeural (mexicana, femenina, cálida, humana)
"""
import json
import subprocess
import sys
import time
import uuid
from pathlib import Path

VOICE = "es-MX-DaliaNeural"
RATE = "-10%"
PITCH = "+8Hz"
VOLUME = "+15%"

DEFAULT_OUTPUT = Path("/tmp/sdc-tts")


def speak(text: str, output_path: str = None) -> dict:
    """Generate speech audio from text."""
    t0 = time.time()

    if output_path is None:
        DEFAULT_OUTPUT.mkdir(parents=True, exist_ok=True)
        output_path = str(DEFAULT_OUTPUT / f"tts-{uuid.uuid4().hex[:8]}.wav")

    import shutil
    edge_tts_bin = shutil.which("edge-tts") or "/home/ubuntu/.local/bin/edge-tts"
    # Try edge-tts first, fallback to espeak
    try:
        cmd = [edge_tts_bin, "--voice", VOICE, "--text", text[:1500], "--write-media", output_path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and Path(output_path).stat().st_size > 1000:
            return {
                "status": "ok", "output": output_path,
                "duration": round(time.time() - t0, 2),
                "size_bytes": Path(output_path).stat().st_size,
                "voice": VOICE,
            }
    except Exception:
        pass

    # Fallback: espeak (siempre funciona offline)
    try:
        subprocess.run(["espeak", "-v", "es-mx", "-w", output_path, text[:500]], capture_output=True, text=True, timeout=10)
        size = Path(output_path).stat().st_size
        if size > 100:
            return {
                "status": "ok", "output": output_path,
                "duration": round(time.time() - t0, 2),
                "size_bytes": size,
                "voice": "espeak-mx",
            }
    except Exception:
        pass

    # Last resort: return the text as-is (frontend can use browser TTS)
    return {
        "status": "fallback",
        "text": text,
        "note": "TTS no disponible. Usa el síntesis del navegador.",
        "duration": round(time.time() - t0, 2),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: python3 -m ops.voice.tts <text> [output.wav]"}))
        sys.exit(1)

    text = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None
    result = speak(text, output)
    print(json.dumps(result, indent=2))
