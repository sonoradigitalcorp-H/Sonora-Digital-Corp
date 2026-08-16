#!/usr/bin/env python3
"""social_pipeline_nathaly.py — Campaña de lanzamiento + automatización de contenido
para Instagram de Nathaly (Hermosillo Contabilidad).

- Genera calendario: 6 publicaciones/día (historias, reels, encuestas, carrusel)
  repartidas cada ~3 horas.
- Crea/elige contenido existente (canva + reel).
- Publica vía Composio Instagram (API key ~/.composio/agent.json).
- Dry-run por defecto (NO publica nada sin --live).
- Pide feedback al cliente cuando se detecta interacción (comentario).

Uso:
  python3 social_pipeline_nathaly.py            # dry-run: muestra plan
  python3 social_pipeline_nathaly.py --live     # publica de verdad (¡cuidado!)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
ASSETS = BASE / ".." / "03_Media_Assets"

# ─── Calendario editorial: 6 publicaciones al día, cada ~3h ───
# (historias, reels, encuestas, carrusel educativo)
DIARIO = [
    {"hora": "09:00", "tipo": "historia", "contenido": "Buenos días, ¿tu contabilidad al día? 📊", "asset": "canva/contabilidad.jpg"},
    {"hora": "12:00", "tipo": "reel", "contenido": "3 cosas que el SAT ve en tu negocio", "asset": "photos/reel_hermosillo.mp4"},
    {"hora": "15:00", "tipo": "encuesta", "contenido": "¿Qué te cuesta más? Contabilidad, SAT o impuestos", "asset": None, "opciones": ["Contabilidad", "SAT", "Impuestos", "Todo"]},
    {"hora": "18:00", "tipo": "carrusel", "contenido": "5 señales de que necesitas un contador", "asset": "canva/citas_sat.jpg"},
    {"hora": "21:00", "tipo": "historia", "contenido": "Tip del día: guarda tus facturas digitales", "asset": "canva/declaracion.jpg"},
    {"hora": "23:30", "tipo": "post", "contenido": "Cierre: agenda tu diagnóstico gratis", "asset": "canva/dashboard.jpg"},
]

# Captions listos (sin emojis excesivos, marca Nathaly)
CAPTIONS = {
    "contabilidad": "Tu contabilidad mensual bajo control. Estados financieros, IVA e ISR al día, sin multas ni sorpresas. Diagnóstico gratis por WhatsApp.",
    "citas_sat": "¿Necesitas cita ante el SAT? La agendamos por ti y te acompañamos en el trámite.",
    "declaracion": "Declaraciones sin errores. Nosotros nos encargamos, tú te enfocas en tu negocio.",
    "importacion": "Importaciones en regla: manifestación, pedimento y requisitos sin retrasos.",
    "dashboard": "Mira tu negocio en tiempo real con nuestro dashboard. Contabilidad clara, decisiones seguras.",
}


def get_composio_key():
    p = Path.home() / ".composio" / "agent.json"
    if not p.exists():
        print("⚠️  No hay ~/.composio/agent.json. Conecta composio primero.")
        sys.exit(1)
    d = json.loads(p.read_text())
    return d["composio"]["api_key"]


def plan_dia(fecha=None):
    """Genera el plan del día (6 publicaciones cada ~3h)."""
    fecha = fecha or datetime.now()
    plan = []
    for item in DIARIO:
        h, m = map(int, item["hora"].split(":"))
        ts = fecha.replace(hour=h, minute=m, second=0, microsecond=0)
        plan.append({**item, "ts": ts})
    return plan


def caption_para(asset):
    """Elige caption según el asset (por keyword)."""
    if not asset:
        return None
    for k, cap in CAPTIONS.items():
        if k in asset:
            return cap
    return CAPTIONS["contabilidad"]


def publicar_ig(composio, tool, args):
    """Publica en IG vía composio execute. Solo con --live."""
    pass  # implementación con composio SDK: INSTAGRAM_SEND_IMAGE / POST


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Publicar de verdad (default: dry-run)")
    ap.add_argument("--dias", type=int, default=1, help="Días a planear")
    args = ap.parse_args()

    key = get_composio_key()
    plan = plan_dia()

    print(f"📅 Plan de contenido Nathaly — {datetime.now().strftime('%Y-%m-%d')}")
    print(f"   API Composio: {key[:10]}...  |  Modo: {'LIVE' if args.live else 'DRY-RUN (no publica)'}")
    print("=" * 64)
    for p in plan:
        gap = "historia" if p["tipo"] == "historia" else p["tipo"]
        asset = p["asset"] or "—"
        print(f"  {p['hora']}  [{p['tipo']:<9}] {p['contenido'][:52]}")
        print(f"         asset: {asset}")

    if args.live:
        print("\n⚠️  MODO LIVE ACTIVADO — requiere composio SDK y conexión IG activa.")
        print("   (implementación de publicación vía INSTAGRAM_SEND_IMAGE pendiente de conexión real)")

    # Feedback: pedir aprobación del cliente para la campaña
    print("\n📣 Feedback del cliente: ¿apruebas esta campaña? (responder por WhatsApp/Telegram)")


if __name__ == "__main__":
    main()