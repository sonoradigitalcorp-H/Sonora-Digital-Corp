#!/usr/bin/env python3
"""
SDC Social Manager — login + post + manage
Logs into all social platforms using stored credentials and keeps the session alive.
"""
import asyncio, json, logging, os, sys, time
from pathlib import Path
from playwright.async_api import async_playwright

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("sdc.social")

CDP = "http://127.0.0.1:9222"

def creds():
    return {
        "facebook": {"email": "sonoradigitalcorp@gmail.com", "pass": "666Gina$$$"},
        "instagram": {"email": "sonoradigitalcorp@gmail.com", "pass": "666Gina$$$"},
        "youtube": {"email": "sonoradigitalcorp@gmail.com", "pass": "666Gina$$$"},
    }

async def login_facebook(page):
    log.info("Logging into Facebook...")
    await page.goto("https://web.facebook.com/login")
    await asyncio.sleep(2)
    
    try:
        await page.fill("#email", "sonoradigitalcorp@gmail.com", timeout=5000)
    except:
        await page.fill("[name='email']", "sonoradigitalcorp@gmail.com", timeout=5000)
    await asyncio.sleep(1)
    
    try:
        await page.fill("#pass", "666Gina$$$", timeout=5000)
    except:
        await page.fill("[name='pass']", "666Gina$$$", timeout=5000)
    await asyncio.sleep(1)
    
    await page.click("[name='login']")
    await asyncio.sleep(5)
    
    if "login" in page.url.lower():
        log.warning("Facebook login may have failed")
        return False
    log.info(f"✅ Facebook logged in: {page.url[:40]}")
    return True

async def login_instagram(page):
    log.info("Logging into Instagram...")
    await page.goto("https://www.instagram.com/accounts/login/")
    await asyncio.sleep(3)
    
    for sel in ["[name='username']", "input[type='text']"]:
        try:
            await page.fill(sel, "sonoradigitalcorp@gmail.com", timeout=3000)
            break
        except:
            continue
    await asyncio.sleep(1)
    
    for sel in ["[name='password']", "input[type='password']"]:
        try:
            await page.fill(sel, "666Gina$$$", timeout=3000)
            break
        except:
            continue
    await asyncio.sleep(1)
    
    await page.click("[type='submit']")
    await asyncio.sleep(5)
    
    if "login" in page.url.lower():
        log.warning("Instagram login may have failed")
        return False
    log.info(f"✅ Instagram logged in: {page.url[:40]}")
    return True

async def login_youtube(page):
    log.info("Logging into YouTube...")
    await page.goto("https://studio.youtube.com/")
    await asyncio.sleep(4)
    
    if "signin" not in page.url.lower() and "ServiceLogin" not in page.url.lower():
        log.info("YouTube already logged in")
        return True
    
    # Try multiple Google sign-in selectors
    email_selectors = [
        "[type='email']",
        "input[type='email']",
        "[name='identifier']",
        "#identifierId",
        "input[autocomplete='username']",
    ]
    filled = False
    for sel in email_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=3000)
            if el:
                await el.fill("sonoradigitalcorp@gmail.com")
                filled = True
                log.info(f"Filled email with selector: {sel}")
                break
        except:
            continue
    
    if not filled:
        log.error("Could not find email field on Google login")
        return False
    
    await asyncio.sleep(1)
    next_selectors = ["#identifierNext", "[jsname='V67aGc']", "button:has-text('Next')", "button:has-text('Siguiente')", "[role='button']:has-text('Next')"]
    for sel in next_selectors:
        try:
            await page.click(sel, timeout=3000)
            log.info(f"Clicked Next with: {sel}")
            break
        except:
            continue
    
    await asyncio.sleep(3)
    
    # Password
    pass_selectors = [
        "[type='password']",
        "input[type='password']",
        "[name='password']",
        "#password",
        "input[autocomplete='current-password']",
    ]
    filled = False
    for sel in pass_selectors:
        try:
            el = await page.wait_for_selector(sel, timeout=3000)
            if el:
                await el.fill("666Gina$$$")
                filled = True
                log.info(f"Filled password with selector: {sel}")
                break
        except:
            continue
    
    if not filled:
        log.warning("Could not find password field, may need 2FA or different page state")
        return False
    
    pass_next = ["#passwordNext", "[jsname='V67aGc']", "button:has-text('Next')", "button:has-text('Siguiente')"]
    for sel in pass_next:
        try:
            await page.click(sel, timeout=3000)
            break
        except:
            continue
    
    await asyncio.sleep(5)
    
    if "signin" in page.url.lower() or "ServiceLogin" in page.url.lower():
        log.warning("YouTube login may have failed or needs 2FA")
        return False
    log.info(f"✅ YouTube logged in: {page.url[:40]}")
    return True

