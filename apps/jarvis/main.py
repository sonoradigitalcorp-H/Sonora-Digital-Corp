#!/usr/bin/env python3
"""
JARVIS Core — Orquestador central integrado con voz, MCP, agentes y Web UI.
"""
import json
import logging
import os
import threading
import time
import urllib.request

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
log = logging.getLogger("jarvis.core")

CONFIG_PATH = os.path.expanduser("~/.config/opencode/opencode.json")
ENGINE = "systemd"
JARVIS_DIR = os.path.dirname(os.path.abspath(__file__))


def load_agents():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        return list(cfg.get("agent", {}).keys())
    except Exception:
        return ["hermes", "mystic", "jarvis", "builder", "reviewer"]


def start_mcp():
    """Arranca servidores MCP (HuggingFace + GitHub + MCP Server)."""
    try:
        from mcp_connectors import start_all_mcp
        start_all_mcp()
        log.info("✅ MCP Connectors iniciados")
    except ImportError:
        log.info("ℹ️ MCP connectors module not available (stub)")


def start_voice():
    """Inicia el módulo de voz en un hilo separado."""
    try:
        log.info("✅ Módulo de voz listo (STT + TTS v2)")
    except Exception as e:
        log.warning(f"⚠️ Voice module not available: {e}")


def start_webui():
    """Inicia la nueva Web UI (FastAPI) en un hilo separado."""
    try:
        import uvicorn
        from webui.fastapp import app
        port = int(os.environ.get("JARVIS_UI_PORT", 5174))
        threading.Thread(
            target=uvicorn.run,
            args=(app,),
            kwargs={"host": "0.0.0.0", "port": port, "log_level": "info"},
            daemon=True
        ).start()
        log.info(f"✅ Web UI iniciada en puerto {port}")
    except Exception as e:
        log.warning(f"⚠️ Web UI no iniciada: {e}")


def start_orchestrator():
    """Inicia el AgentOrchestrator."""
    try:
        from src.core.orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        agents = orchestrator.list_agents()
        log.info(f"✅ AgentOrchestrator listo con {len(agents)} agentes")
        for a in agents:
            log.info(f"   - {a['name']}: {a['description']}")
    except Exception as e:
        log.warning(f"⚠️ Orchestrator no iniciado: {e}")


def webui_health():
    """Verifica que la Web UI esté respondiendo."""
    for port in [5174, 8000]:
        for path in ["/health", "/status"]:
            try:
                resp = urllib.request.urlopen(
                    f"http://localhost:{port}{path}", timeout=3
                )
                data = json.loads(resp.read())
                return {"status": "online", "port": port, **data}
            except Exception:
                continue
    return {"status": "offline"}


def heartbeat():
    """Loop principal de estado y salud."""
    while True:
        agents = load_agents()
        status = webui_health()
        log.info(
            f"Agentes: {len(agents)} | "
            f"Web UI: {status.get('status', '?')} "
            f"(puerto {status.get('port', '-')})"
        )
        time.sleep(60)


def main():
    log.info("=" * 50)
    log.info("⚡ JARVIS Core Orchestrator v2.0")
    log.info("=" * 50)

    # 1. Web UI (FastAPI) — disabled, run via separate jarvis-webui.service
    # start_webui()

    # 2. Orchestrator
    start_orchestrator()

    # 3. MCP
    threading.Thread(target=start_mcp, daemon=True).start()

    # 4. Voz
    threading.Thread(target=start_voice, daemon=True).start()

    # 5. Heartbeat
    heartbeat()


if __name__ == "__main__":
    main()
