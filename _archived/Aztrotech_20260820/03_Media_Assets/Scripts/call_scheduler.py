#!/usr/bin/env python3
"""Call Scheduler + IVR — Aztrotech.

Permite que el agente agenda automáticamente llamadas con César.
Cuando el prospecto llama al número asignado:
  - IVR responde con voz de César
  - Pregunta disponibilidad
  - Agenda llamada en calendario

Uso:
    python3 call_scheduler.py --book --tenant aztrotech --name "Cliente" --phone "+52..."
    python3 call_scheduler.py --ivr --message "hola" --voice cesar
"""
import os, sys, json, random
from pathlib import Path
from datetime import datetime, timedelta

SCHEDULES_DIR = Path.home() / ".openclaw" / "workspace" / "schedules"
SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)

# Horarios disponibles de César (Hermosillo, MX)
CESAR_AVAILABILITY = {
    "lunes_viernes": ["09:00-12:00", "14:00-18:00"],
    "sabados": ["10:00-14:00"],
    "domingos": ["cerrado"]
}


def schedule_call(tenant: str, name: str, phone: str, preferred_day: str = None) -> dict:
    """Agenda una llamada con César. Devuelve opciones de horario."""
    now = datetime.now()

    # Calcular próximos días hábiles
    available_slots = []
    for i in range(14):  # Busca en próximas 2 semanas
        day = now + timedelta(days=i)
        day_name = day.strftime("%A").lower()

        if day_name == "sunday" or day_name == "domingo":
            continue

        slots = CESAR_AVAILABILITY.get("lunes_viernes", [])
        for slot in slots:
            start, end = slot.split("-")
            dt_start = datetime.strptime(f"{start}", "%H:%M")
            dt_end = datetime.strptime(f"{end}", "%H:%M")

            full_start = day.replace(hour=dt_start.hour, minute=dt_start.minute)
            full_end = day.replace(hour=dt_end.hour, minute=dt_end.minute)

            available_slots.append({
                "datetime": full_start.isoformat(),
                "display": full_start.strftime("%A %d/%m %H:%M"),
                "options": ["Confirmar", "Más tarde", "WhatsApp"]
            })

            if len(available_slots) >= 5:
                break

        if len(available_slots) >= 5:
            break

    # Guardar solicitud
    schedule_id = f"{tenant}_{now.timestamp()}"
    schedule_data = {
        "id": schedule_id,
        "tenant": tenant,
        "customer": {"name": name, "phone": phone},
        "requested_at": now.isoformat(),
        "slots": available_slots,
        "status": "pending",
        "ivr_message": f"Hola {name}, soy César. ¿Cuál de estos horarios te funciona para una llamada?"
    }

    with open(SCHEDULES_DIR / f"{schedule_id}.json", "w") as f:
        json.dump(schedule_data, f, indent=2)

    return {
        "status": "scheduled",
        "schedule_id": schedule_id,
        "slots": available_slots,
        "ivr_message": schedule_data["ivr_message"],
        "call_link": f"https://wa.me/{phone}?text=Hola%20César%20agendamos%20nuestra%20llamada%20de%20%243699"
    }


def generate_ivr_message(customer_name: str, package: str = "Growth AI Agent") -> str:
    """Genera mensaje IVR con voz de César (simulado)."""
    messages = [
        f"Hola {customer_name}, soy César Holguín de Aztrotech. Te contacto sobre",
        f"nuestro paquete {package} que incluye agente IA 24/7 para tu negocio.",
        f"¿Te interesa una llamada para explicarte {package}?",
        f"Si prefieres, puedes responder escribiendo 'HOY' para hablar ahora",
        f"o 'MANANA' para un horario más tarde."
    ]

    return " ".join(messages)


def package_info(package: str) -> dict:
    """Devuelve info del paquete solicitado."""
    packages = {
        "starter": {
            "name": "Starter AI Agent",
            "price": 999,
            "moneda": "USD",
            "features": ["Empleado digital 24/7", "WhatsApp auto-respuesta", "Captura leads básica", "Panel web simple"]
        },
        "growth": {
            "name": "Growth AI Agent",
            "price": 1999,
            "moneda": "USD",
            "features": ["Todo el Starter", "Redes sociales integradas", "CRM + scoring", "Onboarding page personalizado", "Soporte voz"]
        },
        "enterprise": {
            "name": "Enterprise AI Agent",
            "price": 3999,
            "moneda": "USD",
            "features": ["Todo el Growth", "Agentes multi-nicho", "Voz clonada oficial", "Landing page 3D", "Pipeline voz completo", "Soporte dedicado"]
        }
    }
    return packages.get(package.lower(), packages["growth"])


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Call Scheduler")
    ap.add_argument("--book", action="store_true", help="Schedule a call")
    ap.add_argument("--name", help="Customer name")
    ap.add_argument("--phone", help="Customer phone")
    ap.add_argument("--tenant", default="aztrotech", help="Tenant ID")
    ap.add_argument("--ivr", action="store_true", help="Generate IVR message")
    ap.add_argument("--message", default="", help="Message for IVR")
    ap.add_argument("--package", default="growth", help="Package name")
    args = ap.parse_args()

    if args.ivr:
        msg = generate_ivr_message(args.message, args.package)
        print(json.dumps({"status": "ivr", "message": msg, "package": package_info(args.package)}, indent=2))
    elif args.book:
        result = schedule_call(args.tenant, args.name, args.phone)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        ap.print_help()