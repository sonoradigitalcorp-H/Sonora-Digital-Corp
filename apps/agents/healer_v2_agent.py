#!/usr/bin/env python3
"""HealerAgent V2 — same healing logic but adds Git MCP + Memory MCP.

On successful healing:
1. Commits config changes to git (Git MCP)
2. Stores decision in Memory MCP (knowledge graph)
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "apps" / "jarvis" / "src"))
sys.path.insert(0, str(BASE))

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("healer.v2")


async def main():
    from apps.agents.healer_agent import docker_restart, MAX_RETRIES, publish_decision, save_to_engram
    from apps.agents.hermes_client import HermesClient

    hermes = HermesClient()

    # Read events from Redis Stream
    import redis as redis_lib
    r = redis_lib.Redis(host="localhost", port=6379, db=0, password="sdc2026prod", decode_responses=True)

    try:
        r.xgroup_create("agent:messages", "healer-v2", id="0", mkstream=True)
    except redis_lib.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            log.warning(f"Redis error: {e}")

    events = r.xreadgroup("healer-v2", "healer-v2-1", {"agent:messages": ">"}, count=5, block=3000)

    for stream_name, messages in events or []:
        for msg_id, data in messages:
            if data.get("type") != "container_down":
                r.xack("agent:messages", "healer-v2", msg_id)
                continue

            container = data.get("container", "")
            log.info(f"HealerV2 processing: {container}")

            # Attempt restart
            for attempt in range(1, MAX_RETRIES + 1):
                log.info(f"  Attempt {attempt}/{MAX_RETRIES}")
                import time
                success, status = docker_restart(container)
                if success:
                    log.info(f"  ✅ {container} revived")
                    publish_decision("healing_success", container, "RESTART", True, status)
                    save_to_engram(container, "RESTART", "success")

                    # Git MCP: commit changes
                    from datetime import datetime
                    msg = f"[healer] auto-restart {container} — success"
                    git_result = await hermes.git_commit(message=msg)
                    log.info(f"  Git commit: {git_result}")

                    # Memory MCP: store decision
                    memory_result = await hermes.memory_create_entities([{
                        "name": f"healing-{container}-{datetime.now().timestamp():.0f}",
                        "entityType": "event",
                        "observations": [f"Container {container} restarted successfully on attempt {attempt}"],
                    }])
                    log.info(f"  Memory store: {memory_result}")

                    break
                log.warning(f"  Attempt {attempt} failed")
            else:
                log.error(f"  🔴 {container} critical after {MAX_RETRIES} attempts")
                publish_decision("container_critical", container, "ESCALATE", False, f"Failed after {MAX_RETRIES} attempts")

            r.xack("agent:messages", "healer-v2", msg_id)

    r.close()


if __name__ == "__main__":
    asyncio.run(main())
