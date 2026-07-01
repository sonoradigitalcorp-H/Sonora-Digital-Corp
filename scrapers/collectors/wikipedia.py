"""Wikipedia collector — free REST API, no API key required."""
CAPABILITY_ID = "search-artist"
PROVIDER_ID = "wikipedia-api"
from datetime import datetime, timezone

import httpx

WIKIPEDIA_API = "https://en.wikipedia.org/api/rest_v1"
TIMEOUT = 15


def fetch_artist(artist_name: str) -> dict | None:
    clean_name = artist_name.replace(" ", "_")
    url = f"{WIKIPEDIA_API}/page/summary/{clean_name}"
    resp = httpx.get(url, timeout=TIMEOUT)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("type") == "disambiguation":
        return None
    extract = data.get("extract", "")
    return {
        "source": "wikipedia",
        "artist_name": data.get("title", artist_name),
        "bio": extract[:500] if extract else "",
        "wikipedia_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def fetch_artist_with_fallback(artist_name: str) -> dict:
    result = fetch_artist(artist_name)
    if result:
        return result
    return {
        "source": "wikipedia",
        "artist_name": artist_name,
        "bio": "",
        "wikipedia_url": "",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