async def post_to_facebook(page, img_path, caption):
    log.info("Posting to Facebook...")
    await page.goto("https://web.facebook.com/")
    await asyncio.sleep(2)
    
    for sel in ["[aria-label='Photo/video']", "text=Photo/video", "text=Foto/video", "[aria-label='Crear publicación']"]:
        try:
            await page.click(sel, timeout=5000)
            break
        except:
            continue
    await asyncio.sleep(2)
    
    await page.set_input_files("input[type='file']", img_path)
    await asyncio.sleep(4)
    
    for sel in ["[aria-label='Write a caption...']", "[contenteditable='true']", "[aria-label='Escribe un pie de foto...']", "div[contenteditable='true']"]:
        try:
            await page.fill(sel, caption, timeout=3000)
            break
        except:
            continue
    
    await page.click("text=Post", timeout=10000)
    await asyncio.sleep(4)
    log.info("✅ Facebook post done")
    return True

async def post_to_instagram(page, img_path, caption):
    log.info("Posting to Instagram...")
    await page.goto("https://www.instagram.com/")
    await asyncio.sleep(3)
    
    for label in ["New post", "Nueva publicación", "Create"]:
        try:
            await page.click(f"[aria-label='{label}']", timeout=5000)
            break
        except:
            continue
    await asyncio.sleep(2)
    
    await page.set_input_files("input[type='file']", img_path)
    await asyncio.sleep(4)
    
    await page.click("text=Next", timeout=10000)
    await asyncio.sleep(2)
    await page.click("text=Next", timeout=10000)
    await asyncio.sleep(2)
    
    for sel in ["[aria-label='Write a caption...']", "textarea", "[aria-label='Escribe un pie de foto...']"]:
        try:
            await page.fill(sel, caption, timeout=3000)
            break
        except:
            continue
    
    await page.click("text=Share", timeout=10000)
    await asyncio.sleep(4)
    log.info("✅ Instagram post done")
    return True

async def main():
    log.info("Starting SDC Social Manager...")
    
    p = await async_playwright().start()
    browser = await p.chromium.connect_over_cdp(CDP)
    
    # Get existing pages or create new ones
    pages = {}
    existing = browser.contexts[0].pages if browser.contexts else []
    
    for page in existing:
        url = page.url
        if "facebook" in url.lower():
            pages["facebook"] = page
        elif "instagram" in url.lower() or "instagram" in await page.title():
            pages["instagram"] = page
        elif "youtube" in url.lower() or "studio" in url.lower():
            pages["youtube"] = page
    
    # Create missing pages
    if "facebook" not in pages:
        pages["facebook"] = await browser.new_page()
    if "instagram" not in pages:
        pages["instagram"] = await browser.new_page()
    if "youtube" not in pages:
        pages["youtube"] = await browser.new_page()
    
    # Login check
    for name in ["facebook", "instagram", "youtube"]:
        page = pages[name]
        url = page.url
        needs = "login" in url.lower() or "signin" in url.lower()
        log.info(f"{name}: {'🔒 needs login' if needs else '🔓 ok'} ({url[:40]})")
        if needs:
            fn = globals().get(f"login_{name}")
            if fn:
                await fn(page)
    
    # Post image
    fb_path = "/tmp/formatted/sdc_brand_20260611-193130_facebook.png"
    ig_path = "/tmp/formatted/sdc_brand_20260611-193130_instagram.png"
    caption = "✨ Sonora Digital Corp — El futuro digital empieza aquí.\n\nTecnología, música e inteligencia artificial para la nueva era.\n\n#SDC #SonoraDigitalCorp #AI #Future #DigitalEmpire #Mystic #MexicoTech #Innovation"
    
    if os.path.exists(fb_path):
        await post_to_facebook(pages["facebook"], fb_path, caption)
    if os.path.exists(ig_path):
        await post_to_instagram(pages["instagram"], ig_path, caption)
    
    log.info("✅ All done. Keeping connection alive...")
    await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
