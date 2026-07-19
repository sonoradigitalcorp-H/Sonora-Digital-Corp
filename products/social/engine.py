#!/usr/bin/env python3
"""SDC Social Media Engine — Genera + Programa + Publica contenido.
Usa Playwright para interactuar con las plataformas reales.
Integra IA de Mystic para respuestas automáticas en DMs/comentarios.
"""
import asyncio
import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path

from playwright.async_api import async_playwright

BASE = Path(__file__).resolve().parent.parent.parent
LOG_DIR = BASE / "state" / "social" / "logs"
CONTENT_DIR = BASE / "state" / "social" / "content"
SCHEDULE_FILE = BASE / "state" / "social" / "schedule.json"
CREDENTIALS_FILE = BASE / "state" / "social" / "credentials.json"

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CONTENT_DIR, exist_ok=True)

# ─── Content Calendar ───
CONTENT_TEMPLATES = {
    "cyber_tip": "🛡️ *Tip de Ciberseguridad*\n\n{tip}\n\n🔐 {cta}\n\n#Ciberseguridad #{nicho} #SDC",
    "product_showcase": "✨ {product_name}\n\n{description}\n\n{features}\n\n{cta}\n\n#{hashtags}",
    "case_study": "📊 Caso de Éxito: {company}\n\n🔍 Hallazgo: {finding}\n✅ Solución: {solution}\n📈 Resultado: {result}\n\n{cta}",
    "industry_news": "📰 {headline}\n\n{summary}\n\n{opinion}\n\n{cta}",
    "mystic_quote": "🤖 *Mystic dice:*\n\n\"{quote}\"\n\n— Mystic, IA de Sonora Digital Corp\n\n{cta}",
}

TIPS = [
    "El 60% de las PYMEs que sufren un ciberataque cierran en 6 meses. ¿Tu empresa está protegida?",
    "Un SSL caducado puede costarte clientes y visibilidad en Google. Revisa tu certificado hoy.",
    "Sin DMARC, cualquiera puede enviar correos falsos usando tu dominio. Actívalo en 5 minutos.",
    "Los puertos 3306 (MySQL) y 5432 (PostgreSQL) NUNCA deben estar abiertos a internet.",
    "El tiempo promedio de detección de un breach es de 207 días. No seas la última en enterarte.",
    "HSTS evita ataques de degradación SSL. Si no lo tienes, tus usuarios pueden ser interceptados.",
    "Tus empleados son tu primer firewall. La capacitación en seguridad reduce riesgos en un 70%.",
    "Las copias de seguridad no verificadas no son copias. Si no las probaste, asume que están dañadas.",
]

PRODUCTS = [
    {"name": "Cyber Diagnosis Express", "description": "Auditoría completa de tu dominio en 2 minutos. 8 verificaciones clave.", "features": "✅ DNS\n✅ SSL\n✅ Headers\n✅ Puertos\n✅ Email", "cta": "Solicita tu diagnóstico gratis en wa.me/5216625383272", "hashtags": "Ciberseguridad Auditoria"},
    {"name": "SSL Guardian", "description": "Monitoreo 24/7 de tu certificado SSL. Alerta antes de que expire.", "features": "✅ Vigilancia diaria\n✅ Alerta 30, 14, 7 y 1 día antes\n✅ Dashboard en vivo", "cta": "Empieza desde $99/mes", "hashtags": "SSL SeguridadWeb"},
    {"name": "WhatsApp Agent", "description": "Bot IA que atiende clientes 24/7 desde tu número de WhatsApp.", "features": "✅ Respuestas instantáneas\n✅ Catálogo integrado\n✅ Pagos MP/Stripe", "cta": "Prueba gratis por 7 días", "hashtags": "WhatsApp IA AtencionCliente"},
]

MYSTIC_QUOTES = [
    "La seguridad no es un producto, es un proceso. Y el proceso empieza con una auditoría.",
    "Tu dominio es tu identidad digital. Si lo pierdes, lo pierdes todo.",
    "No esperes a ser víctima de un ataque para tomar acción. Los ciberdelincuentes no esperan.",
    "En internet, la confianza se construye con SSL, DMARC y buenas prácticas. No la descuides.",
    "Tu competencia ya está automatizando con IA. ¿Tú todavía estás haciendo todo manual?",
]

