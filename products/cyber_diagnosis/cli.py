#!/usr/bin/env python3
"""Cyber Diagnosis Express — CLI Completo
Uso:
  python3 products/cyber_diagnosis/cli.py <dominio> [--audio] [--slides] [--rmp]
  python3 products/cyber_diagnosis/cli.py campaign --niche ecommerce
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE))

from products.cyber_diagnosis.scan import scan_domain
from products.cyber_diagnosis.report import generate_html, generate_rmp, generate_slides
from products.cyber_diagnosis.voice import generate_script, generate_audio, generate_whatsapp_message


def cmd_scan(args):
    domain = args.domain.lower().strip()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n🔍 Escaneando {domain}...")
    result = scan_domain(domain)

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return

    # HTML Report
    html = generate_html(result)
    html_path = output_dir / f"cyber-diagnosis-{domain}.html"
    html_path.write_text(html)
    print(f"✅ Reporte: file://{html_path.absolute()}")

    # Slides
    slides_path = None
    if args.slides:
        slides = generate_slides(result)
        slides_path = output_dir / f"cyber-diagnosis-{domain}-slides.html"
        slides_path.write_text(slides)
        print(f"✅ Slides: file://{slides_path.absolute()}")

    # Risk Management Plan
    rmp_path = None
    if args.rmp:
        rmp = generate_rmp(result)
        rmp_path = output_dir / f"RMP-{domain}.html"
        rmp_path.write_text(rmp)
        print(f"✅ RMP: file://{rmp_path.absolute()}")

    # Audio + Script
    audio_path = None
    if args.audio:
        script = generate_script(result, args.company)
        script_path = output_dir / f"mystic-script-{domain}.txt"
        script_path.write_text(script)
        print(f"✅ Guión: file://{script_path.absolute()}")
        print("🎙️  Generando audio con Mystic (Dalia Neural)...")
        audio_path = generate_audio(script)
        if audio_path:
            print(f"✅ Audio: file://{audio_path}")
        else:
            print("⚠️  No se pudo generar audio")

        # WhatsApp message
        wa = generate_whatsapp_message(result)
        wa_path = output_dir / f"whatsapp-{domain}.txt"
        wa_path.write_text(wa)
        print(f"💬 WhatsApp: file://{wa_path.absolute()}")

    # Summary
    s = result["summary"]
    print(f"\n{'='*50}")
    print(f"  {domain}: {result['grade']} ({result['score']}/100)")
    print(f"  ✅ {s['ok']}  ⚠️  {s['warning']}  ❌ {s['error']}")
    if s["criticos"]:
        print(f"  🔴 Críticos: {', '.join(s['criticos'])}")
    print(f"{'='*50}")


def cmd_campaign(args):
    """Genera campañas de marketing por nicho con trending news."""
    print(f"\n📢 Generando campaña para nicho: {args.niche}...\n")

    campaigns = {
        "ecommerce": {
            "title": "Protege tu Tienda Online",
            "hook": "El 60% de las PYMEs que sufren un ciberataque cierran en 6 meses.",
            "body": "Tu tienda online maneja datos de clientes, pagos, inventario. Una vulnerabilidad DNS o un SSL mal configurado puede costarte todo.",
            "cta": "Auditoría gratuita — 3 cupos esta semana",
        },
        "agencias": {
            "title": "Tu Agencia, Tu Reputación",
            "hook": "Tus clientes confían su marca en tus manos. ¿Y si tu web está comprometida?",
            "body": "Agencias creativas son el target #1 de ataques porque manejan múltiples cuentas. Un breach en tu dominio afecta a todos tus clientes.",
            "cta": "Diagnóstico gratis — protege a tus clientes",
        },
        "real_estate": {
            "title": "Propiedades Seguras",
            "hook": "Datos de compradores, escrituras, pagos — todo en tu web. ¿Está protegida?",
            "body": "El sector inmobiliario maneja información sensible. Un ataque no solo expone datos, sino que detiene operaciones.",
            "cta": "Evaluación gratuita — 48h de validez",
        },
        "prof_services": {
            "title": "Confidencialidad Profesional",
            "hook": "Bufetes, contadores, consultores — objetivo #1 de ransomware en 2026.",
            "body": "Manejas información privilegiada de clientes. Un ataque ransomware no solo secuestra tus datos, destruye tu reputación.",
            "cta": "Protege tu despacho — auditoría sin costo",
        },
        "startups": {
            "title": "De 0 a Hack en 3 Meses",
            "hook": "Las startups crecen rápido... y los atacantes lo saben.",
            "body": "Priorizas producto sobre seguridad. Es normal. Pero una vulnerabilidad hoy puede ser un breach mañana.",
            "cta": "Crece seguro — diagnóstico express gratis",
        },
    }

    camp = campaigns.get(args.niche, campaigns["ecommerce"])

    post = f"""📢 *{camp['title']}*
    🔥 {camp['hook']}

    {camp['body']}

    🛡️ *{camp['cta']}*
    ⏳ Solo {args.slots or 5} cupos esta semana

    👇 Escríbenos para agendar tu auditoría
    https://wa.me/5216625383272

    #Ciberseguridad #{args.niche} #SDC #Mystic
    """
    print(post)

    # Save to file
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"campaign-{args.niche}-{datetime.now().strftime('%Y%m%d')}.txt"
    path.write_text(post)
    print(f"✅ Campaña guardada: file://{path.absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Cyber Diagnosis Express — SDC")
    sub = parser.add_subparsers(dest="command")

    # Scan command
    scan_p = sub.add_parser("scan", help="Escanea un dominio")
    scan_p.add_argument("domain", help="Dominio (ej: empresa.com)")
    scan_p.add_argument("--audio", action="store_true", help="Generar audio Mystic")
    scan_p.add_argument("--slides", action="store_true", help="Generar presentación")
    scan_p.add_argument("--rmp", action="store_true", help="Generar Risk Management Plan")
    scan_p.add_argument("--company", help="Nombre de la empresa (para el guión)")
    scan_p.add_argument("--output", "-o", default="./reports")
    scan_p.add_argument("--json", action="store_true")

    # Campaign command
    camp_p = sub.add_parser("campaign", help="Genera campaña de marketing")
    camp_p.add_argument("--niche", default="ecommerce",
                        choices=["ecommerce", "agencias", "real_estate", "prof_services", "startups"])
    camp_p.add_argument("--slots", type=int, default=5)
    camp_p.add_argument("--output", "-o", default="./campaigns")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "campaign":
        cmd_campaign(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
