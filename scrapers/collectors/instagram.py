"""Instagram collector — Playwright browser + API fallback.

Primary: Playwright headless Chromium render + meta tag extraction
Fallback: i.instagram.com API (X-IG-App-ID header)

Events logged to events.jsonl for traceability (AI Ethics §1).
"""
CAPABILITY_ID = "browse-artist"
PROVIDER_ID = "instagram-browser"
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger("scraper.instagram")

BASE = Path(__file__).resolve().parent.parent.parent
EVENTS_PATH = BASE / "state" / "logs" / "events.jsonl"
TIMEOUT = 15


def _emit_event(event: str, payload: dict):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": event, "producer": "scraper-instagram",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    log.info("Event: %s | %s", event, json.dumps(payload)[:200])


def _browser_profile(username: str) -> dict | None:
    """Fetch profile using Playwright headless browser. Handles JS-rendered pages."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.warning("playwright not installed, skipping browser mode")
        return None

    url = f"https://www.instagram.com/{username}/"
    html = None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/125.0.0.0 Safari/537.36",
            )
            page.goto(url, timeout=15000, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            html = page.content()
            page_title = page.title()
            browser.close()
            # Login wall detected — browser returned Instagram homepage, not profile
            if page_title == "Instagram" or page.url.startswith("https://www.instagram.com/accounts/login"):
                log.warning("Instagram login wall for %s", username)
                return None
    except Exception as e:
        log.warning("Playwright error for %s: %s", username, e)
        return None

    result = {
        "source": "instagram",
        "instagram_username": username,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', html or "")
    if m:
        desc = m.group(1)
        nums = re.findall(r"([\d,.]+[KMB]?)", desc)
        if len(nums) >= 1:
            result["instagram_followers"] = nums[0]
        if len(nums) >= 2:
            result["instagram_following"] = nums[1]
        if len(nums) >= 3:
            result["instagram_posts"] = nums[2]

    m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
    if m:
        title = m.group(1)
        if "(@" in title:
            parts = title.split("(@")
            result["instagram_full_name"] = parts[0].strip()
            result["instagram_username"] = parts[1].rstrip(")").rstrip("•").strip()
        else:
            result["instagram_full_name"] = title

    m = re.search(r'<script\s+type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            ld = json.loads(m.group(1))
            result["instagram_bio"] = ld.get("description", "")
        except json.JSONDecodeError:
            pass

    # Try to find JSON hydration data
    scripts = re.findall(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.DOTALL)
    for script_text in scripts:
        try:
            data = json.loads(script_text)
            raw = json.dumps(data)
            if "biography" in raw and "edge_followed_by" in raw:
                _deep_parse_instagram_json(data, result)
                break
        except (json.JSONDecodeError, TypeError):
            continue

    followers = result.get("instagram_followers")
    if not followers or str(followers).strip() in ("", ".", "0"):
        return None
    return result


def _deep_parse_instagram_json(data: dict, result: dict):
    """Parse Instagram's internal JSON hydration blob for accurate stats."""
    try:
        raw = json.dumps(data)
        m = re.search(r'"biography"\s*:\s*"([^"]+)"', raw)
        if m and not result.get("instagram_bio"):
            result["instagram_bio"] = m.group(1)
        m = re.search(r'"edge_followed_by"\s*:\s*\{\s*"count"\s*:\s*(\d+)', raw)
        if m:
            result["instagram_followers"] = int(m.group(1))
        m = re.search(r'"edge_follow"\s*:\s*\{\s*"count"\s*:\s*(\d+)', raw)
        if m:
            result["instagram_following"] = int(m.group(1))
        m = re.search(r'"edge_owner_to_timeline_media"\s*:\s*\{\s*"count"\s*:\s*(\d+)', raw)
        if m:
            result["instagram_posts"] = int(m.group(1))
    except Exception:
        pass


def _api_profile(username: str) -> dict | None:
    """Fast-path: try Instagram internal API. Often rate-limited from datacenter IPs."""
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{username}/",
    }
    try:
        resp = httpx.get(url, headers=headers, timeout=TIMEOUT, follow_redirects=True)
        if resp.status_code != 200:
            return None
        user = resp.json().get("data", {}).get("user")
        if not user:
            return None
        return {
            "source": "instagram",
            "instagram_username": username,
            "instagram_full_name": user.get("full_name", ""),
            "instagram_followers": user.get("follower_count", 0),
            "instagram_following": user.get("following_count", 0),
            "instagram_posts": user.get("media_count", 0),
            "instagram_bio": user.get("biography", ""),
            "instagram_is_private": user.get("is_private", False),
            "instagram_is_verified": user.get("is_verified", False),
            "instagram_category": user.get("category_name", ""),
            "instagram_profile_pic": user.get("profile_pic_url_hd", ""),
            "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    except Exception as e:
        log.warning("Instagram API error for %s: %s", username, e)
        return None


def fetch_artist(username: str) -> dict[str, Any] | None:
    """Fetch Instagram profile. Tries API (fast), then browser (reliable)."""
    result = _api_profile(username)
    if result:
        _emit_event("instagram_api_success", {
            "username": username,
            "followers": result.get("instagram_followers", 0),
        })
        return result

    _emit_event("instagram_api_failed_try_browser", {"username": username})
    result = _browser_profile(username)
    if result:
        _emit_event("instagram_browser_success", {
            "username": username,
            "followers": result.get("instagram_followers", 0),
        })
        return result

    _emit_event("instagram_profile_not_found", {"username": username})
    return None


def fetch_artist_with_fallback(username: str) -> dict[str, Any]:
    """Fetch Instagram data with fallback — always returns a dict."""
    result = fetch_artist(username)
    if result:
        return result
    return {
        "source": "instagram",
        "instagram_username": username,
        "instagram_full_name": "",
        "instagram_followers": 0,
        "instagram_following": 0,
        "instagram_posts": 0,
        "instagram_bio": "",
        "instagram_is_private": False,
        "instagram_is_verified": False,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
