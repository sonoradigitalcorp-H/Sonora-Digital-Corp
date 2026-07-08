"""publish-track handler — HAS-005
Publish tracks to distribution platforms (simulated).
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
PUBLISH_DIR = REPO / "state" / "publishing"


def _ensure_dir():
    PUBLISH_DIR.mkdir(parents=True, exist_ok=True)


PLATFORMS = ["spotify", "apple_music", "youtube_music", "tiktok", "deezer"]


async def execute(context: Any) -> dict:
    _ensure_dir()
    input_data = context if isinstance(context, dict) else {}
    track_id = input_data.get("track_id", f"track_{uuid.uuid4().hex[:8]}")
    title = input_data.get("title", "Untitled")
    artist_name = input_data.get("artist_name", "Unknown Artist")
    album = input_data.get("album", "")
    platforms = input_data.get("platforms", PLATFORMS)
    isrc = input_data.get("isrc", f"US{datetime.now(timezone.utc).strftime('%y')}{uuid.uuid4().hex[:5].upper()}")

    distribution_id = f"dist_{uuid.uuid4().hex[:8]}"
    results = []

    for platform in platforms:
        platform_result = {
            "platform": platform,
            "status": "published" if platform != "tiktok" else "pending_review",
            "url": f"https://{platform.replace('_', '.')}/track/{uuid.uuid4().hex[:12]}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        results.append(platform_result)

    publish_record = {
        "distribution_id": distribution_id,
        "track_id": track_id,
        "title": title,
        "artist": artist_name,
        "album": album,
        "isrc": isrc,
        "platforms": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
    }

    path = PUBLISH_DIR / f"{distribution_id}.json"
    path.write_text(json.dumps(publish_record, indent=2))

    return publish_record
