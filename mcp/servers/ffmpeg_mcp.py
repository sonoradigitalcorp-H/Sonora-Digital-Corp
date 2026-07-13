"""FFmpeg MCP Server — Video editing and conversion.

Provides programmatic video editing: format conversion, multi-format export,
captions, and ken burns effect for slideshows.
"""

import json
import os
import subprocess
import tempfile

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")


async def _download_file(url: str, path: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, timeout=120)
        with open(path, "wb") as f:
            f.write(resp.content)


async def _upload_file(path: str, storage_path: str) -> str:
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return ""
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
    }
    with open(path, "rb") as f:
        content = f.read()
    # Determine content type
    ext = os.path.splitext(path)[1].lower()
    content_type = {"mp4": "video/mp4", "webm": "video/webm", "srt": "text/plain", "wav": "audio/wav"}.get(ext, "application/octet-stream")
    headers["Content-Type"] = content_type
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/storage/v1/object/sdc-assets/{storage_path}",
            content=content,
            headers=headers,
            timeout=120,
        )
        if resp.status_code in (200, 201):
            return f"{SUPABASE_URL}/storage/v1/object/public/sdc-assets/{storage_path}"
    return ""


async def ffmpeg_convert(video_url: str, target: str, start_time: float = 0, duration: float | None = None) -> str:
    if not video_url:
        return json.dumps({"error": "video_url is required"})
    targets = {
        "9:16": (1080, 1920),
        "16:9": (1920, 1080),
        "1:1": (1080, 1080),
        "4:5": (1080, 1350),
    }
    if target not in targets:
        return json.dumps({"error": f"Invalid target. Options: {list(targets.keys())}"})
    w, h = targets[target]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.mp4")
            output_path = os.path.join(tmp, f"output_{target}.mp4")
            await _download_file(video_url, input_path)
            cmd = ["ffmpeg", "-i", input_path, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2", "-c:a", "copy"]
            if duration:
                cmd.extend(["-t", str(duration)])
            cmd.append(output_path)
            subprocess.run(cmd, capture_output=True, timeout=120)
            if not os.path.exists(output_path):
                return json.dumps({"error": "FFmpeg conversion failed"})
            import hashlib
            storage_path = f"content/converted/{hashlib.md5(video_url.encode()).hexdigest()[:10]}_{target}.mp4"
            url = await _upload_file(output_path, storage_path)
            return json.dumps({"url": url, "format": target, "width": w, "height": h})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def ffmpeg_multiformat(video_url: str, artist_name: str = "", script_text: str = "", intro_url: str = "", outro_url: str = "", music_url: str = "") -> str:
    if not video_url:
        return json.dumps({"error": "video_url is required"})
    try:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.mp4")
            await _download_file(video_url, input_path)

            # Download optional assets
            intro_path = os.path.join(tmp, "intro.mp4")
            if intro_url:
                await _download_file(intro_url, intro_path)
            outro_path = os.path.join(tmp, "outro.mp4")
            if outro_url:
                await _download_file(outro_url, outro_path)

            formats = {
                "tiktok": (1080, 1920, 60),
                "reels": (1080, 1920, 90),
                "shorts": (1920, 1080, 60),
                "facebook": (1080, 1080, 120),
            }

            urls = {}
            for fmt_name, (w, h, max_dur) in formats.items():
                output_path = os.path.join(tmp, f"{fmt_name}.mp4")
                cmd = ["ffmpeg", "-i", input_path, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"]
                cmd.extend(["-t", str(max_dur), "-c:a", "aac", "-b:a", "128k", output_path])
                subprocess.run(cmd, capture_output=True, timeout=120)
                if os.path.exists(output_path):
                    import hashlib
                    artist_slug = artist_name.lower().replace(" ", "-") if artist_name else "unknown"
                    storage_path = f"content/{artist_slug}/{fmt_name}_{hashlib.md5(video_url.encode()).hexdigest()[:8]}.mp4"
                    url = await _upload_file(output_path, storage_path)
                    if url:
                        urls[fmt_name] = url

            return json.dumps({"urls": urls, "artist": artist_name})
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "ffmpeg_convert": {
        "description": "Convert video to target format (9:16, 16:9, 1:1, 4:5)",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "URL of video to convert"},
                "target": {"type": "string", "description": "Target format: 9:16, 16:9, 1:1, 4:5"},
                "start_time": {"type": "number", "description": "Start time in seconds"},
                "duration": {"type": "number", "description": "Duration in seconds (optional)"},
            },
            "required": ["video_url", "target"],
        },
        "handler": lambda args: ffmpeg_convert(args["video_url"], args["target"], args.get("start_time", 0), args.get("duration")),
    },
    "ffmpeg_multiformat": {
        "description": "Export video in 4 platform formats (TikTok, Reels, Shorts, Facebook)",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "URL of raw video"},
                "artist_name": {"type": "string", "description": "Artist name for folder structure"},
                "intro_url": {"type": "string", "description": "URL of intro video (optional)"},
                "outro_url": {"type": "string", "description": "URL of outro video (optional)"},
            },
            "required": ["video_url"],
        },
        "handler": lambda args: ffmpeg_multiformat(args["video_url"], args.get("artist_name", ""), intro_url=args.get("intro_url", ""), outro_url=args.get("outro_url", "")),
    },
}
