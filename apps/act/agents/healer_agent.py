#!/usr/bin/env python3
"""AgenteHealer — escucha Redis Stream, consulta Neo4j + Ollama, decide.

Flujo:
1. Escucha Redis Stream agent:messages por eventos container_down
2. Consulta Neo4j: que servicios dependen de este container?
3. Consulta Ollama (deepseek-r1:7b): reinicio o escalo?
4. Ejecuta decision
5. Publica resultado a Redis Stream
6. Guarda en Engram

Uso: python3 apps/agents/healer_agent.py [--watch]
"""
import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "apps" / "jarvis" / "src"))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("agent.healer")

REDIS_STREAM = "agent:messages"
CONSUMER_GROUP = "healer-group"
CONSUMER_NAME = "healer-1"
MAX_RETRIES = 3
POLL_SECONDS = 5


def neo4j_query(query: str) -> list:
    """Query Neo4j for dependencies. Returns list of dicts."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver("bolt://localhost:7687")
        with driver.session() as session:
            result = session.run(query)
            records = [dict(r) for r in result]
        driver.close()
        return records
    except Exception as e:
        log.warning(f"Neo4j query failed: {e}")
        return []


def get_dependencies(container: str) -> list[str]:
    """Get services that depend on this container."""
    container_name = container.replace("sdc-", "")
    records = neo4j_query(
        f"MATCH (c:Service {{id: '{container}'}})<-[:DEPENDS_ON]-(d) RETURN d.name as name"
    )
    if not records:
        return []
    return [r.get("name", "") for r in records if r.get("name")]


def check_recent_healing(container: str) -> bool:
    """Check if already attempted recently via Redis history."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis(host="localhost", port=6379, db=0, socket_timeout=3, password="sdc2026prod", decode_responses=True)
        events = r.xrevrange(REDIS_STREAM, count=100)
        r.close()
        for _, data in events:
            if data.get("type") in ("healing_attempt", "healing_success"):
                if data.get("container") == container:
                    return True
        return False
    except Exception:
        return False


def ask_ollama(container: str, status: str, dependencies: list[str], history: str) -> str:
    """Consult Ollama to decide: restart, wait, or escalate."""
    prompt = f"""Eres un agente de operaciones responsable de mantener containers vivos.

Container: {container}
Estado: {status}
Dependencias: {dependencies if dependencies else 'ninguna'}
Historial reciente: {history}

Decide exactamente una de estas opciones:
- RESTART: reiniciar el container ahora
- ESCALATE: notificar a humano, no reiniciar
- WAIT: esperar, no hacer nada

Responde SOLO con la palabra: RESTART, ESCALATE, o WAIT"""

    try:
        from core.llm import ask_local
        result = ask_local(prompt, model="qwen3:4b-64k")
        decision = result.strip().upper()
        log.info(f"Ollama decision for {container}: {decision} (raw: {result[:50]})")
        for valid in ["RESTART", "ESCALATE", "WAIT"]:
            if valid in decision:
                return valid
        return "RESTART"  # default
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return "RESTART"  # fallback seguro


def docker_restart(container: str) -> tuple[bool, str]:
    """Restart container. Returns (success, status)."""
    try:
        subprocess.run(["docker", "restart", container], capture_output=True, timeout=30)
        time.sleep(10)
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        status = result.stdout.strip()
        healthy = "healthy" in status and "Up" in status
        return healthy, status
    except Exception as e:
        return False, str(e)


def publish_decision(event_type: str, container: str, decision: str, success: bool, details: str = ""):
    """Publish result to Redis Stream."""
    try:
        import redis as redis_lib
        r = redis_lib.Redis(host="localhost", port=6379, db=0, socket_timeout=3, password="sdc2026prod", decode_responses=True)
        r.xadd(REDIS_STREAM, {
            "type": event_type,
            "container": container,
            "decision": decision,
            "success": str(success),
            "details": details,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source": "agent.healer",
        }, maxlen=1000)
        r.close()
    except Exception as e:
        log.warning(f"Redis publish error: {e}")


