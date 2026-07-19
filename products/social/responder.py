#!/usr/bin/env python3
"""SDC Social Auto-Responder — contexto por plataforma + keyword Sonora.
Detecta menciones, DMs, comentarios. Responde contextualmente.
Trigger: cuando alguien escribe 'sonora' → envía link freemium + captura lead.

Usage:
  python3 products/social/responder.py --check-all    # Revisa todas las plataformas
  python3 products/social/responder.py --respond      # Responde menciones pendientes
"""
import asyncio
import json
import os
import random
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parent.parent.parent
STATE_DIR = BASE / "state" / "social"
STATE_DIR.mkdir(parents=True, exist_ok=True)
COOKIES_FILE = STATE_DIR / "sdc-social-state.json"
LEADS_FILE = STATE_DIR / "leads.json"
LOG_FILE = STATE_DIR / "responder.log"

# ─── Contexto por plataforma ───
PLATFORM_CONTEXT = {
    "instagram": {
        "voice": "casual, visual, emojis, joven",
        "hashtags": "#Ciberseguridad #SDC #Mystic",
        "max_len": 2200,
        "style": "📸 Visual + directo",
    },
    "facebook": {
        "voice": "profesional pero cercano, dueño de negocio",
        "hashtags": "#Ciberseguridad #PYME #SDC",
        "max_len": 5000,
        "style": "📘 Casos de éxito + valor",
    },
    "tiktok": {
        "voice": "rápido, trend, directo, sin rodeos",
        "hashtags": "#ciberseguridad #parati #SDC",
        "max_len": 300,
        "style": "🎬 Trendy + llamativo",
    },
    "youtube": {
        "voice": "educativo, profundo, tutorial",
        "hashtags": "#Ciberseguridad #Tutorial #SDC",
        "max_len": 5000,
        "style": "📹 Educativo + demostración",
    },
}

# ─── Respuestas para keyword "Sonora" ───
SONORA_RESPONSES = [
    "¡Gracias por mencionar a Sonora! 🎉 Como agradecimiento, aquí tienes un diagnóstico de ciberseguridad GRATIS para tu empresa → wa.me/5216625383272?text=Quiero%20mi%20diagnóstico%20Sonora",
    "¡Sonora te saluda! 🛡️ Por ser parte de nuestra comunidad, reclama tu auditoría de seguridad sin costo → sonoradigitalcorp.com/cyber?ref=sonora",
    "¡Mencionaste la palabra mágica! 🔐 Accede a tu diagnóstico express completamente gratis. Solo 5 cupos esta semana → wa.me/5216625383272",
]

GENERIC_RESPONSES = {
    "cyber": [
        "¿Preocupado por tu seguridad online? Empieza con un diagnóstico gratis → wa.me/5216625383272",
        "El 60% de PYMEs que sufren un ataque cierran en 6 meses. No seas una estadística → sonoradigitalcorp.com/cyber",
    ],
    "ia": [
        "¿IA para tu negocio? Tenemos agentes que llaman, venden y atienden 24/7 → wa.me/5216625383272",
        "Nuestro agente IA ha hecho más de 500 llamadas con 34% de conversión. Prueba gratis → sonoradigitalcorp.com",
    ],
    "whatsapp": [
        "¿Bot para WhatsApp? Clientes 24/7 desde tu número. Pagos integrados → wa.me/5216625383272",
    ],
    "precio": [
        "Planes desde $299/mes. Todo incluido, sin contratos → sonoradigitalcorp.com/cyber#precios",
    ],
}


def log(msg):
    line = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def save_lead(platform, username, message, source):
    """Save lead and trigger freemium gate."""
    leads = []
    if LEADS_FILE.exists():
        leads = json.loads(LEADS_FILE.read_text())
    lead = {
        "id": f"lead-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "platform": platform,
        "username": username,
        "message": message[:200],
        "source": source,
        "captured_at": datetime.now().isoformat(),
        "status": "new",
        "sent_benefit": False,
    }
    leads.append(lead)
    LEADS_FILE.write_text(json.dumps(leads, indent=2))
    log(f"   💎 Lead captured: {username} via {platform} ({source})")
    return lead


