"""analyze-artist capability — actual logic (HAS-005)
Analyzes artist performance, trends, and opportunities.
"""
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent.parent


async def run(artist_id: str) -> dict:
    data = _load_data()
    artist = data.get("artists", {}).get(artist_id)
    if not artist:
        return {"status": "error", "error": f"artist {artist_id} not found"}
    analysis = {
        "artist_id": artist_id,
        "artist_name": artist.get("nombre", "Unknown"),
        "total_streams": artist.get("streams", 0),
        "total_revenue": artist.get("revenue", 0),
        "followers": artist.get("followers", 0),
        "momentum_score": _calc_momentum(artist),
        "platforms": _detect_platforms(artist),
        "trend": _calc_trend(artist),
        "opportunities": _find_opportunities(artist),
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"status": "success", "analysis": analysis}


def _load_data() -> dict:
    data_file = REPO / "data" / "abe-music.json"
    if data_file.exists():
        return json.loads(data_file.read_text())
    return {"artists": {}}


def _calc_momentum(artist: dict) -> int:
    streams = artist.get("streams", 0)
    followers = artist.get("followers", 0)
    revenue = artist.get("revenue", 0)
    score = 0
    if streams > 100_000_000:
        score += 40
    elif streams > 10_000_000:
        score += 30
    elif streams > 1_000_000:
        score += 20
    elif streams > 100_000:
        score += 10
    if followers > 100_000:
        score += 20
    elif followers > 10_000:
        score += 10
    if revenue > 100_000:
        score += 40
    elif revenue > 10_000:
        score += 20
    return min(100, score)


def _detect_platforms(artist: dict) -> list[str]:
    platforms = []
    if artist.get("spotify_monthly_listeners"):
        platforms.append("spotify")
    if artist.get("deezer_id"):
        platforms.append("deezer")
    if artist.get("youtube_channel_name"):
        platforms.append("youtube")
    if artist.get("instagram_followers"):
        platforms.append("instagram")
    if artist.get("tiktok_followers"):
        platforms.append("tiktok")
    if artist.get("apple_music_id"):
        platforms.append("apple_music")
    return platforms


def _calc_trend(artist: dict) -> str:
    streams = artist.get("streams", 0)
    revenue = artist.get("revenue", 0)
    if streams > 50_000_000 and revenue > 100_000:
        return "growing"
    if streams > 10_000_000:
        return "stable"
    return "emerging"


def _find_opportunities(artist: dict) -> list[str]:
    opportunities = []
    if not artist.get("youtube_channel_name"):
        opportunities.append("expand to YouTube")
    if not artist.get("instagram_followers"):
        opportunities.append("build Instagram presence")
    if not artist.get("tiktok_followers"):
        opportunities.append("create TikTok content")
    if artist.get("streams", 0) > 10_000_000 and artist.get("revenue", 0) < 50_000:
        opportunities.append("improve revenue per stream")
    return opportunities
