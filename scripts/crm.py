#!/usr/bin/env python3
"""
CRM - Sonora Digital Corp Contact Relationship Management.
Uso: python3 scripts/crm.py <comando> [args]

Comandos:
  contacts                   - Listar todos los contactos
  contact --phone <num>      - Detalle de un contacto
  search --q <query>         - Buscar contactos
  update --phone <num> [opts]- Actualizar contacto
  log-wa --phone <num> --dir <in|out> --msg <txt>  - Registrar mensaje
  summary                    - Estadísticas de contactos
"""
import json
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import warnings

warnings.filterwarnings("ignore", message=".*relationship type.*")
warnings.filterwarnings("ignore", message=".*label in your query.*")

from src.core.neo4j_store import (
    contacts_summary,
    get_contact,
    get_contact_history,
    log_wa_message,
    search_contacts,
    update_contact,
)


def cmd_contacts():
    """List all contacts."""
    args = {"status": "", "query": ""}
    if "--status" in sys.argv:
        i = sys.argv.index("--status")
        args["status"] = sys.argv[i + 1]
    if "--q" in sys.argv:
        i = sys.argv.index("--q")
        args["query"] = sys.argv[i + 1]

    if args["query"]:
        results = search_contacts(query=args["query"])
    elif args["status"]:
        results = search_contacts(status=args["status"])
    else:
        results = search_contacts()

    print(json.dumps({"status": "ok", "count": len(results), "contacts": results}, indent=2, default=str))


def cmd_contact():
    """Get contact detail."""
    if "--phone" not in sys.argv:
        print(json.dumps({"status": "error", "message": "Requiere --phone"}))
        return
    i = sys.argv.index("--phone")
    phone = sys.argv[i + 1]
    contact = get_contact(phone)
    if not contact:
        print(json.dumps({"status": "error", "message": "Contacto no encontrado"}))
        return
    history = get_contact_history(phone)
    print(json.dumps({
        "status": "ok",
        "contact": history["contact"],
        "messages": history["messages"],
    }, indent=2, default=str))


def cmd_update():
    """Update contact."""
    if "--phone" not in sys.argv:
        print(json.dumps({"status": "error", "message": "Requiere --phone"}))
        return
    i = sys.argv.index("--phone")
    phone = sys.argv[i + 1]
    updates = {}
    if "--name" in sys.argv:
        j = sys.argv.index("--name")
        updates["name"] = sys.argv[j + 1]
    if "--status" in sys.argv:
        j = sys.argv.index("--status")
        updates["status"] = sys.argv[j + 1]
    if "--notes" in sys.argv:
        j = sys.argv.index("--notes")
        updates["notes"] = sys.argv[j + 1]
    if not updates:
        print(json.dumps({"status": "error", "message": "Sin campos para actualizar. Usa --name, --status, --notes"}))
        return
    ok = update_contact(phone, updates)
    print(json.dumps({"status": "ok" if ok else "error", "updated": updates}))


def cmd_log_wa():
    """Log a WhatsApp message."""
    if "--phone" not in sys.argv or "--msg" not in sys.argv:
        print(json.dumps({"status": "error", "message": "Requiere --phone y --msg"}))
        return
    i = sys.argv.index("--phone")
    phone = sys.argv[i + 1]
    j = sys.argv.index("--msg")
    content = sys.argv[j + 1]
    direction = "incoming"
    if "--dir" in sys.argv:
        k = sys.argv.index("--dir")
        direction = sys.argv[k + 1]
    ok = log_wa_message(phone, direction, content)
    print(json.dumps({"status": "ok" if ok else "error", "phone": phone, "direction": direction}))


def cmd_summary():
    """Get contacts summary."""
    s = contacts_summary()
    print(json.dumps({"status": "ok", "summary": s}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    cmds = {
        "contacts": cmd_contacts,
        "contact": cmd_contact,
        "search": cmd_contacts,
        "update": cmd_update,
        "log-wa": cmd_log_wa,
        "summary": cmd_summary,
    }
    if cmd in cmds:
        cmds[cmd]()
    else:
        print(f"Comando desconocido: {cmd}")
        sys.exit(1)
