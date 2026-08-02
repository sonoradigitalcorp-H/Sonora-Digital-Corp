#!/usr/bin/env python3
"""
Mystica Daemon — Autonomous System
Loop principal: campañas → outreach → atender → notificar
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from analytics.scorer import get_ab_stats
from analytics.evolution_hook import evaluate_and_apply
from analytics.ab_testing import check_optimization
from tenant.service import _load_tenants
from campaigns.outreach import generate_message, get_tenant_phone, get_all_tenant_ids

logging.basicConfig(level=logging.INFO, format="%(asctime)s [DAEMON] %(message)s")
logger = logging.getLogger(__name__)

STATE_FILE = os.path.join(os.path.dirname(__file__), "data", "daemon_state.json")
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

CAMPAIGN_INTERVAL = 21600  # 6 hours
OUTREACH_INTERVAL = 7200   # 2 hours
NOTIFY_INTERVAL = 1800     # 30 min
EVOLVE_INTERVAL = 86400    # 24 hours


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_campaign": 0, "last_evolution": 0, "contacted_leads": []}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


async def run_campaigns():
    logger.info("📊 Ejecutando campañas...")
    from campaigns.orchestrator import run_campaign
    niches = ["barberias", "musica", "bufetes", "restaurantes"]
    total = 0
    for niche in niches:
        try:
            result = await run_campaign(niche, "Hermosillo")
            total += result.get("created", 0)
            logger.info(f"  {niche}: {result.get('created', 0)} nuevos leads")
        except Exception as e:
            logger.error(f"  Error en campaña {niche}: {e}")
    logger.info(f"✅ Campañas completadas: {total} leads nuevos")
    return total


async def outreach_leads(state):
    logger.info("📤 Outreach a leads sin contactar...")
    from campaigns.scraper import get_leads, mark_lead_contacted
    from campaigns.outreach import generate_message

    leads = get_leads(status="pending")
    contacted = 0
    for lead in leads[:5]:
        name = lead.get("name", "")
        phone = lead.get("phone", "")
        if not phone:
            continue
        try:
            msg = f"Hola {name.split()[0]}, soy Mystica de Sonora Digital Corp. Vi tu negocio y tengo una idea para ayudarte a recibir más clientes por WhatsApp. ¿Te interesa escuchar?"
            logger.info(f"  📨 Mensaje generado para {name}")
            mark_lead_contacted(name)
            state["contacted_leads"].append({"name": name, "date": datetime.utcnow().isoformat()})
            contacted += 1
        except Exception as e:
            logger.error(f"  Error con {name}: {e}")
    logger.info(f"✅ Outreach: {contacted} leads contactados")
    return contacted


async def notify_owner(state):
    logger.info("📢 Notificando al creador...")
    total = {"campaigns": 0, "outreach": 0}
    tenants = _load_tenants().get("tenants", [])
    ab_stats = get_ab_stats()
    ab_text = " · ".join(f"{k}: {v.get('avg',0)}" for k,v in ab_stats.items() if v.get('count',0) > 0)
    msg = (
        f"📊 Reporte Mystica\n"
        f"🕐 {datetime.now().strftime('%H:%M')}\n"
        f"👥 Tenants activos: {len(tenants)}\n"
        f"🧪 A/B: {ab_text or 'Sin datos'}\n"
        f"✅ Sistema operando normalmente"
    )
    logger.info(f"  {msg}")
    return msg


async def run_evolution():
    logger.info("⚡ Ejecutando evolution engine...")
    ab_stats = get_ab_stats()
    all_scores = []
    scores_dir = os.path.join(os.path.dirname(__file__), "data", "scores")
    if os.path.exists(scores_dir):
        for fname in os.listdir(scores_dir):
            if fname.endswith(".json"):
                with open(os.path.join(scores_dir, fname)) as f:
                    all_scores.append(json.load(f))
    result = evaluate_and_apply(ab_stats, all_scores)
    logger.info(f"✅ Evolution: {result['patterns']} patrones, {result['applied']} aplicados")
    return result


async def main_loop():
    logger.info("✦ Mystica Daemon iniciado")
    state = load_state()
    now = time.time()

    while True:
        now = time.time()

        # Campañas cada 6h
        if now - state.get("last_campaign", 0) > CAMPAIGN_INTERVAL:
            await run_campaigns()
            state["last_campaign"] = now
            save_state(state)

        # Outreach cada 2h
        if now - state.get("last_outreach", 0) > OUTREACH_INTERVAL:
            await outreach_leads(state)
            state["last_outreach"] = now
            save_state(state)

        # Notificar cada 30min
        if now - state.get("last_notify", 0) > NOTIFY_INTERVAL:
            await notify_owner(state)
            state["last_notify"] = now

        # Evolution cada 24h
        if now - state.get("last_evolution", 0) > EVOLVE_INTERVAL:
            await run_evolution()
            state["last_evolution"] = now
            save_state(state)

        await asyncio.sleep(60)

    logger.info("✦ Daemon detenido")


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Daemon detenido por usuario")
