#!/usr/bin/env python3
"""Niche Generator — Genera landing, skills, catalog y pricing para un nicho.

Usage:
    python3 scripts/generate_niche.py --niche barbero --name "BarberKing Studio"
    python3 scripts/generate_niche.py --niche musico
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from string import Template

try:
    import yaml
except ImportError:
    print("❌ Se necesita PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    from ruamel.yaml import YAML
    from ruamel.yaml.comments import CommentedSeq, CommentedMap
    HAS_RUAMEL = True
except ImportError:
    HAS_RUAMEL = False

REPO = Path(__file__).resolve().parent.parent
PHONE = "5216623538272"
NICHE_JSON = REPO / "scripts" / "niche_templates" / "niches.json"
LANDING_TEMPLATE = REPO / "scripts" / "niche_templates" / "landing_template.html"
ONBOARDING_SKILL_TEMPLATE = REPO / "scripts" / "niche_templates" / "onboarding_skill_template.md"
CATALOG_SKILL_TEMPLATE = REPO / "scripts" / "niche_templates" / "catalog_skill_template.md"
REGISTRY_PATH = REPO / "products" / "registry.yaml"

NICHES = [
    "barbero", "abogado", "musico", "fitness", "coach", "restaurante",
]


def slugify(text):
    text = text.lower().replace(' ', '-')
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9-]', '', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def load_json(path):
    with open(path) as f:
        return json.load(f)


def read_template(path):
    return path.read_text()


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  ✅ {path.relative_to(REPO)}")


# ─── Landing Page Generator ──────────────────────────────────────────────

def process_landing(niche, name, slug, services_data, prices_data, colors):
    template = read_template(LANDING_TEMPLATE)
    sections_config = services_data["landing_sections"]

    # Extract sections: <!-- SECTION:name --> ... <!-- ENDSECTION:name -->
    section_pattern = re.compile(
        r'<!--\s*SECTION:(\w+)\s*-->\n?(.*?)\n?<!--\s*ENDSECTION:\1\s*-->',
        re.DOTALL,
    )
    all_sections = {}
    for m in section_pattern.finditer(template):
        all_sections[m.group(1)] = m.group(2)

    body_parts = []
    for sec_name in sections_config:
        if sec_name in all_sections:
            body_parts.append(all_sections[sec_name])

    # Remove section markers from template, keep only body
    body_only = section_pattern.sub('', template)

    # Find where </body> is and insert our sections before it
    head_end = body_only.index('</body>')
    head_part = body_only[:head_end]
    footer_part = body_only[head_end:]

    assembled = head_part + '\n'.join(body_parts) + '\n' + footer_part

    # Generate services HTML
    services_html_lines = []
    svc_names = services_data["services"]
    svc_tokens = services_data["tokens"]
    svc_prices = services_data["prices"]
    emojis = ["🎯", "🔥", "💎"]
    for i, svc_name in enumerate(svc_names):
        emoji = emojis[i] if i < len(emojis) else "✨"
        token = svc_tokens[i] if i < len(svc_tokens) else 0
        price = svc_prices[i] if i < len(svc_prices) else 0
        svc_slug = slugify(svc_name)
        svc_href = f"https://wa.me/{PHONE}?text=Hola%20quiero%20{svc_slug}%20para%20{slug}"
        services_html_lines.append(
            f'    <div class="card">'
            f'<div class="card-icon">{emoji}</div>'
            f'<h3>{svc_name}</h3>'
            f'<div class="price-tag">${price} <span>MXN</span></div>'
            f'<p>Desde {token} tokens · Entrega rápida</p>'
            f'<a href="{svc_href}"'
            f' target="_blank" class="cta-small">Solicitar →</a>'
            f'</div>'
        )
    services_html = '\n'.join(services_html_lines)

    # Generate pricing HTML
    pricing_html_lines = []
    tier_labels = ["Básico", "Pro", "Premium"]
    tier_emojis = ["🌱", "🔥", "💎"]
    for i, svc_name in enumerate(svc_names):
        price = svc_prices[i] if i < len(svc_prices) else 0
        label = tier_labels[i] if i < len(tier_labels) else svc_name
        emoji = tier_emojis[i] if i < len(tier_emojis) else "✨"
        featured = " featured" if i == 1 else ""
        plan_href = f"https://wa.me/{PHONE}?text=Hola%20quiero%20el%20plan%20{slugify(label)}%20de%20{slugify(name)}"
        pricing_html_lines.append(
            f'    <div class="price-card{featured}">'
            f'<div class="emoji">{emoji}</div>'
            f'<h3>{label}</h3>'
            f'<div class="sub-text">{svc_name}</div>'
            f'<div class="price">${price}<span>/servicio</span></div>'
            f'<a href="{plan_href}"'
            f' target="_blank" class="cta">Contratar →</a>'
            f'</div>'
        )
    pricing_html = '\n'.join(pricing_html_lines)

    # Compute price vars
    price_basic = svc_prices[0] if svc_prices else 0
    price_rec = svc_prices[1] if len(svc_prices) > 1 else price_basic
    price_prem = svc_prices[2] if len(svc_prices) > 2 else price_rec

    # Replacements
    wa_link = f"https://wa.me/{PHONE}?text=Hola%20quiero%20informes%20sobre%20{name.replace(' ', '%20')}%20en%20Sonora%20Digital%20Corp"
    uppercase_name = name.upper()

    assembled = assembled.replace('{{SERVICES_HTML}}', services_html)
    assembled = assembled.replace('{{PRICING_HTML}}', pricing_html)
    assembled = assembled.replace('{{NICHE_NAME}}', name)
    assembled = assembled.replace('{{NICHE_NAME_UPPER}}', uppercase_name)
    assembled = assembled.replace('{{NICHE_ID}}', services_data["id"])
    assembled = assembled.replace('{{SLUG}}', slug)
    assembled = assembled.replace('{{PRIMARY_COLOR}}', colors["primary"])
    assembled = assembled.replace('{{ACCENT_COLOR}}', colors["accent"])
    assembled = assembled.replace('{{PRIMARY_RGB}}', hex_to_rgb(colors["primary"]))
    assembled = assembled.replace('{{ACCENT_RGB}}', hex_to_rgb(colors["accent"]))
    assembled = assembled.replace('{{WA_LINK}}', wa_link)
    assembled = assembled.replace('{{WA_PHONE}}', PHONE)
    assembled = assembled.replace('{{PRICE_BASIC}}', str(price_basic))
    assembled = assembled.replace('{{PRICE_RECOMMENDED}}', str(price_rec))
    assembled = assembled.replace('{{PRICE_PREMIUM}}', str(price_prem))
    assembled = assembled.replace('{{PHONE}}', PHONE)

    return assembled


# ─── State Files Generator ───────────────────────────────────────────────

def generate_catalog_json(niche_id, name, slug, services, tokens, prices):
    items = []
    for i, svc in enumerate(services):
        item_id = f"{niche_id}-{slugify(svc)}"
        items.append({
            "id": item_id,
            "name": svc,
            "description": f"Servicio profesional de {svc.lower()} para {name}",
            "tokens": tokens[i],
            "price_mxn": prices[i],
            "delivery": "24-48 hrs",
            "revisions": 2,
        })
    catalog = {
        "version": "1.0.0",
        "niche": niche_id,
        "name": name,
        "slug": slug,
        "currency": "MXN",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "items": items,
    }
    return json.dumps(catalog, indent=2, ensure_ascii=False) + "\n"


def generate_pricing_json(niche_id, name, slug, services, tokens, prices):
    tiers = []
    for i, svc in enumerate(services):
        tiers.append({
            "service": svc,
            "tokens": tokens[i],
            "price_mxn": prices[i],
            "currency": "MXN",
        })
    pricing = {
        "version": "1.0.0",
        "niche": niche_id,
        "name": name,
        "slug": slug,
        "currency": "MXN",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "pricing_tiers": tiers,
    }
    return json.dumps(pricing, indent=2, ensure_ascii=False) + "\n"


# ─── Skill Files Generator ───────────────────────────────────────────────

def generate_onboarding_skill(niche_id, name, slug, triggers, services):
    template = read_template(ONBOARDING_SKILL_TEMPLATE)
    triggers_str = ", ".join(triggers)
    services_comma = ", ".join(services)
    reps = {
        "{{NICHE_ID}}": niche_id,
        "{{NICHE_NAME}}": name,
        "{{SLUG}}": slug,
        "{{TRIGGERS}}": triggers_str,
        "{{SERVICES_COMMA}}": services_comma,
    }
    for k, v in reps.items():
        template = template.replace(k, v)
    return template


def generate_catalog_skill(niche_id, name, slug, triggers):
    template = read_template(CATALOG_SKILL_TEMPLATE)
    triggers_str = ", ".join(triggers)
    reps = {
        "{{NICHE_ID}}": niche_id,
        "{{NICHE_NAME}}": name,
        "{{SLUG}}": slug,
        "{{TRIGGERS}}": triggers_str,
    }
    for k, v in reps.items():
        template = template.replace(k, v)
    return template


# ─── Registry Updater ────────────────────────────────────────────────────

def register_in_registry(niche_id, name, slug, services, prices):
    """Add product entry to registry.yaml if not already present."""
    prefix = f"niche-{slug}"

    registry_yaml = REGISTRY_PATH.read_text()

    if f"id: {prefix}" in registry_yaml:
        print(f"  ℹ️  Producto '{prefix}' ya existe en registry.yaml (idempotent)")
        return

    features = [f"Catálogo WhatsApp para {s}" for s in services]
    triggers = [
        f"event:niche:{niche_id}:message:received",
        f"event:niche:{niche_id}:catalog:requested",
    ]
    events = [
        f"niche:{niche_id}:onboarding:started",
        f"niche:{niche_id}:onboarding:completed",
        f"niche:{niche_id}:catalog:sent",
        f"niche:{niche_id}:service:selected",
    ]

    price_min = min(prices)
    price_max = max(prices)

    new_entry_lines = [
        "",
        f"  - id: {prefix}",
        f"    name: {name}",
        "    entity: Niche Agent",
        f"    tagline: \"Servicios profesionales de {name} vía WhatsApp\"",
        "    category: niche",
        "    tier: [pro, enterprise]",
        f"    price_mxn: {{pro: {price_min}, enterprise: {price_max}}}",
        f"    skills: [niche-{slug}-onboarding.skill.md, niche-{slug}-catalog.skill.md]",
        "    features:",
    ]
    for f in features:
        new_entry_lines.append(f"      - {f}")
    new_entry_lines.append("    triggers:")
    for t in triggers:
        new_entry_lines.append(f"      - {t}")
    new_entry_lines.append("    events:")
    for e in events:
        new_entry_lines.append(f"      - {e}")
    new_entry_lines.append("    cache: \"Cache-Control: no-cache\"")
    new_entry_lines.append("    auth: WhatsApp")
    new_entry_lines.append("    faqs:")
    new_entry_lines.append(f"      - p: \"¿Qué servicios ofrece {name}?\"")
    new_entry_lines.append(f"        r: \"Ofrecemos: {', '.join(services)}. Todo por WhatsApp.\"")
    new_entry_lines.append(f"      - p: \"¿Cuánto cuesta?\"")
    new_entry_lines.append(f"        r: \"Desde ${price_min} MXN. Consulta nuestro catálogo en WhatsApp.\"")

    new_block = "\n".join(new_entry_lines)

    # Find the products: line and insert before the end of list
    with open(REGISTRY_PATH, 'a') as f:
        f.write(new_block)
        f.write("\n")

    print(f"  ✅ Registrado en products/registry.yaml como '{prefix}'")


# ─── Main ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Niche Generator — Genera landing, skills, catalog y pricing para un nicho.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  python3 scripts/generate_niche.py --niche barbero --name \"BarberKing Studio\"\n"
            "  python3 scripts/generate_niche.py --niche musico\n"
        ),
    )
    parser.add_argument(
        "--niche", required=True, choices=NICHES,
        help="Tipo de nicho a generar",
    )
    parser.add_argument(
        "--name",
        help="Nombre del negocio (default: nombre del nicho, ej. 'Barbería')",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Sobrescribir archivos existentes",
    )
    args = parser.parse_args()

    niches = load_json(NICHE_JSON)
    niche_id = args.niche
    niche_data = niches[niche_id]
    name = args.name if args.name else niche_data["name"]
    slug = slugify(name)

    services = niche_data["services"]
    tokens = niche_data["tokens"]
    prices = niche_data["prices"]
    triggers = niche_data["triggers"]
    colors = niche_data["colors"]
    landing_sections = niche_data["landing_sections"]

    # Build enriched config that includes id
    services_config = dict(niche_data)
    services_config["id"] = niche_id

    # Ensure all directories exist
    landings_dir = REPO / "frontends" / "landings" / slug
    niches_state_dir = REPO / "state" / "niches" / slug
    skills_dir = REPO / "skills"

    title = f"🧬 {name}"
    sep = "=" * len(title)
    print(f"\n{sep}")
    print(f"{title}")
    print(f"{sep}")
    print(f"  Nicho: {niche_id}")
    print(f"  Slug:  {slug}")
    print()

    # 1. Landing page
    print("📄 Landing page:")
    landing_html = process_landing(niche_id, name, slug, services_config, prices, colors)
    landing_path = landings_dir / "index.html"
    if not landing_path.exists() or args.force:
        write_file(landing_path, landing_html)
    else:
        print(f"  ℹ️  {landing_path.relative_to(REPO)} ya existe (usa --force para sobrescribir)")

    # 2. Catalog JSON
    print("\n📦 State files:")
    catalog_json = generate_catalog_json(niche_id, name, slug, services, tokens, prices)
    catalog_path = niches_state_dir / "catalog.json"
    write_file(catalog_path, catalog_json)

    pricing_json = generate_pricing_json(niche_id, name, slug, services, tokens, prices)
    pricing_path = niches_state_dir / "pricing.json"
    write_file(pricing_path, pricing_json)

    # 3. Skills
    print("\n🧠 Skills:")
    onboarding_skill = generate_onboarding_skill(niche_id, name, slug, triggers, services)
    onboarding_path = skills_dir / f"niche-{slug}-onboarding.skill.md"
    if not onboarding_path.exists() or args.force:
        write_file(onboarding_path, onboarding_skill)
    else:
        print(f"  ℹ️  {onboarding_path.relative_to(REPO)} ya existe (usa --force para sobrescribir)")

    catalog_skill = generate_catalog_skill(niche_id, name, slug, triggers)
    catalog_skill_path = skills_dir / f"niche-{slug}-catalog.skill.md"
    if not catalog_skill_path.exists() or args.force:
        write_file(catalog_skill_path, catalog_skill)
    else:
        print(f"  ℹ️  {catalog_skill_path.relative_to(REPO)} ya existe (usa --force para sobrescribir)")

    # 4. Registry
    print("\n📋 Registry:")
    register_in_registry(niche_id, name, slug, services, prices)

    # 5. Summary
    wa_link = f"https://wa.me/{PHONE}?text=Hola%20quiero%20informes%20sobre%20{name.replace(' ', '%20')}%20en%20Sonora%20Digital%20Corp"
    print(f"\n{'=' * len(title)}")
    print(f"✅ {name} generado exitosamente")
    print(f"   🌐 Landing:    frontends/landings/{slug}/index.html")
    print(f"   📦 Catalog:    state/niches/{slug}/catalog.json")
    print(f"   💰 Pricing:    state/niches/{slug}/pricing.json")
    print(f"   🧠 Skill (on): skills/niche-{slug}-onboarding.skill.md")
    print(f"   🧠 Skill (cat): skills/niche-{slug}-catalog.skill.md")
    print(f"   📋 Registry:   products/registry.yaml")
    print(f"   💬 WhatsApp:   {wa_link}")
    print()


if __name__ == "__main__":
    main()
