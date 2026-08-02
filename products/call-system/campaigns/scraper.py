import asyncio
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

LEADS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "leads")
os.makedirs(LEADS_PATH, exist_ok=True)

SEARCH_QUERIES = {
    "barberias": [
        "barbería en Hermosillo Sonora",
        "barber shop Hermosillo",
        "barbería en Obregón Sonora",
        "barberías en Nogales Sonora",
    ],
    "musica": [
        "estudio de grabación Hermosillo",
        "productor musical Sonora",
        "músico independiente Hermosillo",
    ],
    "bufetes": [
        "bufete jurídico Hermosillo",
        "abogado Hermosillo Sonora",
        "despacho legal Sonora",
    ],
    "restaurantes": [
        "restaurante en Hermosillo",
        "taquería Hermosillo",
        "food truck Hermosillo",
    ],
}

BUSINESS_KEYWORDS = {
    "barberias": ["barber", "barbería", "barber shop", "peluquería", "estilo", "corte"],
    "musica": ["música", "producción musical", "estudio", "artista", "banda", "músico"],
    "bufetes": ["abogado", "bufete", "jurídico", "legal", "despacho", "notaría"],
    "restaurantes": ["restaurante", "taquería", "comida", "tacos", "mariscos", "cocina"],
}


async def search_businesses(niche, location="Hermosillo"):
    query = SEARCH_QUERIES.get(niche, [f"{niche} en {location}"])[0]
    leads = []

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        logger.warning("Playwright no instalado. Usando modo simulado.")
        return _mock_search(niche)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            search_url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}/"
            await page.goto(search_url, timeout=30000)
            await asyncio.sleep(3)

            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(1)

            items = await page.query_selector_all('[role="article"]')
            seen_names = set()

            for item in items[:20]:
                try:
                    name_el = await item.query_selector('[class*="fontHeadline"]')
                    name = await name_el.inner_text() if name_el else ""

                    if not name or name in seen_names:
                        continue
                    seen_names.add(name)

                    try:
                        addr_el = await item.query_selector('[class*="fontBody"]')
                        address = await addr_el.inner_text() if addr_el else ""
                    except Exception:
                        address = ""

                    lead = {
                        "name": name.strip(),
                        "address": address.strip()[:100] if address else "",
                        "source": f"google_maps_{niche}",
                        "niche": niche,
                        "phone": "",
                        "company": name.strip(),
                        "status": "pending",
                    }
                    leads.append(lead)
                except Exception:
                    continue

            await browser.close()

    except Exception as e:
        logger.error(f"Error en scraper Playwright: {e}")
        leads = _mock_search(niche)

    for lead in leads:
        lead_path = os.path.join(LEADS_PATH, f"{_slugify(lead['name'])}.json")
        if not os.path.exists(lead_path):
            with open(lead_path, "w") as f:
                json.dump(lead, f, indent=2, ensure_ascii=False)

    logger.info(f"Scraper [{niche}]: {len(leads)} leads encontrados")
    return leads


def _mock_search(niche):
    mock_data = {
        "barberias": [
            {"name": "Barbería El Clásico", "address": "Hermosillo Centro"},
            {"name": "Estilo Urbano Barber Shop", "address": "Col. Pitic, Hermosillo"},
            {"name": "BarberKing Studio", "address": "Blvd. Kino, Hermosillo"},
            {"name": "La Casa del Barbero", "address": "Col. San Benito"},
            {"name": "Fade Zone Barbería", "address": "Plaza Zaragoza, Hermosillo"},
        ],
        "musica": [
            {"name": "Estudio 504", "address": "Hermosillo"},
            {"name": "Sonora Music Pro", "address": "Col. Centenario"},
            {"name": "Sound Factory Estudio", "address": "Col. Paseo"},
        ],
        "bufetes": [
            {"name": "Bufete Jurídico Integral", "address": "Hermosillo Centro"},
            {"name": "Asesores Legales Sonora", "address": "Col. Bugambilias"},
        ],
        "restaurantes": [
            {"name": "Tacos El Fogón", "address": "Col. Villa de Seris, Hermosillo"},
            {"name": "Mariscos El Puerto", "address": "Blvd. Kino, Hermosillo"},
            {"name": "Taquería El Vaquero", "address": "Col. Pitic"},
        ],
    }

    leads = []
    for m in mock_data.get(niche, []):
        lead = {**m, "source": f"mock_{niche}", "niche": niche, "phone": "", "company": m["name"], "status": "pending"}
        leads.append(lead)
        lead_path = os.path.join(LEADS_PATH, f"{_slugify(lead['name'])}.json")
        if not os.path.exists(lead_path):
            with open(lead_path, "w") as f:
                json.dump(lead, f, indent=2, ensure_ascii=False)
    return leads


def _slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def get_leads(niche=None, status=None):
    leads = []
    if os.path.exists(LEADS_PATH):
        for fname in os.listdir(LEADS_PATH):
            if fname.endswith(".json"):
                with open(os.path.join(LEADS_PATH, fname)) as f:
                    lead = json.load(f)
                if niche and lead.get("niche") != niche:
                    continue
                if status and lead.get("status") != status:
                    continue
                leads.append(lead)
    return leads


def mark_lead_contacted(name):
    path = os.path.join(LEADS_PATH, f"{_slugify(name)}.json")
    if os.path.exists(path):
        with open(path) as f:
            lead = json.load(f)
        lead["status"] = "contacted"
        with open(path, "w") as f:
            json.dump(lead, f, indent=2, ensure_ascii=False)