def detect_intent(message: str) -> dict:
    """Detect intent from message text."""
    msg = message.lower()
    intent = "general"
    topics = []

    if "sonora" in msg:
        intent = "sonora_trigger"
    if any(w in msg for w in ["cyber", "seguridad", "hack", "virus", "ssl", "dmarc"]):
        intent = "cyber"
        topics.append("security")
    if any(w in msg for w in ["ia", "inteligencia", "agente", "automat", "bot"]):
        topics.append("ai")
        if intent == "general":
            intent = "ia"
    if any(w in msg for w in ["whatsapp", "whats", "wp"]):
        topics.append("whatsapp")
    if any(w in msg for w in ["precio", "costo", "cuánto", "cuanto", "pago", "plan"]):
        topics.append("pricing")
        if intent == "general":
            intent = "precio"
    if any(w in msg for w in ["hola", "buenos", "gracias", "info", "información"]):
        topics.append("greeting")

    return {"intent": intent, "topics": topics, "has_sonora": "sonora" in msg.lower()}


def generate_response(intent: str, platform: str, username: str = "") -> str:
    """Generate contextual response based on intent and platform."""
    ctx = PLATFORM_CONTEXT.get(platform, PLATFORM_CONTEXT["facebook"])
    greeting = f"@{username} " if username and platform in ("instagram", "tiktok") else f"{username}, " if username else ""

    if intent == "sonora_trigger":
        body = random.choice(SONORA_RESPONSES)
        return f"{greeting}{body}"

    responses = GENERIC_RESPONSES.get(intent, GENERIC_RESPONSES["cyber"])
    body = random.choice(responses)
    return f"{greeting}{body}"


# ─── Playwright Scanners ───

async def check_instagram_dms(page):
    """Check Instagram DMs and respond."""
    log("📸 Checking Instagram DMs...")
    try:
        await page.goto("https://www.instagram.com/direct/inbox/", timeout=30000)
        await asyncio.sleep(3)

        # Look for unread conversations
        unread = await page.query_selector_all('[role="listitem"]')
        log(f"   Conversations found: {len(unread)}")

        for conv in unread[:5]:
            try:
                await conv.click()
                await asyncio.sleep(2)

                # Get last message
                messages = await page.query_selector_all('div[role="row"]')
                if messages:
                    last_msg = messages[-1]
                    text = await last_msg.inner_text()
                    username_el = await page.query_selector('h2, h3, span')
                    username = await username_el.inner_text() if username_el else "unknown"

                    intent = detect_intent(text)
                    if intent["has_sonora"]:
                        response = generate_response("sonora_trigger", "instagram", username)
                        log(f"   💬 Sonora trigger from {username}: {text[:50]}")
                        # Send response via DM
                        msg_box = await page.query_selector('div[role="textbox"]')
                        if msg_box:
                            await msg_box.click()
                            await asyncio.sleep(0.5)
                            await msg_box.fill(response[:500])
                            await asyncio.sleep(1)
                            send_btn = await page.query_selector('div[role="button"]')
                            if send_btn:
                                await send_btn.click()
                                log(f"   ✅ Response sent to {username}")
                            save_lead("instagram", username, text, "dm_sonora_trigger")
            except Exception as e:
                log(f"   ⚠️ Error processing conversation: {e}")
    except Exception as e:
        log(f"   ❌ Instagram DM error: {e}")


async def check_facebook_comments(page):
    """Check Facebook notifications and comments."""
    log("📘 Checking Facebook...")
    try:
        await page.goto("https://www.facebook.com/notifications", timeout=30000)
        await asyncio.sleep(3)

        notifications = await page.query_selector_all('[role="listitem"]')
        log(f"   Notifications: {len(notifications)}")

        for notif in notifications[:5]:
            try:
                await notif.click()
                await asyncio.sleep(3)
                text = await page.inner_text('body')
                intent = detect_intent(text)
                if intent["has_sonora"]:
                    log(f"   💬 Sonora mention detected")
                    save_lead("facebook", "unknown", text[:200], "comment_sonora")
            except Exception as e:
                log(f"   ⚠️ Error: {e}")
    except Exception as e:
        log(f"   ❌ Facebook error: {e}")


async def run():
    """Main: check all platforms and respond."""
    log("=" * 50)
    log("🚀 SDC Social Auto-Responder")
    log("=" * 50)

    if not COOKIES_FILE.exists():
        log("❌ No cookies file. Run social-cookies.py first")
        return

    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir="/tmp/sdc-social-responder",
            headless=True,
            args=["--no-sandbox"],
        )

        with open(COOKIES_FILE) as f:
            state = json.load(f)
        await browser.add_cookies(state.get("cookies", []))
        log(f"🍪 Cookies: {len(state.get('cookies', []))}")

        page = await browser.new_page()

        await check_instagram_dms(page)
        await check_facebook_comments(page)

        await browser.close()

    log("✅ Auto-responder cycle complete\n")


if __name__ == "__main__":
    if "--check-all" in sys.argv or len(sys.argv) == 1:
        asyncio.run(run())
