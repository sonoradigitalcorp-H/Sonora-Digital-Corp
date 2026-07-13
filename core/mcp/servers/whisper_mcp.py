"""Whisper MCP Server — Speech-to-Text transcription.

Transcribes audio to text with SRT subtitle generation.
"""

import json
import os
import subprocess
import tempfile

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def whisper_transcribe(audio_url: str, language: str = "es") -> str:
    if not audio_url:
        return json.dumps({"error": "audio_url is required"})
    try:
        with tempfile.TemporaryDirectory() as tmp:
            # Download audio
            audio_path = os.path.join(tmp, "input.wav")
            if audio_url.startswith("http"):
                async with httpx.AsyncClient() as client:
                    resp = await client.get(audio_url, timeout=60)
                    with open(audio_path, "wb") as f:
                        f.write(resp.content)
            else:
                return json.dumps({"error": "audio_url must be a URL"})

            try:
                import whisper
            except ImportError:
                return json.dumps({"warning": "whisper not installed, returning raw text", "text": "", "srt": ""})

            model = whisper.load_model("base")
            result = model.transcribe(audio_path, language=language)
            text = result.get("text", "").strip()
            segments = result.get("segments", [])

            srt_lines = []
            for i, seg in enumerate(segments, 1):
                start = seg["start"]
                end = seg["end"]
                srt_lines.append(str(i))
                srt_lines.append(f"{_fmt_srt_time(start)} --> {_fmt_srt_time(end)}")
                srt_lines.append(seg["text"].strip())
                srt_lines.append("")

            srt_content = "\n".join(srt_lines)

            srt_url = ""
            if SUPABASE_URL and SUPABASE_SERVICE_KEY and text:
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "text/plain",
                }
                import hashlib
                srt_path = f"content/subtitles/{hashlib.md5(text.encode()).hexdigest()[:10]}.srt"
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{SUPABASE_URL}/storage/v1/object/sdc-assets/{srt_path}",
                        content=srt_content.encode(),
                        headers=headers,
                        timeout=30,
                    )
                    if resp.status_code in (200, 201):
                        srt_url = f"{SUPABASE_URL}/storage/v1/object/public/sdc-assets/{srt_path}"

            return json.dumps({
                "text": text,
                "srt": srt_content,
                "srt_url": srt_url,
                "segments": [{"start": s["start"], "end": s["end"], "text": s["text"].strip()} for s in segments],
                "language": language,
            })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _fmt_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


async def whisper_list_models() -> str:
    return json.dumps({
        "models": [
            {"name": "base", "size": "74M", "speed": "fast", "accuracy": "good"},
            {"name": "small", "size": "244M", "speed": "medium", "accuracy": "better"},
            {"name": "medium", "size": "769M", "speed": "slow", "accuracy": "best"},
        ]
    })


MCP_TOOLS = {
    "whisper_transcribe": {
        "description": "Transcribe audio to text with SRT subtitles",
        "input_schema": {
            "type": "object",
            "properties": {
                "audio_url": {"type": "string", "description": "URL of audio file to transcribe"},
                "language": {"type": "string", "description": "Language code (default: es)", "default": "es"},
            },
            "required": ["audio_url"],
        },
        "handler": lambda args: whisper_transcribe(args["audio_url"], args.get("language", "es")),
    },
    "whisper_list_models": {
        "description": "List available Whisper models",
        "input_schema": {"type": "object", "properties": {}},
        "handler": lambda _: whisper_list_models(),
    },
}
