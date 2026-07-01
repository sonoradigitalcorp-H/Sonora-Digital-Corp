"""TikTok collector — Playwright browser scraping of public profiles.

TikTok public profiles are accessible without login. We extract:
- Follower count, following count, likes
- Bio, display name, verified status
- Recent video stats

Events logged to events.jsonl for traceability (AI Ethics §1).
"""
CAPABILITY_ID = "browse-artist"
PROVIDER_ID = "tiktok-browser"
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("scraper.tiktok")

BASE = Path(__file__).resolve().parent.parent.parent
EVENTS_PATH = BASE / "state" / "logs" / "events.jsonl"


def _emit_event(event: str, payload: dict):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": event, "producer": "scraper-tiktok",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    log.info("Event: %s | %s", event, json.dumps(payload)[:200])


def fetch_artist(username: str) -> dict[str, Any] | None:
    """Fetch TikTok profile using Playwright browser."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("playwright not installed")
        return None

    url = f"https://www.tiktok.com/@{username}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/125.0.0.0 Safari/537.36",
            )
            page.goto(url, timeout=25000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            html = page.content()
            browser.close()
    except Exception as e:
        log.warning("TikTok Playwright error for %s: %s", username, e)
        return None

    result = {
        "source": "tiktok",
        "tiktok_username": username,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    # Extract JSON-LD
    ld_match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if ld_match:
        try:
            ld = json.loads(ld_match.group(1))
            result["tiktok_display_name"] = ld.get("name", "")
            result["tiktok_bio"] = ld.get("description", "")
            if "interactionStatistic" in ld:
                for stat in ld.get("interactionStatistic", []):
                    if stat.get("interactionType") == "FollowAction":
                        result["tiktok_followers"] = stat.get("userInteractionCount", 0)
        except json.JSONDecodeError:
            pass

    # Try to extract from <script> with user data
    sig_patterns = [
        r'"followerCount"\s*:\s*(\d+)',
        r'"followingCount"\s*:\s*(\d+)',
        r'"heartCount"\s*:\s*(\d+)',
        r'"videoCount"\s*:\s*(\d+)',
        r'"nickname"\s*:\s*"([^"]+)"',
        r'"uniqueId"\s*:\s*"([^"]+)"',
        r'"bio"\s*:\s*"([^"]+)"',
        r'"verified"\s*:\s*(true|false)',
    ]
    for pattern in sig_patterns:
        m = re.search(pattern, html)
        if not m:
            continue
        key = {
            "followerCount": "tiktok_followers",
            "followingCount": "tiktok_following",
            "heartCount": "tiktok_likes",
            "videoCount": "tiktok_videos",
            "nickname": "tiktok_display_name",
            "uniqueId": "tiktok_username",
            "bio": "tiktok_bio",
            "verified": "tiktok_verified",
        }.get(pattern.split("\\")[0].strip('"').split(":")[0], None)
        if key == "tiktok_verified":
            result[key] = m.group(1) == "true"
        elif key:
            try:
                result[key] = int(m.group(1))
            except ValueError:
                result[key] = m.group(1)

    # Fallback: extract from meta tags
    og_title = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
    if og_title and "tiktok_display_name" not in result:
        result["tiktok_display_name"] = og_title.group(1)
    og_desc = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html)
    if og_desc and "tiktok_bio" not in result:
        result["tiktok_bio"] = og_desc.group(1)

    # Account not found — TikTok shows "Couldn't find this account"
    if "Couldn't find this account" in html or "couldn't find this account" in html.lower():
        log.warning("TikTok account @%s not found", username)
        return None

    has_data = any(k.startswith("tiktok_") and v not in ("", 0, None)
                   for k, v in result.items() if v)
    return result if has_data else None


def fetch_artist_with_fallback(username: str) -> dict[str, Any]:
    result = fetch_artist(username)
    if result:
        return result
    return {
        "source": "tiktok",
        "tiktok_username": username,
        "tiktok_display_name": "",
        "tiktok_followers": 0,
        "tiktok_following": 0,
        "tiktok_likes": 0,
        "tiktok_videos": 0,
        "tiktok_bio": "",
        "tiktok_verified": False,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
