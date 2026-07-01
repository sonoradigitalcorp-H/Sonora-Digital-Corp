"""Bridge to open-source collectors (Deezer, Apple Music, Wikipedia) — no API keys."""
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRAPERS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "scrapers"
if str(SCRAPERS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRAPERS_DIR))

log = logging.getLogger("abe.bridge.collectors")


def _import_collectors():
    from scrapers.collectors import deezer  # noqa: I001
    from scrapers.collectors import apple_music  # noqa: I001
    from scrapers.collectors import wikipedia  # noqa: I001
    return deezer, apple_music, wikipedia


async def collect_artist(artist_name: str) -> dict:
    deezer, apple_music, wikipedia = _import_collectors()
    result = {"nombre": artist_name, "source": "collectors", "fetched_at": datetime.now(timezone.utc).isoformat()}

    dz = deezer.fetch_artist_with_fallback(artist_name)
    if dz:
        result["deezer_id"] = dz.get("deezer_id")
        result["followers"] = dz.get("followers", 0)
        result["nb_album"] = dz.get("nb_album", 0)
        result["has_radio"] = dz.get("has_radio", False)
        result["top_tracks"] = dz.get("top_tracks", [])
        result["picture"] = dz.get("picture", "")
        result["deezer_url"] = dz.get("url", "")

    am = apple_music.fetch_artist_with_fallback(artist_name)
    if am:
        result["apple_music_id"] = am.get("apple_music_id", 0)
        result["apple_music_url"] = am.get("apple_music_url", "")
        result["genres"] = am.get("genres", [])

    wp = wikipedia.fetch_artist_with_fallback(artist_name)
    if wp:
        result["bio"] = wp.get("bio", "")
        result["wikipedia_url"] = wp.get("wikipedia_url", "")

    return result


async def collect_all_artists(artists: list[dict]) -> list[dict]:
    results = []
    for artist in artists:
        name = artist.get("nombre") or artist.get("name", "")
        if not name:
            continue
        try:
            data = await collect_artist(name)
            data["artist_id"] = artist.get("artist_id") or artist.get("id", "")
            data["status"] = artist.get("status", "active")
            results.append(data)
            log.info(f"Collected: {name} — {data.get('followers', 0)} followers, {data.get('nb_album', 0)} albums")
        except Exception as e:
            log.warning(f"Collector failed for {name}: {e}")
            results.append({"nombre": name, "artist_id": artist.get("id", ""), "error": str(e)})
    return results
