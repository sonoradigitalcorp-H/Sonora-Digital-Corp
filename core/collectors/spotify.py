"""Spotify collector — Playwright browser scraping of public artist pages.

Spotify public artist pages show monthly listeners, followers, top tracks,
and related artists without requiring login.

Events logged to events.jsonl for traceability (AI Ethics §1).
"""
CAPABILITY_ID = "acquire-metadata"
PROVIDER_ID = "spotify-browser"
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("scraper.spotify")

BASE = Path(__file__).resolve().parent.parent.parent
EVENTS_PATH = BASE / "state" / "logs" / "events.jsonl"


def _emit_event(event: str, payload: dict):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": event, "producer": "scraper-spotify",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    log.info("Event: %s | %s", event, json.dumps(payload)[:200])


def _spotify_id_from_url(url: str) -> str | None:
    """Extract Spotify artist ID from URL."""
    m = re.search(r'(?:open\.spotify\.com/|spotify:)?artist[/:](\w{22})', url)
    return m.group(1) if m else None


def _browser_fetch(artist_id: str) -> dict | None:
    """Fetch Spotify artist page using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    url = f"https://open.spotify.com/artist/{artist_id}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/125.0.0.0 Safari/537.36",
            )
            page.goto(url, timeout=25000, wait_until="networkidle")
            page.wait_for_timeout(4000)
            html = page.content()
            browser.close()
    except Exception as e:
        log.warning("Spotify Playwright error for %s: %s", artist_id, e)
        return None

    result = {"source": "spotify", "spotify_id": artist_id}

    # Monthly listeners & followers
    m = re.search(r'(\d[\d,.]*[KMB]?)\s*(?:monthly\s*listener|oy dinleyici|oyente mensual)', html, re.IGNORECASE)
    if m:
        result["spotify_monthly_listeners_raw"] = m.group(1)

    m = re.search(r'(\d[\d,.]*[KMB]?)\s*(?:follower|takipçi)', html, re.IGNORECASE)
    if m:
        result["spotify_followers_raw"] = m.group(1)

    # Artist name from og:title
    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
    if m:
        result["spotify_name"] = m.group(1).replace(" - Spotify", "").strip()

    # Image
    m = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
    if m:
        result["spotify_image"] = m.group(1)

    # Genre tags
    genres = re.findall(r'<a[^>]*href="/genre/[^"]*"[^>]*>([^<]+)</a>', html)
    if genres:
        result["spotify_genres"] = [g.strip() for g in genres[:5]]

    # Top tracks from the page
    tracks = re.findall(
        r'<div[^>]*data-testid="track-row"[^>]*>.*?<span[^>]*>([^<]+)</span>',
        html, re.DOTALL
    )[:10]
    if tracks:
        result["spotify_top_tracks"] = [t.strip() for t in tracks]

    # Monthly listeners in number form
    m = re.search(r'"monthlyListeners"\s*:\s*(\d+)', html)
    if m:
        result["spotify_monthly_listeners"] = int(m.group(1))

    # Fallback: parse raw string like "1,028,288" or "1.2M"
    if "spotify_monthly_listeners_raw" in result:
        raw = result["spotify_monthly_listeners_raw"]
        multiplier = 1
        if raw.endswith("K"):
            multiplier = 1000
            raw = raw[:-1]
        elif raw.endswith("M"):
            multiplier = 1000000
            raw = raw[:-1]
        elif raw.endswith("B"):
            multiplier = 1000000000
            raw = raw[:-1]
        raw = raw.replace(",", "").replace(".", "")
        try:
            result["spotify_monthly_listeners"] = int(float(raw) * multiplier)
        except ValueError:
            pass
    if "spotify_followers_raw" in result:
        raw = result["spotify_followers_raw"]
        multiplier = 1
        if raw.endswith("K"):
            multiplier = 1000
            raw = raw[:-1]
        elif raw.endswith("M"):
            multiplier = 1000000
            raw = raw[:-1]
        elif raw.endswith("B"):
            multiplier = 1000000000
            raw = raw[:-1]
        raw = raw.replace(",", "").replace(".", "")
        try:
            result["spotify_followers"] = int(float(raw) * multiplier)
        except ValueError:
            pass

    # JSON hydration in _NEXT_DATA_
    m = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            next_data = json.loads(m.group(1))
            props = next_data.get("props", {}).get("pageProps", {})
            state = props.get("state", props)
            entity = state.get("entity", {})
            if entity.get("monthlyListeners"):
                result["spotify_monthly_listeners"] = entity["monthlyListeners"]
            if entity.get("followers"):
                result["spotify_followers"] = entity["followers"]
            if entity.get("name"):
                result["spotify_name"] = entity["name"]
            if entity.get("genres"):
                result["spotify_genres"] = entity["genres"]
            if entity.get("images") and len(entity["images"]) > 0:
                result["spotify_image"] = entity["images"][0].get("url", "")
        except (json.JSONDecodeError, AttributeError):
            pass

    return result if result.get("spotify_monthly_listeners") or result.get("spotify_monthly_listeners_raw") else None


def fetch_artist(identifier: str) -> dict[str, Any] | None:
    """Fetch Spotify artist page. Accepts Spotify ID or URL."""
    artist_id = _spotify_id_from_url(identifier) if "spotify" in identifier or ":" in identifier else identifier
    if not artist_id:
        log.warning("Invalid Spotify identifier: %s", identifier)
        return None

    result = _browser_fetch(artist_id)
    if result:
        _emit_event("spotify_scrape_success", {
            "artist_id": artist_id,
            "name": result.get("spotify_name", ""),
            "monthly_listeners": result.get("spotify_monthly_listeners", 0),
        })
        return result

    _emit_event("spotify_scrape_failed", {"artist_id": artist_id})
    return None


def fetch_artist_with_fallback(identifier: str) -> dict[str, Any]:
    result = fetch_artist(identifier)
    if result:
        return result
    return {
        "source": "spotify",
        "spotify_id": identifier,
        "spotify_name": "",
        "spotify_monthly_listeners": 0,
        "spotify_followers": 0,
        "spotify_genres": [],
        "spotify_image": "",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
