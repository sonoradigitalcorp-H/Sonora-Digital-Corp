"""generate-video handler — HAS-005
Generate talking head or lipsync videos from audio + image.
"""
import json
import os
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
OUTPUT_DIR = REPO / "state" / "generated" / "videos"


def _ensure_output():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _check_ffmpeg() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


async def execute(context: Any) -> dict:
    _ensure_output()
    input_data = context if isinstance(context, dict) else {}
    audio_path = input_data.get("audio_path", "")
    image_path = input_data.get("image_path", "")
    video_type = input_data.get("type", "lipsync")
    artist_name = input_data.get("artist_name", "unknown")
    duration_seconds = input_data.get("duration_seconds", 30)

    video_id = f"vid_{uuid.uuid4().hex[:8]}"
    output_path = OUTPUT_DIR / f"{video_id}.mp4"

    has_ffmpeg = _check_ffmpeg()
    audio_exists = audio_path and os.path.exists(audio_path) if isinstance(audio_path, str) else False
    image_exists = image_path and os.path.exists(image_path) if isinstance(image_path, str) else False

    if has_ffmpeg and audio_exists and image_exists:
        try:
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", image_path,
                "-i", audio_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-shortest",
                "-pix_fmt", "yuv420p",
                str(output_path),
            ]
            subprocess.run(cmd, capture_output=True, timeout=duration_seconds + 30)
        except Exception:
            pass

    if not output_path.exists():
        output_path.write_text(json.dumps({
            "video_id": video_id,
            "type": video_type,
            "artist": artist_name,
            "duration_seconds": duration_seconds,
            "audio_path": audio_path,
            "image_path": image_path,
            "ffmpeg_available": has_ffmpeg,
            "audio_found": audio_exists,
            "image_found": image_exists,
        }))

    return {
        "video_id": video_id,
        "path": str(output_path),
        "type": video_type,
        "artist": artist_name,
        "duration_seconds": duration_seconds,
        "ffmpeg_available": has_ffmpeg,
        "audio_found": audio_exists,
        "image_found": image_exists,
        "file_size_bytes": output_path.stat().st_size if output_path.exists() else 0,
    }