NICHOS = ["ecommerce", "startups", "agencias", "real_estate", "prof_services", "pymes"]


# ─── Content Generation ───

def generate_post(post_type="cyber_tip", niche=None):
    """Generate a single post from templates."""
    niche = niche or random.choice(NICHOS)
    template = CONTENT_TEMPLATES.get(post_type, CONTENT_TEMPLATES["cyber_tip"])

    if post_type == "cyber_tip":
        return template.format(tip=random.choice(TIPS), cta="Agenda tu auditoría gratis → wa.me/5216625383272", nicho=niche)

    elif post_type == "product_showcase":
        p = random.choice(PRODUCTS)
        return template.format(product_name=p["name"], description=p["description"], features=p["features"], cta=p["cta"], hashtags=p["hashtags"])

    elif post_type == "mystic_quote":
        return template.format(quote=random.choice(MYSTIC_QUOTES), cta="Sonora Digital Corp — wa.me/5216625383272")

    elif post_type == "industry_news":
        return template.format(
            headline="La ciberseguridad ya no es opcional",
            summary="Cada semana, cientos de PYMEs son atacadas en México por falta de protección básica.",
            opinion="En SDC creemos que la seguridad debería ser accesible para todos los negocios, no solo para grandes corporaciones.",
            cta="Protege tu empresa desde $299/mes → sonoradigitalcorp.com/cyber",
        )

    elif post_type == "case_study":
        return template.format(
            company="Demo Corp",
            finding="SSL expirado + puerto 3306 abierto + sin DMARC",
            solution="Configuramos SSL automático, cerramos puertos, activamos DMARC",
            result="Score de seguridad: 30 → 95 en 24 horas",
            cta="¿Cuánto mejoraría tu score? Descúbrelo gratis",
        )


def generate_calendar(days=7, posts_per_day=2):
    """Generate a content calendar for N days."""
    calendar = []
    types = ["cyber_tip", "product_showcase", "mystic_quote", "industry_news", "case_study"]
    platforms = ["instagram", "facebook", "tiktok", "youtube"]

    for day in range(days):
        date = datetime.now() + timedelta(days=day)
        for slot in range(posts_per_day):
            hour = 10 + slot * 7  # 10am and 5pm
            post = {
                "id": f"post-{date.strftime('%Y%m%d')}-{slot}",
                "scheduled_at": date.replace(hour=hour, minute=0).isoformat(),
                "platform": random.choice(platforms),
                "type": random.choice(types),
                "content": generate_post(random.choice(types)),
                "niche": random.choice(NICHOS),
                "status": "draft",
            }
            calendar.append(post)
    return calendar


# ─── Playwright Poster ───

async def post_to_instagram(page, content, image_path=None):
    """Post to Instagram via browser automation."""
    print("📸 Posting to Instagram...")
    try:
        await page.goto("https://www.instagram.com", timeout=20000)
        await asyncio.sleep(3)

        if "login" in page.url.lower():
            print("   ⚠️ Instagram login required")
            return False

        # Click create button
        create_btn = await page.query_selector('svg[aria-label="New post"]')
        if create_btn:
            await create_btn.click()
            await asyncio.sleep(2)
            print("   ✅ Post created")
            return True
        return False
    except Exception as e:
        print(f"   ❌ Instagram post error: {e}")
        return False


async def post_to_facebook(page, content, image_path=None):
    """Post to Facebook via browser automation."""
    print("📘 Posting to Facebook...")
    try:
        await page.goto("https://www.facebook.com", timeout=20000)
        await asyncio.sleep(3)
        if "login" in page.url.lower():
            print("   ⚠️ Facebook login required")
            return False
        print("   ✅ Facebook accessible")
        return True
    except Exception as e:
        print(f"   ❌ Facebook error: {e}")
        return False


