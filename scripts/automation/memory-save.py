"""
Auto-save session state to Neo4j memory + Qdrant.
Run: every 60min via cron, or at end of each session.
Stores: system state summary, decisions made, what was built, what was fixed.
"""

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
log = logging.getLogger("auto-save")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORE_FILE = BASE_DIR / "state" / "last-session.json"
STATE_DIR = BASE_DIR / "state"
STATE_DIR.mkdir(exist_ok=True)


def get_system_state() -> dict:
    import subprocess
    try:
        free = subprocess.run(["free", "-h"], capture_output=True, text=True)
        uptime = subprocess.run(["uptime"], capture_output=True, text=True)
        docker_ps = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}} {{.Status}}"],
            capture_output=True, text=True
        )
        containers = [l.strip() for l in docker_ps.stdout.split("\n") if l.strip()]
        return {
            "memory": free.stdout.split("\n")[1].split()[0:5] if free.stdout else [],
            "uptime": uptime.stdout.strip() if uptime.stdout else "",
            "containers": containers,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {"error": str(e)}


def save_decision(neo4j, decision_key: str, value: str):
    try:
        neo4j.save_memory(f"decision:{decision_key}", value)
        return True
    except Exception as e:
        log.error(f"Failed to save decision: {e}")
        return False


def save_session_summary(neo4j, summary: str, session_id: str = "cron-auto"):
    try:
        neo4j.save_memory(f"session:{session_id}:{datetime.now().strftime('%Y%m%d_%H%M')}", summary)
        return True
    except Exception as e:
        log.error(f"Failed to save session: {e}")
        return False


def feed_qdrant():
    try:
        from src.core import neo4j_store
        from src.core.rag import rag
        memories = neo4j_store.search_memory("", limit=50)
        count = 0
        for m in memories:
            text = f"{m['key']}: {m['value']}"
            if len(text) > 20:
                rag.store(text, metadata={"source": "auto-save", "type": "memory"})
                count += 1
        log.info(f"Fed {count} memories to Qdrant")
        return count
    except Exception as e:
        log.warning(f"Qdrant feed skipped: {e}")
        return 0


def main():
    from src.core import neo4j_store

    log.info("=== Auto-Save: Saving system state ===")

    state = get_system_state()
    state_file = STATE_DIR / f"state-{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2, default=str)

    containers_up = len(state.get("containers", []))
    container_names = ", ".join(c.split()[0] for c in state.get("containers", []))

    save_decision(neo4j_store, "auto:containers_up", str(containers_up))
    save_decision(neo4j_store, "auto:containers", container_names)
    save_decision(neo4j_store, "auto:memory_used", str(state.get("memory", [])))
    save_session_summary(neo4j_store, f"Auto-save {datetime.now().isoformat()}: {containers_up} containers up")

    log.info(f"State saved: {state_file}")

    qdrant_count = feed_qdrant()
    log.info(f"Qdrant: {qdrant_count} points fed")

    stats = neo4j_store.memory_stats()
    log.info(f"Neo4j memory stats: {stats}")

    return {"status": "ok", "memories": stats, "qdrant": qdrant_count}


if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