def save_to_engram(container: str, decision: str, result: str):
    """Save learning to Engram for future decisions."""
    try:
        from core.engram import engram
        engram.store(
            content=f"Healing decision for {container}: {decision} -> {result}",
            tags=["healing", container],
            importance=3,
        )
    except Exception as e:
        log.warning(f"Engram error: {e}")


def process_event(data: dict):
    """Process a single container_down event."""
    container = data.get("container", "")
    status = data.get("status", "unknown")
    log.info(f"Processing: {container} ({status})")

    if check_recent_healing(container):
        log.info(f"  {container} already attempted recently — skip")
        return

    # Get dependencies from Neo4j
    deps = get_dependencies(container)
    if deps:
        log.info(f"  Dependencies: {', '.join(deps)}")

    # Consult Ollama
    decision = ask_ollama(container, status, deps, "")

    if decision == "WAIT":
        log.info(f"  Decision: WAIT — no action for {container}")
        publish_decision("healing_skip", container, "WAIT", True, "Agent decided to wait")
        return

    if decision == "ESCALATE":
        log.info(f"  Decision: ESCALATE — notifying for {container}")
        publish_decision("healing_escalated", container, "ESCALATE", False, "Agent decided to escalate")
        publish_decision("container_critical", container, "ESCALATE", False, "Escalated by Healer Agent")
        return

    # RESTART
    for attempt in range(1, MAX_RETRIES + 1):
        log.info(f"  Attempt {attempt}/{MAX_RETRIES}: restarting {container}")
        publish_decision("healing_attempt", container, "RESTART", True, f"Attempt {attempt}")
        success, new_status = docker_restart(container)
        if success:
            log.info(f"  ✅ {container} revived (attempt {attempt}): {new_status}")
            publish_decision("healing_success", container, "RESTART", True, new_status)
            save_to_engram(container, "RESTART", "success")
            return
        log.warning(f"  Attempt {attempt} failed: {new_status}")

    # All attempts failed
    log.error(f"  🔴 {container}: CRITICAL — all {MAX_RETRIES} attempts failed")
    publish_decision("healing_failure", container, "RESTART", False, f"Failed after {MAX_RETRIES} attempts")
    publish_decision("container_critical", container, "ESCALATE", False, f"Failed after {MAX_RETRIES} restart attempts")
    save_to_engram(container, "RESTART", f"failed after {MAX_RETRIES} attempts")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true", help="Loop escuchando Redis Stream")
    args = parser.parse_args()

    try:
        import redis as redis_lib
    except ImportError:
        log.error("redis library not installed. Run: pip install redis")
        sys.exit(1)

    r = redis_lib.Redis(host="localhost", port=6379, db=0, socket_timeout=5, password="sdc2026prod", decode_responses=True)

    # Create consumer group (if not exists)
    try:
        r.xgroup_create(REDIS_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
    except redis_lib.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            log.warning(f"Redis group error: {e}")

    log.info(f"Watching Redis Stream: {REDIS_STREAM} (group: {CONSUMER_GROUP})")

    while True:
        try:
            events = r.xreadgroup(CONSUMER_GROUP, CONSUMER_NAME, {REDIS_STREAM: ">"}, count=10, block=5000)
            if events:
                for stream_name, messages in events:
                    for msg_id, data in messages:
                        decoded = {k.decode() if isinstance(k, bytes) else k:
                                   v.decode() if isinstance(v, bytes) else v
                                   for k, v in data.items()}
                        log.info(f"Received: {decoded.get('type')} for {decoded.get('container')}")
                        if decoded.get("type") == "container_down":
                            process_event(decoded)
                        r.xack(REDIS_STREAM, CONSUMER_GROUP, msg_id)
        except Exception as e:
            log.error(f"Error in main loop: {e}")

        if not args.watch:
            break
        time.sleep(1)

    r.close()


if __name__ == "__main__":
    main()