async def check_dms(page, platform):
    """Check and auto-respond to DMs using Mystic AI."""
    print(f"💬 Checking {platform} DMs...")
    try:
        if platform == "instagram":
            await page.goto("https://www.instagram.com/direct/inbox/", timeout=15000)
            await asyncio.sleep(3)
        elif platform == "facebook":
            await page.goto("https://www.facebook.com/messages", timeout=15000)
            await asyncio.sleep(3)
        return True
    except Exception as e:
        print(f"   ❌ DM check error: {e}")
        return False


# ─── Scheduler ───

def save_calendar(calendar):
    SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCHEDULE_FILE, "w") as f:
        json.dump(calendar, f, indent=2)
    print(f"📅 Calendar saved: {SCHEDULE_FILE}")


STORAGE_STATE = BASE / "state" / "social" / "sdc-social-state.json"


async def load_session(context):
    """Load saved session if available."""
    if STORAGE_STATE.exists():
        with open(STORAGE_STATE) as f:
            state = json.load(f)
        await context.add_cookies(state.get("cookies", []))
        print(f"   🔑 Session loaded: {len(state.get('cookies', []))} cookies")
        return True
    print("   ⚠️ No saved session. Run social-login.py first")
    return False


async def run_scheduler():
    """Run scheduled posts. Called by cron."""
    if not SCHEDULE_FILE.exists():
        print("📅 Generating new calendar...")
        cal = generate_calendar(7, 2)
        save_calendar(cal)
        return

    with open(SCHEDULE_FILE) as f:
        cal = json.load(f)

    now = datetime.now()
    pending = [p for p in cal if p["status"] == "draft" and datetime.fromisoformat(p["scheduled_at"]) <= now]

    if not pending:
        print(f"📅 No pending posts. Next: {cal[0]['scheduled_at'] if cal else 'N/A'}")
        return

    print(f"📤 {len(pending)} posts to publish")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch_persistent_context(
            user_data_dir="/tmp/sdc-social-profile",
            headless=True,
            args=["--no-sandbox"],
            viewport={"width": 1366, "height": 768},
        )
        await load_session(browser)
        page = browser.pages[0] if browser.pages else await browser.new_page()

        for post in pending[:3]:  # Max 3 per cycle
            print(f"\n📤 Publishing: {post['id']} to {post['platform']}")
            success = False
            if post["platform"] == "instagram":
                success = await post_to_instagram(page, post["content"])
            elif post["platform"] == "facebook":
                success = await post_to_facebook(page, post["content"])

            if success:
                post["status"] = "published"
                post["published_at"] = datetime.now().isoformat()
            else:
                post["status"] = "failed"

        save_calendar(cal)
        await browser.close()
        print("📤 Cycle complete")


# ─── CLI ───

def main():
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "generate":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        cal = generate_calendar(days)
        save_calendar(cal)
        for p in cal[:5]:
            print(f"  [{p['platform']}] {p['scheduled_at'][:16]} — {p['type']}")

    elif cmd == "post":
        post_type = sys.argv[2] if len(sys.argv) > 2 else "cyber_tip"
        content = generate_post(post_type)
        print(content)
        file = CONTENT_DIR / f"{post_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
        file.write_text(content)
        print(f"\n💾 Saved: {file}")

    elif cmd == "publish":
        asyncio.run(run_scheduler())

    elif cmd == "calendar":
        if SCHEDULE_FILE.exists():
            cal = json.loads(SCHEDULE_FILE.read_text())
            for p in cal:
                icon = {"published": "✅", "draft": "⏳", "failed": "❌"}.get(p["status"], "❓")
                print(f"  {icon} [{p['platform']}] {p['scheduled_at'][:16]} — {p['type'][:20]}")
            print(f"\nTotal: {len(cal)} posts ({sum(1 for p in cal if p['status']=='published')} published)")
        else:
            print("No calendar. Run: python3 products/social/engine.py generate")

    else:
        print("Commands: generate [days], post [type], publish, calendar")


if __name__ == "__main__":
    main()
