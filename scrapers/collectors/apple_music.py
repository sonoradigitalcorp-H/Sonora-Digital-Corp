"""Apple Music collector — free iTunes Search API, no API key required."""
CAPABILITY_ID = "acquire-metadata"
PROVIDER_ID = "apple-music-api"
from datetime import datetime, timezone

import httpx

ITUNES_API = "https://itunes.apple.com"
TIMEOUT = 15


def search_artist(artist_name: str) -> dict | None:
    url = f"{ITUNES_API}/search"
    params = {"term": artist_name, "entity": "musicArtist", "limit": 1}
    resp = httpx.get(url, timeout=TIMEOUT, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None
    return results[0]


def lookup_artist(artist_id: int) -> dict | None:
    url = f"{ITUNES_API}/lookup"
    params = {"id": artist_id, "entity": "musicArtist"}
    resp = httpx.get(url, timeout=TIMEOUT, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    results = data.get("results", [])
    if not results:
        return None
    return results[0]


def fetch_artist(artist_name: str, artist_id: int = None) -> dict | None:
    if artist_id:
        result = lookup_artist(artist_id)
    else:
        result = search_artist(artist_name)

    if not result:
        return None

    genres = []
    if result.get("primaryGenreName"):
        genres.append(result["primaryGenreName"])

    return {
        "source": "apple_music",
        "artist_name": result.get("artistName", artist_name),
        "apple_music_id": result.get("artistId", 0),
        "apple_music_url": result.get("artistLinkUrl", ""),
        "genres": genres,
        "url": result.get("artistLinkUrl", ""),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


async def execute(provider, input_data: dict) -> dict:
    artist_name = input_data.get("artist_name", "")
    if not artist_name:
        return {"error": "artist_name required"}
    return search_artist(artist_name) or {}


def fetch_artist_with_fallback(artist_name: str) -> dict:
    result = fetch_artist(artist_name)
    if result:
        return result
    return {
        "source": "apple_music",
        "artist_name": artist_name,
        "apple_music_id": 0,
        "apple_music_url": "",
        "genres": [],
        "url": "",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
