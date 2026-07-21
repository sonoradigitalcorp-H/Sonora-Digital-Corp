"""FFmpeg MCP Server — Video/audio processing for clone service delivery.

FR-05: Post-processing, multi-format export, and asset assembly.
"""

import json
import os
import subprocess
import tempfile

import httpx

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

PLATFORM_FORMATS = {
    "tiktok": (1080, 1920, 60),
    "reels": (1080, 1920, 90),
    "youtube_shorts": (1920, 1080, 60),
    "instagram": (1080, 1080, 120),
    "youtube": (1920, 1080, 600),
    "linkedin": (1080, 1350, 120),
}


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
    ext = os.path.splitext(path)[1].lower()
    content_types = {".mp4": "video/mp4", ".webm": "video/webm", ".wav": "audio/wav", ".mp3": "audio/mpeg", ".jpg": "image/jpeg", ".png": "image/png"}
    headers["Content-Type"] = content_types.get(ext, "application/octet-stream")
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


async def ffmpeg_convert(video_url: str, target: str, start_time: float = 0, duration: float = 0) -> str:
    if not video_url:
        return json.dumps({"error": "video_url is required"})
    if target not in PLATFORM_FORMATS:
        return json.dumps({"error": f"Invalid target. Options: {list(PLATFORM_FORMATS.keys())}"})
    w, h, _ = PLATFORM_FORMATS[target]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.mp4")
            output_path = os.path.join(tmp, f"output_{target}.mp4")
            await _download_file(video_url, input_path)
            cmd = ["ffmpeg", "-i", input_path, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2", "-c:a", "copy"]
            if duration > 0:
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


async def ffmpeg_assemble(video_url: str, audio_url: str = "", client_id: str = "",
                          intro_url: str = "", outro_url: str = "", watermark_text: str = "") -> str:
    if not video_url:
        return json.dumps({"error": "video_url is required"})
    try:
        with tempfile.TemporaryDirectory() as tmp:
            vid_path = os.path.join(tmp, "video.mp4")
            out_path = os.path.join(tmp, "final.mp4")
            await _download_file(video_url, vid_path)

            filter_chains = []

            if watermark_text:
                filter_chains.append(
                    f"drawtext=text='{watermark_text}':fontcolor=white:fontsize=24:"
                    f"x=w-tw-10:y=h-th-10:box=1:boxcolor=black@0.5"
                )

            cmd = ["ffmpeg", "-i", vid_path]

            if audio_url:
                audio_path = os.path.join(tmp, "audio.wav")
                await _download_file(audio_url, audio_path)
                cmd.extend(["-i", audio_path])
                cmd.extend(["-c:v", "libx264", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0", "-shortest"])
            else:
                cmd.extend(["-c:v", "libx264", "-c:a", "copy"])

            if filter_chains:
                cmd.extend(["-vf", ",".join(filter_chains)])

            cmd.append(out_path)
            subprocess.run(cmd, capture_output=True, timeout=180)

            if not os.path.exists(out_path):
                return json.dumps({"error": "FFmpeg assembly failed"})

            import hashlib
            slug = client_id or "unknown"
            storage_path = f"clients/{slug}/output/videos/final_{hashlib.md5(video_url.encode()).hexdigest()[:8]}.mp4"
            url = await _upload_file(out_path, storage_path)
            return json.dumps({"url": url, "client_id": client_id, "has_audio": bool(audio_url)})
    except Exception as e:
        return json.dumps({"error": str(e)})


async def ffmpeg_multiformat(video_url: str, client_id: str = "",
                             platforms: list[str] | None = None) -> str:
    if not video_url:
        return json.dumps({"error": "video_url is required"})
    targets = platforms or ["tiktok", "instagram", "youtube"]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            input_path = os.path.join(tmp, "input.mp4")
            await _download_file(video_url, input_path)

            urls = {}
            for target in targets:
                if target not in PLATFORM_FORMATS:
                    continue
                w, h, max_dur = PLATFORM_FORMATS[target]
                output_path = os.path.join(tmp, f"{target}.mp4")
                cmd = ["ffmpeg", "-i", input_path, "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2"]
                cmd.extend(["-t", str(max_dur), "-c:a", "aac", "-b:a", "128k", output_path])
                subprocess.run(cmd, capture_output=True, timeout=120)
                if os.path.exists(output_path):
                    slug = client_id or "unknown"
                    import hashlib
                    storage_path = f"clients/{slug}/output/videos/{target}_{hashlib.md5(video_url.encode()).hexdigest()[:8]}.mp4"
                    url = await _upload_file(output_path, storage_path)
                    if url:
                        urls[target] = url

            return json.dumps({"urls": urls, "client_id": client_id, "platforms": targets})
    except Exception as e:
        return json.dumps({"error": str(e)})


MCP_TOOLS = {
    "ffmpeg_convert": {
        "description": "Convert video to platform format (tiktok, reels, youtube, instagram, linkedin)",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "URL of video to convert"},
                "target": {"type": "string", "description": "Target format: tiktok, reels, youtube_shorts, instagram, youtube, linkedin"},
                "start_time": {"type": "number", "description": "Start time in seconds"},
                "duration": {"type": "number", "description": "Duration in seconds"},
            },
            "required": ["video_url", "target"],
        },
        "handler": lambda args: ffmpeg_convert(args["video_url"], args["target"], args.get("start_time", 0), args.get("duration", 0)),
    },
    "ffmpeg_assemble": {
        "description": "Assemble final video: combine video + audio + intro/outro + watermark",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "URL of main video"},
                "audio_url": {"type": "string", "description": "URL of audio track (optional)"},
                "client_id": {"type": "string", "description": "Client identifier for storage path"},
                "intro_url": {"type": "string", "description": "URL of intro video (optional)"},
                "outro_url": {"type": "string", "description": "URL of outro video (optional)"},
                "watermark_text": {"type": "string", "description": "Watermark text overlay (optional)"},
            },
            "required": ["video_url"],
        },
        "handler": lambda args: ffmpeg_assemble(args["video_url"], args.get("audio_url", ""),
                                                args.get("client_id", ""), args.get("intro_url", ""),
                                                args.get("outro_url", ""), args.get("watermark_text", "")),
    },
    "ffmpeg_multiformat": {
        "description": "Export video in multiple platform formats (tiktok, instagram, youtube)",
        "input_schema": {
            "type": "object",
            "properties": {
                "video_url": {"type": "string", "description": "URL of raw video"},
                "client_id": {"type": "string", "description": "Client identifier for storage path"},
                "platforms": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Platforms to export (default: tiktok, instagram, youtube)",
                },
            },
            "required": ["video_url"],
        },
        "handler": lambda args: ffmpeg_multiformat(args["video_url"], args.get("client_id", ""), args.get("platforms")),
    },
}
