#!/usr/bin/env python3
"""Social Login — Import cookies from Chrome to Playwright for social media.

This script extracts cookies from Chrome's profile and injects them
into a Playwright browser context, enabling automation without
re-logging in to each platform.

Usage:
  python3 social_login.py --platform twitter
  python3 social_login.py --platform instagram
  python3 social_login.py --platform facebook
  python3 social_login.py --platform all
"""

import os
import sys
import json
import shutil
import sqlite3
import tempfile
import argparse
import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("social-login")

CHROME_DB = Path.home() / ".config/google-chrome/Default/Cookies"

PLATFORM_DOMAINS = {
    "twitter": ["twitter.com", "x.com", ".twitter.com", ".x.com"],
    "instagram": ["instagram.com", ".instagram.com"],
    "facebook": ["facebook.com", ".facebook.com", "www.facebook.com"],
    "tiktok": ["tiktok.com", ".tiktok.com"],
    "linkedin": ["linkedin.com", ".linkedin.com"],
}

# Chrome cookie columns: host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly, samesite
# Chrome stores encrypted_value with v10/v11 prefix on Linux (uses DPAPI-like)


def extract_chrome_cookies(domains: List[str]) -> List[dict]:
    """Extract cookies from Chrome for specified domains."""
    if not CHROME_DB.exists():
        logger.error(f"Chrome DB not found: {CHROME_DB}")
        return []
    
    # Copy to temp to avoid lock issues
    tmp = tempfile.mktemp(suffix=".db")
    shutil.copy2(str(CHROME_DB), tmp)
    
    cookies = []
    try:
        conn = sqlite3.connect(tmp)
        
        for domain in domains:
            rows = conn.execute(
                "SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, samesite "
                "FROM cookies WHERE host_key LIKE ? ORDER BY name",
                (f"%{domain}%",)
            ).fetchall()
            
            for row in rows:
                name, value, host, path, expires, secure, httponly, samesite = row
                
                # Chrome timestamps are microseconds since 1601-01-01
                if expires > 0:
                    import time
                    expires_ts = (expires / 1000000) - 11644473600
                else:
                    expires_ts = -1
                
                cookie = {
                    "name": name,
                    "value": value,
                    "domain": host,
                    "path": path or "/",
                    "expires": expires_ts,
                    "secure": bool(secure),
                    "httpOnly": bool(httponly),
                }
                
                # Map samesite
                samesite_map = {0: "None", 1: "Lax", 2: "Strict", -1: "None"}
                cookie["sameSite"] = samesite_map.get(samesite, "Lax")
                
                cookies.append(cookie)
        
        conn.close()
    except Exception as e:
        logger.error(f"Cookie extraction error: {e}")
    finally:
        os.unlink(tmp)
    
    return cookies


async def inject_cookies_to_playwright(platform: str, cookies: List[dict]) -> bool:
    """Inject cookies into Playwright browser context."""
    from playwright.async_api import async_playwright
    
    pw = await async_playwright().start()
    
    browser = await pw.chromium.launch(
        headless=True,
        args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
    )
    
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Add cookies
    try:
        await context.add_cookies(cookies)
        logger.info(f"Injected {len(cookies)} cookies for {platform}")
    except Exception as e:
        logger.error(f"Cookie injection error: {e}")
        await browser.close()
        await pw.stop()
        return False
    
    # Save session state
    storage = await context.storage_state()
    session_file = Path(__file__).parent.parent / "ops" / "state" / f"{platform}_session.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json.dumps(storage, indent=2))
    
    logger.info(f"Session saved to {session_file}")
    
    # Verify by visiting the platform
    page = await context.new_page()
    platform_urls = {
        "twitter": "https://x.com/home",
        "instagram": "https://www.instagram.com/",
        "facebook": "https://www.facebook.com/",
    }
    
    try:
        await page.goto(platform_urls.get(platform, "https://google.com"), wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(3000)
        
        title = await page.title()
        url = page.url
        logger.info(f"Verification: title='{title}', url='{url}'")
        
        # Check if logged in
        logged_in = await _check_login_status(page, platform)
        if logged_in:
            logger.info(f"✅ Login verified for {platform}")
        else:
            logger.warning(f"⚠️ Login NOT verified for {platform} — may need manual login")
    except Exception as e:
        logger.warning(f"Verification failed: {e}")
    
    await browser.close()
    await pw.stop()
    return True


async def _check_login_status(page, platform: str) -> bool:
    """Check if user is logged in to a platform."""
    try:
        if platform == "twitter":
            # Check for compose tweet button or home timeline
            return await page.locator('[data-testid="SideNav_NewTweet_Button"]').count() > 0 or \
                   await page.locator('[data-testid="primaryColumn"]').count() > 0
        elif platform == "instagram":
            # Check for new post button or feed
            return await page.locator('svg[aria-label="New post"]').count() > 0 or \
                   await page.locator('article').count() > 0
        elif platform == "facebook":
            # Check for create post or feed
            return await page.locator('div[role="feed"]').count() > 0 or \
                   await page.locator('div[aria-label="Create a post"]').count() > 0
    except Exception:
        pass
    return False


def main():
    parser = argparse.ArgumentParser(description="Social Login - Import Chrome cookies to Playwright")
    parser.add_argument("--platform", choices=["twitter", "instagram", "facebook", "tiktok", "linkedin", "all"], required=True)
    parser.add_argument("--verify", action="store_true", help="Verify login after injection")
    args = parser.parse_args()
    
    platforms = list(PLATFORM_DOMAINS.keys()) if args.platform == "all" else [args.platform]
    
    for platform in platforms:
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing {platform.upper()}")
        logger.info(f"{'='*50}")
        
        domains = PLATFORM_DOMAINS.get(platform, [platform])
        cookies = extract_chrome_cookies(domains)
        logger.info(f"Found {len(cookies)} cookies for {platform}")
        
        if cookies:
            import asyncio
            asyncio.run(inject_cookies_to_playwright(platform, cookies))
        else:
            logger.warning(f"No cookies found for {platform} in Chrome")


if __name__ == "__main__":
    main()