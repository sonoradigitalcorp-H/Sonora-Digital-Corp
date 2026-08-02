import asyncio
import json
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from campaigns.scraper import search_businesses, get_leads, mark_lead_contacted
from tenant.service import create_tenant

logger = logging.getLogger(__name__)


async def run_campaign(niche, location="Hermosillo"):
    logger.info(f"Iniciando campaña: {niche} en {location}")
    leads = await search_businesses(niche, location)

    created = 0
    for lead in leads:
        name = lead.get("name", "").strip()
        company = lead.get("company", name)
        if not name:
            continue

        try:
            tenant = create_tenant(
                name=name.split(",")[0].strip() if "," in name else name,
                phone=lead.get("phone", ""),
                company=company,
                source=f"campaign_{niche}",
                niche=niche,
            )
            created += 1
            logger.info(f"  Lead creado: {name} → {tenant['id']}")
        except Exception as e:
            logger.error(f"  Error creando lead {name}: {e}")

    logger.info(f"Campaña completada: {len(leads)} leads, {created} nuevos")
    return {"total": len(leads), "created": created, "niche": niche}


def get_campaign_summary():
    niches = ["barberias", "musica", "bufetes", "restaurantes"]
    summary = {}
    for niche in niches:
        leads = get_leads(niche=niche)
        contacted = get_leads(niche=niche, status="contacted")
        summary[niche] = {"total": len(leads), "contacted": len(contacted)}
    return summary
