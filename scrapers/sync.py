"""Sync orchestrator — collect, validate, backup, merge, write, emit.
Uses Decision Engine for provider selection."""
import asyncio
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from planner import NoProviderAvailableError, emit_sync_completed, emit_sync_started, execute_capability, load_registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sync")

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
BACKUP_DIR = BASE / "state" / "backups" / "abe-music"
DATA_FILE = DATA_DIR / "abe-music.json"
MEMORY_EVENTS_FILE = BASE / "memory" / "learning" / "events.jsonl"
PIPELINE_EVENTS_FILE = BASE / "state" / "logs" / "events.jsonl"
BRIDGE_STATE_FILE = BASE / "state" / "lead-bridge.json"


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {"artists": {}, "releases": {}}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data: dict):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def backup_data():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if DATA_FILE.exists():
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(DATA_FILE, BACKUP_DIR / f"abe-music_{ts}.json")


def _merge(result: dict, collector_result: dict | None):
    if not collector_result:
        return
    skip_keys = {"source", "artist_name", "fetched_at", "spotify_id", "instagram_username"}
    for k, v in collector_result.items():
        if v and k not in skip_keys:
            result[k] = v


async def collect_artist_metrics(artist: dict) -> dict | None:
    name = artist.get("nombre", "")
    if not name:
        return None

    result = None
    try:
        cap_result = await execute_capability(
            "acquire-metadata",
            {"artist_name": name},
            fallback=True,
        )
        if cap_result and cap_result.success and cap_result.data:
            data = cap_result.data.get("data") or cap_result.data
            if isinstance(data, dict):
                result = data
    except NoProviderAvailableError:
        logger.warning("No providers available for acquire-metadata")
        return None

    if not result:
        return None

    # Search enrichment via search-artist capability
    try:
        search_result = await execute_capability(
            "search-artist",
            {"artist_name": name, "limit": 3},
            fallback=True,
        )
        if search_result and search_result.success and search_result.data:
            search_data = search_result.data.get("data") or search_result.data
            if isinstance(search_data, dict):
                _merge(result, search_data)
    except NoProviderAvailableError:
        logger.warning("No providers available for search-artist")

    # Browser enrichment via browse-artist capability
    insta_user = artist.get("instagram", "").lstrip("@")
    if insta_user:
        try:
            browser_result = await execute_capability(
                "browse-artist",
                {"platform": "instagram", "username": insta_user},
                fallback=True,
            )
            if browser_result and browser_result.success and browser_result.data:
                _merge(result, browser_result.data.get("data") or browser_result.data)
        except NoProviderAvailableError:
            pass

    tiktok_user = artist.get("tiktok", "").lstrip("@")
    if tiktok_user:
        try:
            browser_result = await execute_capability(
                "browse-artist",
                {"platform": "tiktok", "username": tiktok_user},
                fallback=True,
            )
            if browser_result and browser_result.success and browser_result.data:
                _merge(result, browser_result.data.get("data") or browser_result.data)
        except NoProviderAvailableError:
            pass

    spotify_url = artist.get("spotify_url", "")
    if spotify_url:
        try:
            import re
            m = re.search(r'artist/(\w+)', spotify_url)
            if m:
                sp_result = await execute_capability(
                    "acquire-metadata",
                    {"artist_name": name, "platform": "spotify"},
                )
                if sp_result and sp_result.success and sp_result.data:
                    _merge(result, sp_result.data.get("data") or sp_result.data)
        except NoProviderAvailableError:
            pass

    return result


def emit_event(event: dict, write_pipeline: bool = False):
    event["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    MEMORY_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MEMORY_EVENTS_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")

    if write_pipeline:
        PIPELINE_EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        pipeline_entry = {
            "event": event.get("type"),
            "timestamp": event["timestamp"],
            "payload": {k: v for k, v in event.items() if k != "type"},
        }
        with open(PIPELINE_EVENTS_FILE, "a") as f:
            f.write(json.dumps(pipeline_entry) + "\n")

    logger.info(f"Event emitted: {event.get('type')}")


