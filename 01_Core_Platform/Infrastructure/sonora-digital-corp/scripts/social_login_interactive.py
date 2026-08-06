#!/usr/bin/env python3
"""Interactive Login — Open browser for manual login, then save session.

Run this ONCE per platform to save fresh cookies:
  python3 social_login_interactive.py --platform twitter
  python3 social_login_interactive.py --platform instagram
  python3 social_login_interactive.py --platform facebook

The browser opens visible (NOT headless), you log in manually,
then press Enter to save the session. After that, Playwright
automation uses the saved session automatically.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path

SESSION_DIR = Path(__file__).parent.parent / "ops" / "state"

PLATFORM_URLS = {
    "twitter": "https://x.com/login",
    "instagram": "https://www.instagram.com/accounts/login/",
    "facebook": "https://www.facebook.com/login/",
}


async def interactive_login(platform: str):
    """Open browser for manual login."""
    from playwright.async_api import async_playwright
    
    url = PLATFORM_URLS.get(platform)
    if not url:
        print(f"Unknown platform: {platform}")
        return
    
    print(f"\n{'='*50}")
    print(f"  INTERACTIVE LOGIN: {platform.upper()}")
    print(f"{'='*50}")
    print(f"\n  1. Browser will open to {url}")
    print(f"  2. Log in manually")
    print(f"  3. Once logged in, press Enter in this terminal")
    print(f"  4. Session will be saved for automation\n")
    
    pw = await async_playwright().start()
    
    browser = await pw.chromium.launch(
        headless=False,  # VISIBLE for manual login
        args=["--no-sandbox", "--disable-dev-shm-usage"]
    )
    
    context = await browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    page = await context.new_page()
    await page.goto(url)
    
    input(f"  Press Enter after logging in to {platform}...")
    
    # Save session
    storage = await context.storage_state()
    session_file = SESSION_DIR / f"{platform}_session.json"
    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(json.dumps(storage, indent=2))
    
    print(f"\n  ✅ Session saved to {session_file}")
    print(f"  Cookies: {len(storage.get('cookies', []))} cookies")
    print(f"  localStorage: {len(storage.get('origins', []))} origins")
    
    await browser.close()
    await pw.stop()


def main():
    parser = argparse.ArgumentParser(description="Interactive Social Login")
    parser.add_argument("--platform", choices=["twitter", "instagram", "facebook", "all"], required=True)
    args = parser.parse_args()
    
    platforms = ["twitter", "instagram", "facebook"] if args.platform == "all" else [args.platform]
    
    for p in platforms:
        asyncio.run(interactive_login(p))


if __name__ == "__main__":
    main()