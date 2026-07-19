#!/usr/bin/env python3
"""Playwright script: navigate openrouter.ai/keys, revoke old API keys."""
import asyncio
import os
import re

from playwright.async_api import async_playwright

HOME = os.path.expanduser("~")
SCREENSHOT_DIR = os.path.join(HOME, "jarvis/screenshots/revoke_keys")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

KEEP_KEYS = set(os.environ.get("OPENROUTER_KEEP_KEYS", "").split(",")) - {""}

async def main():
    print("=" * 70)
    print("  🔍 PLAYWRIGHT — REVOCAR KEYS VIEJAS OPENROUTER")
    print("=" * 70)

    async with async_playwright() as p:
        # Try persistent context first (Chrome profile) for saved login
        browser = None
        context = None
        user_data_dir = os.path.join(HOME, ".config/google-chrome")
        if os.path.isdir(user_data_dir):
            try:
                print("\n📁 Intentando con perfil Chrome (login guardado)...")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    executable_path="/opt/google/chrome/chrome",
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                    viewport={"width": 1280, "height": 900},
                )
                page = context.pages[0] if context.pages else await context.new_page()
                print("   ✅ Perfil Chrome cargado")
            except Exception as e:
                print(f"   ⚠️  Error con perfil: {e}")
                print("   Intentando sin perfil...")

        if not context:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context(viewport={"width": 1280, "height": 900})
            page = await context.new_page()
            print("   ✅ Navegador sin perfil (no hay login guardado)")

        # Navigate to OpenRouter keys
        print("\n📡 Navegando a https://openrouter.ai/keys ...")
        try:
            await page.goto("https://openrouter.ai/keys", wait_until="networkidle", timeout=20000)
        except Exception as e:
            print(f"   ⚠️  Timeout/error: {e}")
            print("   Tomando screenshot del estado actual...")

        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01-keys-page.png"), full_page=True)
        print("   ✅ Screenshot guardado: 01-keys-page.png")

        current_url = page.url
        print(f"\n📍 URL actual: {current_url}")

        if "login" in current_url or "auth" in current_url or "sign-in" in current_url:
            print("\n⚠️  REDIRIGIDO A LOGIN — No hay sesión activa en el perfil Chrome")
            print("\n💡 Para revocar keys manualmente:")
            print("   1. Abre Chrome y ve a https://openrouter.ai/keys")
            print("   2. Inicia sesión con: perrykingla.69@gmail.com")
            print("   3. Revoca TODAS las keys excepto:")
            print("      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")
            print("\n📸 Screenshot de login guardado")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02-login-page.png"))
            await context.close()
            if browser:
                await browser.close()
            return

        print("   ✅ Sesión activa — dentro de openrouter.ai")

        # Extract visible keys from page
        content = await page.content()
        found_keys = set()
        for match in re.finditer(r'sk-or-v1-[a-zA-Z0-9]{40,}', content):
            found_keys.add(match.group())

        print(f"\n🔑 Keys en la página: {len(found_keys)}")
        for k in sorted(found_keys):
            masked = k[:15] + "..." + k[-6:]
            action = "✅ CONSERVAR" if k in KEEP_KEYS else "🔴 REVOCAR"
            print(f"   {action}: {masked}")

        to_revoke = found_keys - KEEP_KEYS
        if not to_revoke:
            print("\n🎯 No hay keys viejas que revocar. ¡Todo limpio!")
            await context.close()
            if browser:
                await browser.close()
            return

        # Try to click revoke buttons
        print(f"\n🔄 Intentando revocar {len(to_revoke)} keys...")
        revoked = 0
        for key in to_revoke:
            try:
                btn = await page.query_selector(f'button:has-text("{key[:20]}")')
                if not btn:
                    btn = await page.query_selector(f'[data-key*="{key[:20]}"] button, tr:has-text("{key[:20]}") button')
                if not btn:
                    btn = await page.query_selector('tr:has-text("Revoke") button, button:has-text("Revoke")')
                if btn:
                    page.once("dialog", lambda d: asyncio.ensure_future(d.accept()))
                    await btn.click()
                    await asyncio.sleep(1.5)
                    revoked += 1
                    print(f"   ✅ Revocada: {key[:20]}...")
                else:
                    print(f"   ⚠️  No se encontró botón para: {key[:20]}...")
            except Exception as e:
                print(f"   ❌ Error: {e}")

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03-after-revoke.png"))
        print(f"\n📊 Revocados: {revoked}/{len(to_revoke)}")

        await context.close()
        if browser:
                await browser.close()

    print("\n" + "=" * 70)
    print(f"  📸 Screenshots en: {SCREENSHOT_DIR}/")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
