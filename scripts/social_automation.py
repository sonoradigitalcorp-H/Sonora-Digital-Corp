#!/usr/bin/env python3
"""
Social Media Automation — Sonora Digital Corp
Uses Playwright with Chrome profile (sonoradigitalcorp@gmail.com)
Manages: Facebook, Instagram, WhatsApp Web
"""
import asyncio, json, os, sys
from datetime import datetime
from playwright.async_api import async_playwright

HOME = os.path.expanduser("~")
CHROME_PATH = "/opt/google/chrome/chrome"
USER_DATA_DIR = os.path.join(HOME, ".config/google-chrome")
LOG_DIR = os.path.join(HOME, "jarvis/logs/social")
SCREENSHOT_DIR = os.path.join(HOME, "jarvis/screenshots/social")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

SOCIAL_URLS = {
    "facebook": "https://www.facebook.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "meta_business": "https://business.facebook.com",
}

async def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, f"{datetime.now():%Y%m%d}.log"), "a") as f:
        f.write(line + "\n")

async def take_screenshot(page, name):
    path = os.path.join(SCREENSHOT_DIR, f"{datetime.now():%H%M%S}-{name}.png")
    await page.screenshot(path=path, full_page=False)
    await log(f"📸 Screenshot: {name}")

async def check_notifications(page, platform):
    """Check and respond to notifications on a platform."""
    await log(f"🔔 Checking {platform} notifications...")
    try:
        # Try notification indicators
        notif_selectors = [
            'div[aria-label*="notification"]',
            'span:has-text("notification")',
            '[data-pagelet*="notifications"]',
            'a[href*="notifications"]',
            'div[role="dialog"]',
        ]
        for sel in notif_selectors:
            el = await page.query_selector(sel)
            if el:
                text = await el.inner_text()
                await log(f"   Notification found: {text[:100]}")
                await take_screenshot(page, f"{platform}-notif")
                # Try to click and respond
                await el.click()
                await asyncio.sleep(2)
                await take_screenshot(page, f"{platform}-notif-open")
                break
    except Exception as e:
        await log(f"   Error checking {platform}: {e}")

async def main():
    await log("=" * 60)
    await log("🚀 SOCIAL AUTOMATION STARTED")
    await log("=" * 60)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            executable_path=CHROME_PATH,
            headless=False,  # Needed for WhatsApp Web QR and Meta sessions
            args=["--no-sandbox", "--disable-dev-shm-usage"],
            viewport={"width": 1366, "height": 768},
        )
        page = context.pages[0] if context.pages else await context.new_page()

        # Cycle through social platforms
        for platform, url in SOCIAL_URLS.items():
            await log(f"\n📱 Opening {platform}...")
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                await asyncio.sleep(3)
                await take_screenshot(page, platform)
                current_url = page.url
                await log(f"   URL: {current_url}")

                if "login" in current_url or "checkpoint" in current_url:
                    await log(f"   ⚠️ {platform} requires login")
                    continue

                await check_notifications(page, platform)
                await asyncio.sleep(2)
            except Exception as e:
                await log(f"   ❌ Error with {platform}: {e}")

        await context.close()

    await log("\n✅ Social automation cycle complete")

if __name__ == "__main__":
    asyncio.run(main())
