"""YouTube collector — yt-dlp wrapper, no API keys required.

Logs all events to events.jsonl for traceability (AI Ethics §1).
"""
CAPABILITY_ID = "search-artist"
PROVIDER_ID = "youtube-search"
import json
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("scraper.youtube")

BASE = Path(__file__).resolve().parent.parent.parent
EVENTS_PATH = BASE / "state" / "logs" / "events.jsonl"


def _emit_event(event: str, payload: dict):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": event, "producer": "scraper-youtube",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    log.info("Event: %s | %s", event, json.dumps(payload)[:200])


def _run(*args, timeout: int = 20) -> tuple[str | None, str | None, int]:
    try:
        r = subprocess.run(
            ["yt-dlp", *args],
            capture_output=True, text=True, timeout=timeout,
        )
        return r.stdout.strip(), r.stderr.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s", -1
    except FileNotFoundError:
        return None, "yt-dlp not found. Install: pip install yt-dlp", -1


def search_artist(artist_name: str, max_results: int = 3) -> list[dict]:
    """Search YouTube for an artist. Returns video results with channel info."""
    out, err, rc = _run(
        f"ytsearch{max_results}:{artist_name}", "--skip-download",
        "--dump-json", "--flat-playlist", timeout=15,
    )
    if rc != 0 or not out:
        _emit_event("youtube_search_failed", {"artist": artist_name, "error": (err or "")[:200]})
        return []

    results = []
    for line in out.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            results.append({
                "title": d.get("title", ""),
                "url": d.get("webpage_url", ""),
                "channel": d.get("channel", ""),
                "channel_id": d.get("channel_id", ""),
                "channel_url": d.get("channel_url", ""),
                "views": d.get("view_count", 0),
                "duration": d.get("duration", 0),
            })
        except json.JSONDecodeError:
            continue

    _emit_event("youtube_search_completed", {
        "artist": artist_name,
        "results": len(results),
        "channels": list(set(r["channel"] for r in results if r["channel"])),
    })
    return results


def fetch_artist(artist_name: str) -> dict[str, Any] | None:
    """Fetch YouTube data for an artist. Returns full metadata dict or None."""
    search_results = search_artist(artist_name)
    if not search_results:
        _emit_event("youtube_artist_not_found", {"artist": artist_name})
        return None

    top_results = search_results[:5]
    total_views = sum(r.get("views", 0) for r in top_results)
    channels = list(set(r.get("channel", "") for r in top_results if r.get("channel")))
    channel_urls = list(set(r.get("channel_url", "") for r in top_results if r.get("channel_url")))

    result = {
        "source": "youtube",
        "artist_name": artist_name,
        "youtube_channel_url": channel_urls[0] if channel_urls else "",
        "youtube_channels": channels,
        "youtube_total_views_search": total_views,
        "youtube_video_count": len(top_results),
        "youtube_latest_videos": top_results[:3],
        "youtube_subscribers": 0,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    _emit_event("youtube_artist_found", {
        "artist": artist_name,
        "videos_found": len(top_results),
        "total_views": total_views,
        "channels": channels,
    })
    return result


def fetch_artist_with_fallback(artist_name: str) -> dict[str, Any]:
    """Fetch YouTube data with fallback — always returns a dict."""
    result = fetch_artist(artist_name)
    if result:
        return result
    return {
        "source": "youtube", "artist_name": artist_name,
        "youtube_channel_url": "", "youtube_channels": [],
        "youtube_total_views_search": 0, "youtube_video_count": 0,
        "youtube_latest_videos": [], "youtube_subscribers": 0,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
