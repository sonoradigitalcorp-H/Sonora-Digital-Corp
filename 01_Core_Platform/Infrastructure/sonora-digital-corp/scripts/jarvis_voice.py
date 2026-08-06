"""JARVIS Voice Engine — TTS and text preprocessing for voice output.

Provides text cleaning, filler injection, and async TTS via edge-tts or OpenAI.
Voice config: es-MX-DaliaNeural (edge-tts) / nova (OpenAI).

Usage:
    from jarvis_voice import clean_for_speech, add_fillers, tts_speak
    cleaned = clean_for_speech("Hello 🎉 **world**!")
    filled = add_fillers(cleaned)
    path = await tts_speak(filled, "/tmp/output.mp3")
"""

import asyncio
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

# ─── Voice Config ────────────────────────────────────────────────────────────

EDGE_VOICE = "es-MX-DaliaNeural"
OPENAI_VOICE = "nova"
TTS_SPEED = 0.95
FILLER_INTERVAL = 12  # words between fillers

FILLERS = ["bueno", "a ver", "eh", "oye", "digamos"]
PAUSE_BETWEEN_SENTENCES = 0.3  # seconds (for timing calculations)

# ─── Preprocessing ───────────────────────────────────────────────────────────


def clean_for_speech(text: str) -> str:
    """Strip emojis, markdown, symbols, and normalize whitespace."""
    if not text:
        return ""

    # Remove emojis (Unicode emoji ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)

    # Remove markdown formatting
    text = re.sub(r"```[\s\S]*?```", " código ", text)  # code blocks
    text = re.sub(r"`([^`]+)`", r"\1", text)  # inline code
    text = re.sub(r"#{1,6}\s*", "", text)  # headings
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)  # bold
    text = re.sub(r"\*([^*]+)\*", r"\1", text)  # italic
    text = re.sub(r"__([^_]+)__", r"\1", text)  # bold alt
    text = re.sub(r"_([^_]+)_", r"\1", text)  # italic alt
    text = re.sub(r"~~([^~]+)~~", r"\1", text)  # strikethrough
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)  # images

    # Remove special symbols but keep basic punctuation
    text = re.sub(r"[#@$%^&*(){}<>|\\]", "", text)
    text = re.sub(r"[ \t]+", " ", text)  # collapse spaces
    text = re.sub(r"\n{3,}", "\n\n", text)  # limit newlines
    text = text.strip()

    return text


def add_fillers(text: str) -> str:
    """Insert natural filler words every FILLER_INTERVAL words."""
    if not text:
        return ""

    words = text.split()
    if len(words) <= FILLER_INTERVAL:
        return text

    result = []
    for i, word in enumerate(words):
        result.append(word)
        if (i + 1) % FILLER_INTERVAL == 0 and i < len(words) - 1:
            filler = FILLERS[(i // FILLER_INTERVAL) % len(FILLERS)]
            result.append(filler)

    return " ".join(result)


# ─── TTS Engine ──────────────────────────────────────────────────────────────


async def tts_speak(text: str, output_path: str | None = None) -> str:
    """Generate speech audio from text. Returns path to audio file.

    Tries edge-tts first, falls back to OpenAI TTS if OPENAI_API_KEY is set.
    """
    if not text:
        raise ValueError("text is empty")

    if output_path is None:
        out_dir = Path(tempfile.gettempdir()) / "jarvis-tts"
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = str(out_dir / f"jarvis-{uuid.uuid4().hex[:8]}.mp3")

    # Try edge-tts first (free, local)
    edge_bin = shutil.which("edge-tts")
    if edge_bin:
        try:
            proc = await asyncio.create_subprocess_exec(
                edge_bin,
                "--voice", EDGE_VOICE,
                "--rate", f"{int((TTS_SPEED - 1) * 100)}%",
                "--text", text[:4000],
                "--write-media", output_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=30)
            if proc.returncode == 0 and Path(output_path).exists():
                size = Path(output_path).stat().st_size
                if size > 500:
                    return output_path
        except (asyncio.TimeoutError, FileNotFoundError):
            pass

    # Fallback: OpenAI TTS if key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            import httpx

            headers = {"Authorization": f"Bearer {api_key}"}
            payload = {
                "model": "tts-1",
                "input": text[:4000],
                "voice": OPENAI_VOICE,
                "speed": TTS_SPEED,
                "response_format": "mp3",
            }
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/audio/speech",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 200:
                    Path(output_path).write_bytes(resp.content)
                    return output_path
        except Exception:
            pass

    # Last resort: write text metadata so frontend can use Web Speech API
    meta_path = output_path + ".meta.json"
    import json

    Path(meta_path).write_text(json.dumps({
        "status": "fallback_browser_tts",
        "text": text,
        "voice": "browser",
        "note": "TTS server unavailable — frontend should use SpeechSynthesis API",
    }))
    return output_path


# ─── Web Speech API Config (for frontend) ───────────────────────────────────

WEB_SPEECH_CONFIG = {
    "lang": "es-MX",
    "rate": TTS_SPEED,
    "pitch": 1.0,
    "volume": 1.0,
    "voice_name": "Google es-MX",
    "continuous": True,
    "interim_results": True,
    "alternatives": 3,
}


def get_web_speech_config() -> dict:
    """Return Web Speech API configuration for frontend integration."""
    return WEB_SPEECH_CONFIG.copy()


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import json as _json

    if len(sys.argv) < 2:
        print(_json.dumps({"error": "Usage: python3 jarvis_voice.py <text> [output.mp3]"}))
        sys.exit(1)

    raw = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    cleaned = clean_for_speech(raw)
    filled = add_fillers(cleaned)

    result = asyncio.run(tts_speak(filled, out))
    print(_json.dumps({"input": raw[:80], "output": result}))
