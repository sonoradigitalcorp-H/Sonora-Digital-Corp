#!/usr/bin/env python3
"""
Opens social media tabs in Chrome and keeps them alive.
Run in background: python3 open_tabs.py &
"""
import asyncio, logging, sys
sys.path.insert(0, '/home/mystic/sonora-digital-corp/sonora-enterprise-os/digital_twins/business/content-pipeline')
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("tabs")

URLS = [
    "https://web.facebook.com/profile.php?id=61573262032923&locale=es_LA",
    "https://www.instagram.com/sonoradigitalcorp/",
    "https://studio.youtube.com/",
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        pages = []
        for url in URLS:
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded")
            pages.append(page)
            log.info(f"Opened: {url[:50]}")
        log.info("All tabs open. Keeping alive...")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
