"""Deezer collector — public API, no API key required."""
CAPABILITY_ID = "acquire-metadata"
PROVIDER_ID = "deezer-api"
from datetime import datetime, timezone

import httpx

DEEZER_API = "https://api.deezer.com"
TIMEOUT = 15


def search_artist(artist_name: str) -> dict | None:
    url = f"{DEEZER_API}/search/artist?q={artist_name}"
    resp = httpx.get(url, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if not data.get("data"):
        return None
    return data["data"][0]


def get_artist_detail(artist_id: int) -> dict | None:
    resp = httpx.get(f"{DEEZER_API}/artist/{artist_id}", timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    return resp.json()


def fetch_top_tracks(artist_id: int, limit: int = 5) -> list:
    url = f"{DEEZER_API}/artist/{artist_id}/top"
    resp = httpx.get(url, timeout=TIMEOUT, params={"limit": limit})
    if resp.status_code != 200:
        return []
    data = resp.json()
    return [
        {"name": t.get("title", "Unknown"), "popularity_score": t.get("rank", 0)}
        for t in data.get("data", [])
    ]


def fetch_artist(artist_name: str, deezer_id: int = None) -> dict | None:
    artist_id = deezer_id
    if not artist_id:
        search_result = search_artist(artist_name)
        if not search_result:
            return None
        artist_id = search_result["id"]

    detail = get_artist_detail(artist_id)
    if not detail:
        return None

    top_tracks = fetch_top_tracks(artist_id)

    return {
        "source": "deezer",
        "artist_name": detail.get("name", artist_name),
        "deezer_id": artist_id,
        "followers": detail.get("nb_fan", 0),
        "nb_album": detail.get("nb_album", 0),
        "has_radio": detail.get("radio", False),
        "top_tracks": top_tracks,
        "genres": [],
        "url": detail.get("link", ""),
        "picture": detail.get("picture", ""),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


async def execute(provider, input_data: dict) -> dict:
    artist_name = input_data.get("artist_name", "")
    if not artist_name:
        return {"error": "artist_name required"}
    return fetch_artist(artist_name) or fetch_artist_with_fallback(artist_name)


def fetch_artist_with_fallback(artist_name: str) -> dict | None:
    result = fetch_artist(artist_name)
    if result:
        return result
    search_result = search_artist(artist_name)
    if not search_result:
        return {
            "source": "fallback",
            "artist_name": artist_name,
            "followers": 0, "nb_album": 0,
            "top_tracks": [], "genres": [], "url": "",
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    return {
        "source": "deezer",
        "artist_name": search_result.get("name", artist_name),
        "deezer_id": search_result.get("id"),
        "followers": search_result.get("nb_fan", 0),
        "nb_album": 0,
        "has_radio": False,
        "top_tracks": [],
        "genres": [],
        "url": search_result.get("link", ""),
        "picture": search_result.get("picture", ""),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
