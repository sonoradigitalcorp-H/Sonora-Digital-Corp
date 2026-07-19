"""
Sonora Notifier — Motor de Notificaciones Multicanal

Escucha el bus de eventos (state/events/events.jsonl o Redis Streams)
y entrega notificaciones via WhatsApp, Telegram o Email según reglas
configurables por tenant y tipo de evento.

Channels:
  - WhatsApp (wacli_mcp)
  - Telegram (python-telegram-bot)
  - Email (SMTP)

Uso:
  python3 -m products.notifier.main          # Inicia API :6200
  python3 -m products.notifier.core --daemon # Inicia worker en background
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent

app = FastAPI(
    title="Sonora Notifier",
    version="1.0.0",
    docs_url="/notifier/docs",
    redoc_url="/notifier/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Models (Pydantic) ───────────────────────────────────────────────

class NotificationRule(BaseModel):
    id: str = ""
    tenant: str = "default"
    event_type: str = ""
    channel: str = "whatsapp"  # whatsapp, telegram, email
    template: str = "Evento: {{event_type}} acaba de ocurrir."
    recipients: list[str] = []
    enabled: bool = True

class NotificationLog(BaseModel):
    id: str
    rule_id: str
    tenant: str
    event_type: str
    channel: str
    recipient: str
    status: str  # queued, sent, failed
    error: str = ""
    delivered_at: str = ""
    created_at: str = ""


# ─── In-memory store (replace with DB) ─────────────────────────────

RULES_FILE = REPO / "state" / "notifier" / "rules.json"
LOG_FILE = REPO / "state" / "notifier" / "log.jsonl"

def _load_rules() -> list[dict]:
    if not RULES_FILE.exists():
        RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
        default = [
            {
                "id": "rule-001",
                "tenant": "default",
                "event_type": "whatsapp:message:received",
                "channel": "telegram",
                "template": "📩 WhatsApp: {{from}}: {{text}}",
                "recipients": ["admin"],
                "enabled": True,
            },
            {
                "id": "rule-002",
                "tenant": "default",
                "event_type": "delivery:completed",
                "channel": "whatsapp",
                "template": "✅ ¡Tu pedido está listo! {{delivery_url}}",
                "recipients": [],
                "enabled": True,
            },
            {
                "id": "rule-003",
                "tenant": "default",
                "event_type": "onboarding:completed",
                "channel": "whatsapp",
                "template": "🎉 ¡Bienvenido {{client_name}}! Tienes {{tokens_bonus}} tokens de regalo.",
                "recipients": [],
                "enabled": True,
            },
        ]
        with open(RULES_FILE, "w") as f:
            json.dump(default, f, indent=2, ensure_ascii=False)
        return default
    try:
        with open(RULES_FILE) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_rules(rules: list[dict]) -> None:
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RULES_FILE, "w") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)

def _log_delivery(entry: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Rules API ───────────────────────────────────────────────────────

@app.get("/notifier/rules")
def list_rules(tenant: str = ""):
    rules = _load_rules()
    if tenant:
        rules = [r for r in rules if r.get("tenant") == tenant]
    return {"rules": rules, "total": len(rules)}

@app.post("/notifier/rules")
def create_rule(rule: NotificationRule):
    rules = _load_rules()
    if not rule.id:
        rule.id = f"rule-{len(rules) + 1:04d}"
    rules.append(rule.model_dump())
    _save_rules(rules)
    return {"ok": True, "id": rule.id}

@app.delete("/notifier/rules/{rule_id}")
def delete_rule(rule_id: str):
    rules = _load_rules()
    new_rules = [r for r in rules if r.get("id") != rule_id]
    if len(new_rules) == len(rules):
        raise HTTPException(404, f"Rule {rule_id} not found")
    _save_rules(new_rules)
    return {"ok": True, "deleted": rule_id}

@app.get("/notifier/log")
def delivery_log(limit: int = 50, tenant: str = ""):
    if not LOG_FILE.exists():
        return {"entries": [], "total": 0}
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    if not tenant or entry.get("tenant") == tenant:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue
    return {"entries": entries[-limit:], "total": len(entries)}

@app.get("/notifier/stats")
def stats():
    rules = _load_rules()
    total_rules = len(rules)
    enabled = sum(1 for r in rules if r.get("enabled"))
    return {
        "rules": total_rules,
        "enabled": enabled,
        "channels": list({r.get("channel") for r in rules}),
        "tenants": list({r.get("tenant") for r in rules}),
    }


# ─── Health ─────────────────────────────────────────────────────────

@app.get("/notifier/health")
def health():
    return {
        "status": "ok",
        "rules_file": str(RULES_FILE),
        "rules_exist": RULES_FILE.exists(),
        "log_exists": LOG_FILE.exists(),
    }


# ─── Direct launch ─────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("NOTIFIER_PORT", "6200"))
    uvicorn.run("products.notifier.main:app", host="0.0.0.0", port=port, reload=False)