async def sync_artist_async(artist_id: str) -> dict:
    data = load_data()
    if artist_id not in data.get("artists", {}):
        return {"updated": False, "error": "artist_not_found"}

    artist = data["artists"][artist_id]
    metrics = await collect_artist_metrics(artist)
    if not metrics:
        return {"updated": False, "error": "collector_failed"}

    old_followers = artist.get("followers", 0)
    old_nb_album = artist.get("nb_album", 0)

    new_followers = metrics.get("followers", old_followers)
    new_nb_album = metrics.get("nb_album", artist.get("nb_album", 0))

    artist["followers"] = new_followers
    artist["nb_album"] = new_nb_album
    artist["deezer_id"] = metrics.get("deezer_id", artist.get("deezer_id"))
    artist["has_radio"] = metrics.get("has_radio", artist.get("has_radio", False))
    artist["top_tracks"] = metrics.get("top_tracks", artist.get("top_tracks", []))
    artist["deezer_url"] = metrics.get("url", artist.get("deezer_url", ""))
    artist["picture"] = metrics.get("picture", artist.get("picture", ""))
    artist["apple_music_id"] = metrics.get("apple_music_id", artist.get("apple_music_id", 0))
    artist["apple_music_url"] = metrics.get("apple_music_url", artist.get("apple_music_url", ""))
    artist["bio"] = metrics.get("bio", artist.get("bio", ""))
    artist["wikipedia_url"] = metrics.get("wikipedia_url", artist.get("wikipedia_url", ""))
    artist["last_sync"] = metrics.get("fetched_at", "")

    for field in ["youtube_channel_name", "youtube_subscribers", "youtube_total_views",
                   "youtube_total_views_search", "youtube_video_count",
                   "instagram_followers", "instagram_following",
                   "instagram_posts", "instagram_bio", "tiktok_followers", "tiktok_following",
                   "tiktok_likes", "tiktok_videos", "tiktok_verified",
                   "spotify_monthly_listeners", "spotify_followers", "spotify_genres",
                   "spotify_top_tracks", "spotify_image"]:
        new_val = metrics.get(field, None)
        if new_val is not None and new_val != "":
            artist[field] = new_val

    delta = {"followers": new_followers - old_followers, "nb_album": new_nb_album - old_nb_album}
    save_data(data)

    updated = delta["followers"] != 0 or delta["nb_album"] != 0
    return {"updated": updated, "delta": delta}


LEAD_THRESHOLD_STREAMS = 1000000
LEAD_THRESHOLD_FOLLOWERS = 10000

NICHE_MAP = {
    "Regional Mexicano": "musica",
    "Pop Latino": "musica",
    "Reggaeton": "musica",
    "Corrido": "musica",
    "Latin": "musica",
}


def _read_bridge_state() -> set:
    try:
        if BRIDGE_STATE_FILE.exists():
            return set(json.loads(BRIDGE_STATE_FILE.read_text()))
    except (json.JSONDecodeError, OSError):
        pass
    return set()


def _save_bridge_state(processed: set):
    BRIDGE_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_STATE_FILE.write_text(json.dumps(list(processed)))


def bridge_lead_to_pipeline(artist: dict):
    name = artist.get("nombre", "")
    if not name:
        return

    processed = _read_bridge_state()
    if name in processed:
        logger.info(f"Skipping duplicate lead bridge for {name}")
        return

    try:
        import sys
        sys.path.insert(0, str(BASE / "apps" / "jarvis" / "src"))
        from src.core.sales_pipeline import LeadSource, SalesPipeline

        genre = artist.get("genero", "")
        niche = NICHE_MAP.get(genre, "musica")
        streams = artist.get("streams", 0)
        followers = artist.get("followers", 0)
        notes = f"Artist: {name} | Streams: {streams:,} | Followers: {followers:,} | Genre: {genre}"

        pipeline = SalesPipeline()
        lead = pipeline.capture_lead(
            name=name,
            email=artist.get("email", ""),
            phone=artist.get("telefono", ""),
            source=LeadSource.DATA_SYNC.value,
            niche=niche,
            notes=notes,
        )
        processed.add(name)
        _save_bridge_state(processed)
        logger.info(f"Lead bridged to sales pipeline: {lead.id} ({name})")

    except Exception as e:
        logger.warning(f"Could not bridge lead to pipeline (expected if Neo4j is offline): {e}")


async def _async_sync_cycle():
    logger.info("Starting sync cycle")
    backup_data()

    load_registry()

    data = load_data()
    artist_ids = list(data.get("artists", {}).keys())
    emit_sync_started(len(artist_ids), ["acquire-metadata", "search-artist", "browse-artist"])

    artists_synced = []
    for artist_id in artist_ids:
        result = await sync_artist_async(artist_id)
        artists_synced.append({
            "artist_id": artist_id,
            "updated": result.get("updated"),
            "delta": result.get("delta", {}),
        })

    emit_event({
        "type": "data_sync_completed",
        "artists_synced": artists_synced,
        "total_artists": len(artists_synced),
    }, write_pipeline=True)

    for result in artists_synced:
        artist = data["artists"].get(result["artist_id"], {})
        streams = artist.get("streams", 0)
        followers = artist.get("followers", 0)
        if streams >= LEAD_THRESHOLD_STREAMS or followers >= LEAD_THRESHOLD_FOLLOWERS:
            lead_event = {
                "type": "lead_generated_from_data",
                "artist_id": result["artist_id"],
                "artist_name": artist.get("nombre", "Unknown"),
                "streams": streams,
                "followers": followers,
                "reason": "high_value_artist_detected",
            }
            emit_event(lead_event, write_pipeline=True)
            bridge_lead_to_pipeline(artist)
            logger.info(f"Lead generated: {artist.get('nombre')} ({streams} streams)")

    emit_sync_completed(len(artists_synced), 0)
    logger.info(f"Sync cycle completed. {len(artists_synced)} artists synced.")
    return artists_synced


def run_sync_cycle():
    """Synchronous wrapper for cron compatibility."""
    return asyncio.run(_async_sync_cycle())


if __name__ == "__main__":
    run_sync_cycle()
