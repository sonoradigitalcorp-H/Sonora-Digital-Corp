import json
from datetime import datetime

def log_agent_action(agent_name, client, action, status, payload=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "client_tenant": client,
        "action": action,
        "status": status,
        "payload": payload or {}
    }
    # En producción esto iría a Datadog/Loki, por ahora imprimimos JSON
    print(json.dumps(log_entry))

# Ejemplo de uso: log_agent_action("Hermes", "Aztrotech", "booking_attempt", "success", {"date": "2026-08-10"})
