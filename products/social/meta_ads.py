#!/usr/bin/env python3
"""SDC Meta Ads Manager — campañas + leads desde Meta Business Suite.
Crea audiencias, sincroniza leads desde formularios de Meta, maneja conversiones.

Usage:
  python3 products/social/meta_ads.py status                # Estado de campañas
  python3 products/social/meta_ads.py leads                 # Descargar leads de Meta
  python3 products/social/meta_ads.py sync                  # Sincronizar leads → CRM
  python3 products/social/meta_ads.py campaign --budget 500 # Crear campaña
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx

BASE = Path(__file__).resolve().parent.parent.parent
STATE_DIR = BASE / "state" / "social"
STATE_DIR.mkdir(parents=True, exist_ok=True)

META_CONFIG = STATE_DIR / "meta_ads.json"
LEADS_FILE = STATE_DIR / "leads.json"
META_LEADS_FILE = STATE_DIR / "meta_leads.json"

# ─── Meta Business SDK placeholder ───
# Para activar: crear app en developers.facebook.com
# Obtener: access_token, page_id, ad_account_id, form_id
META_CREDENTIALS = {
    "access_token": os.environ.get("META_ADS_TOKEN", ""),
    "ad_account_id": os.environ.get("META_AD_ACCOUNT", ""),
    "page_id": os.environ.get("META_PAGE_ID", ""),
    "form_id": os.environ.get("META_FORM_ID", ""),
}


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def get_leads_from_meta():
    """Descarga leads desde formularios de Meta (Instagram/Facebook)."""
    token = META_CREDENTIALS["access_token"]
    form_id = META_CREDENTIALS["form_id"]
    if not token or not form_id:
        log("⚠️  Meta Ads no configurado. Faltan token o form_id")
        log("   Crea: state/social/meta_ads.json con { access_token, ad_account_id, page_id, form_id }")
        return []

    try:
        url = f"https://graph.facebook.com/v21.0/{form_id}/leads"
        params = {"access_token": token, "fields": "id,created_time,field_data"}
        r = httpx.get(url, params=params, timeout=15)
        data = r.json()

        leads = []
        for lead in data.get("data", []):
            fields = {f["name"]: f["values"][0] for f in lead.get("field_data", [])}
            leads.append({
                "id": lead["id"],
                "meta_id": lead["id"],
                "name": fields.get("full_name", fields.get("name", "")),
                "email": fields.get("email", ""),
                "phone": fields.get("phone", fields.get("whatsapp", "")),
                "niche": fields.get("niche", fields.get("tipo_negocio", "")),
                "team": fields.get("team", fields.get("tamano_equipo", "")),
                "source": "meta_ads",
                "captured_at": lead.get("created_time", datetime.now().isoformat()),
                "status": "new",
            })
        return leads
    except Exception as e:
        log(f"❌ Error descargando leads de Meta: {e}")
        return []


def sync_leads():
    """Sincroniza leads de Meta con nuestro CRM local."""
    meta_leads = get_leads_from_meta()
    if not meta_leads:
        return

    # Load existing leads
    existing = []
    if LEADS_FILE.exists():
        existing = json.loads(LEADS_FILE.read_text())

    existing_ids = {l.get("meta_id", l["id"]) for l in existing}
    new_leads = [l for l in meta_leads if l["meta_id"] not in existing_ids]

    if not new_leads:
        log("📭 No hay leads nuevos de Meta")
        return

    existing.extend(new_leads)
    LEADS_FILE.write_text(json.dumps(existing, indent=2))
    log(f"✅ {len(new_leads)} lead(s) sincronizados desde Meta Ads")

    # Save raw Meta leads
    META_LEADS_FILE.write_text(json.dumps(meta_leads, indent=2))

    # For each new lead, print details
    for l in new_leads:
        log(f"   🆕 {l['name']} — {l.get('niche','?')} — {l.get('team','?')} — {l['source']}")


def campaign_status():
    """Muestra estado de campañas (placeholder — requiere Meta Ads API con permisos)."""
    token = META_CREDENTIALS["access_token"]
    account = META_CREDENTIALS["ad_account_id"]

    if not token or not account:
        log("⚠️  Meta Ads no configurado")
        return

    try:
        url = f"https://graph.facebook.com/v21.0/act_{account}/campaigns"
        params = {
            "access_token": token,
            "fields": "id,name,status,daily_budget,lifetime_budget,insights.date_preset(last_7d){spend,impressions,clicks,conversions}",
            "limit": 10,
        }
        r = httpx.get(url, params=params, timeout=15)
        campaigns = r.json().get("data", [])

        log(f"\n📊 Meta Ads Campaigns ({len(campaigns)}):")
        for c in campaigns:
            ins = c.get("insights", {}).get("data", [{}])[0] if c.get("insights") else {}
            status_icon = "✅" if c.get("status") == "ACTIVE" else "⏸️" if c.get("status") == "PAUSED" else "❌"
            log(f"  {status_icon} {c['name']}")
            log(f"     Presupuesto: ${int(c.get('daily_budget',0))/100:.0f}/día")
            log(f"     Gasto: ${float(ins.get('spend',0)):.0f} | Impresiones: {ins.get('impressions','N/A')}")
            log(f"     Clics: {ins.get('clicks','N/A')} | Conversiones: {ins.get('conversions','N/A')}")
            log(f"     Estado: {c.get('status','?')}")
    except Exception as e:
        log(f"❌ Error obteniendo campañas: {e}")


def create_campaign(name, budget=500, niche=None):
    """Crea campaña en Meta Ads (requiere access_token con permisos ads:management)."""
    token = META_CREDENTIALS["access_token"]
    account = META_CREDENTIALS["ad_account_id"]

    if not token or not account:
        log("⚠️  Meta Ads no configurado")
        return

    niche_interest = {
        "ecommerce": ["Online shopping", "E-commerce", "Shopify", "Magento"],
        "startups": ["Startup", "Technology", "SaaS", "Software as a service"],
        "agencias": ["Marketing agency", "Creative agency", "Digital marketing"],
        "real_estate": ["Real estate", "Property", "Inmobiliaria"],
        "prof_services": ["Lawyer", "Accounting", "Consulting", "Professional services"],
    }
    interests = niche_interest.get(niche, [])

    try:
        # Create Campaign
        log(f"📢 Creando campaña: {name} (${budget}/día)")

        # This is a placeholder — Meta Ads API requires complex targeting setup
        log(f"   Target: {', '.join(interests) if interests else 'General'}")
        log(f"   Placements: Instagram Feed, Facebook Feed, Stories")
        log(f"   Objective: LEAD_GENERATION")

        # Save campaign config
        config_file = STATE_DIR / "campaigns.json"
        campaigns = []
        if config_file.exists():
            campaigns = json.loads(config_file.read_text())
        campaigns.append({
            "name": name,
            "budget": budget,
            "niche": niche,
            "interests": interests,
            "created_at": datetime.now().isoformat(),
            "status": "draft",
        })
        config_file.write_text(json.dumps(campaigns, indent=2))
        log(f"✅ Campaña '{name}' creada (draft). Actívala desde Meta Business Suite.")

    except Exception as e:
        log(f"❌ Error: {e}")


def generate_lead_summary():
    """Genera resumen de leads capturados."""
    if not LEADS_FILE.exists():
        log("📭 No hay leads")
        return

    leads = json.loads(LEADS_FILE.read_text())
    total = len(leads)
    new = sum(1 for l in leads if l.get("status") == "new")
    by_niche = {}
    by_source = {}

    for l in leads:
        n = l.get("niche", "otro")
        s = l.get("source", "desconocido")
        by_niche[n] = by_niche.get(n, 0) + 1
        by_source[s] = by_source.get(s, 0) + 1

    log(f"\n📊 Lead Summary ({total} total, {new} nuevos):")
    log(f"  Por nicho:")
    for n, c in sorted(by_niche.items(), key=lambda x: -x[1]):
        log(f"    {n}: {c}")
    log(f"  Por fuente:")
    for s, c in sorted(by_source.items(), key=lambda x: -x[1]):
        log(f"    {s}: {c}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 products/social/meta_ads.py <command> [opts]")
        print("  status              - Estado de campañas")
        print("  leads               - Descargar leads de Meta")
        print("  sync                - Sincronizar leads Meta → CRM")
        print("  campaign --budget X - Crear campaña")
        print("  summary             - Resumen de leads")
        return

    cmd = sys.argv[1]

    if cmd == "status":
        campaign_status()
    elif cmd == "leads":
        leads = get_leads_from_meta()
        log(f"📥 {len(leads)} leads desde Meta")
        for l in leads[:5]:
            log(f"   {l['name']} — {l.get('niche','?')} — {l.get('email','')}")
    elif cmd == "sync":
        sync_leads()
    elif cmd == "campaign":
        budget = int(sys.argv[sys.argv.index("--budget") + 1]) if "--budget" in sys.argv else 500
        niche = sys.argv[sys.argv.index("--niche") + 1] if "--niche" in sys.argv else None
        name = sys.argv[sys.argv.index("--name") + 1] if "--name" in sys.argv else f"SDC Cyber {datetime.now().strftime('%b')}"
        create_campaign(name, budget, niche)
    elif cmd == "summary":
        generate_lead_summary()
    else:
        print(f"Unknown: {cmd}")


if __name__ == "__main__":
    main()
