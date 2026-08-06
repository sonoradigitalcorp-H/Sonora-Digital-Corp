import os
import json
import urllib.request
from datetime import datetime
from telemetry import log_agent_action

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = os.environ.get("OPENAI_MODEL", "google/gemma-4-26b-a4b-it:free")

class SDC_Client:
    def __init__(self, client_name):
        self.client = client_name
        print(f"[SDC SDK] Inicializado para el tenant: {self.client}")

    def get_context(self, query):
        return f"Contexto recuperado para {self.client}"

    def log_event(self, event_type, payload):
        print(f"[SDC SDK] Log [{event_type}] para {self.client}: {json.dumps(payload)}")

    def call_llm(self, messages, model=None, temperature=0.1, max_tokens=500):
        """Llama a OpenRouter (LLM remoto). Sin modelos locales."""
        model = model or OPENROUTER_MODEL
        key = OPENROUTER_KEY
        if not key:
            log_agent_action("Hermes", self.client, "llm_call", "failure", {"reason": "no OPENROUTER_API_KEY"})
            return {"error": "OPENROUTER_API_KEY not configured"}
        body = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        req = urllib.request.Request(
            OPENROUTER_URL, data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {key}",
                     "HTTP-Referer": "https://sonora-digital-corp.local",
                     "X-Title": "Hermes-SDK",
                     "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read())
            log_agent_action("Hermes", self.client, "llm_call", "success", {"model": model, "tokens": data.get("usage", {})})
            return {"status": "success", "model": model, "content": data["choices"][0]["message"]["content"], "usage": data.get("usage", {})}
        except Exception as e:
            log_agent_action("Hermes", self.client, "llm_call", "failure", {"reason": str(e)})
            return {"error": str(e)}

    def execute_skill(self, skill_name, input_data):
        log_agent_action("Hermes", self.client, f"execute_{skill_name}", "started", input_data)
        result = {"status": "success", "skill": skill_name, "client": self.client}
        log_agent_action("Hermes", self.client, f"execute_{skill_name}", "success", {"result": "ok"})
        return result

    def get_secret(self, secret_name):
        vault_path = f"../08_Security_and_RBAC/Vault/tenants/{self.client.lower().replace(' ', '_')}/{secret_name}.key"
        try:
            with open(os.path.join(os.path.dirname(__file__), vault_path), 'r') as f:
                log_agent_action("Hermes", self.client, "secret_access", "success", {"secret": secret_name})
                return f.read().strip()
        except FileNotFoundError:
            log_agent_action("Hermes", self.client, "secret_access", "failure", {"secret": secret_name, "reason": "not_found"})
            return None

def log_agent_action(agent_name, client, action, status, payload=None):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "agent": agent_name,
        "client_tenant": client,
        "action": action,
        "status": status,
        "payload": payload or {}
    }
    print(json.dumps(log_entry))
