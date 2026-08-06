#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STATE_DIR="$SCRIPT_DIR/state"
LOGS_DIR="$STATE_DIR/logs"
SKILLS_LOG="$LOGS_DIR/skills/capture-knowledge.log"
EVENTS_FILE="$LOGS_DIR/events.jsonl"
ENGRAM_DB="$STATE_DIR/engram.db"
FALLBACK_FILE="$STATE_DIR/knowledge-fallback.jsonl"
MAX_RETRIES=3

mkdir -p "$LOGS_DIR/skills"

log() {
  local level="$1" msg="$2"
  echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] [$level] $msg" >> "$SKILLS_LOG"
}

emit_event() {
  local event="$1"
  echo "$event" >> "$EVENTS_FILE"
  log "INFO" "Emitted event: $(echo "$event" | python3 -c 'import sys,json; print(json.loads(sys.stdin.read()).get("type","unknown"))')"
}

engram_store() {
  local spec_id="$1" tag="$2" summary="$3" context="$4" timestamp="$5"
  export ENGRAM_DB
  export SPEC_ID="$spec_id"
  export TAG="$tag"
  export SUMMARY="$summary"
  export CONTEXT="$context"
  export TIMESTAMP="$timestamp"
  python3 -c '
import os, sqlite3, sys
db = os.environ["ENGRAM_DB"]
for attempt in range(3):
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(
            "INSERT INTO memories (spec_id, tag, summary, context, timestamp) VALUES (?, ?, ?, ?, ?)",
            (os.environ["SPEC_ID"], os.environ["TAG"], os.environ["SUMMARY"], os.environ["CONTEXT"], os.environ["TIMESTAMP"])
        )
        asset_id = c.lastrowid
        conn.commit()
        conn.close()
        print(asset_id)
        sys.exit(0)
    except Exception as e:
        if attempt < 2:
            import time; time.sleep(0.1)
        else:
            print(f"ENGRAM_RETRY_EXHAUSTED:{e}", file=sys.stderr)
            sys.exit(1)
' 2>> "$SKILLS_LOG" || {
    log "ERROR" "Engram write failed after $MAX_RETRIES retries"
    echo "$summary" >> "$FALLBACK_FILE"
    log "WARN" "Written to fallback: $FALLBACK_FILE"
    echo "0"
  }
}

qdrant_index() {
  local spec_id="$1" tag="$2" summary="$3" context="$4" timestamp="$5"
  export SPEC_ID="$spec_id"
  export TAG="$tag"
  export SUMMARY="$summary"
  export CONTEXT="$context"
  export TIMESTAMP="$timestamp"
    python3 -c '
import os, uuid, sys
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import PointStruct
    client = QdrantClient(host="localhost", port=6333)
    try:
        client.get_collection("knowledge")
    except Exception:
        try:
            client.create_collection("knowledge", vectors_config={"size": 384, "distance": "Cosine"})
        except Exception:
            pass
    point = PointStruct(
        id=str(uuid.uuid4()),
        vector=[0.0]*384,
        payload={
            "spec_id": os.environ["SPEC_ID"],
            "tag": os.environ["TAG"],
            "summary": os.environ["SUMMARY"],
            "context": os.environ["CONTEXT"],
            "timestamp": os.environ["TIMESTAMP"]
        }
    )
    client.upsert("knowledge", points=[point])
    print("QDRANT_OK")
except ImportError:
    print("QDRANT_UNAVAILABLE")
    sys.exit(1)
except Exception as e:
    print(f"QDRANT_ERROR:{e}", file=sys.stderr)
    sys.exit(1)
' >> "$SKILLS_LOG" 2>&1
}

neo4j_store() {
  local spec_id="$1" tag="$2" summary="$3" context="$4" timestamp="$5"
  export SPEC_ID="$spec_id"
  export TAG="$tag"
  export SUMMARY="$summary"
  export CONTEXT="$context"
  export TIMESTAMP="$timestamp"
  python3 -c '
import os, sys
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://localhost:7687", connection_timeout=3)
    driver.verify_connectivity()
    with driver.session() as session:
        result = session.run(
            "MERGE (k:Knowledge {spec_id: $spec_id}) SET k.tag = $tag, k.summary = $summary, k.context = $context, k.timestamp = $timestamp RETURN k.spec_id",
            spec_id=os.environ["SPEC_ID"],
            tag=os.environ["TAG"],
            summary=os.environ["SUMMARY"],
            context=os.environ["CONTEXT"],
            timestamp=os.environ["TIMESTAMP"]
        )
        print(f"NEO4J_OK:{result.single()}")
    driver.close()
except Exception:
    sys.exit(1)
' >> "$SKILLS_LOG" 2>&1
}

# === MAIN ===
log "INFO" "=== knowledge-sync started ==="

# 1. Read last 50 lines of events
if [ ! -f "$EVENTS_FILE" ]; then
  touch "$EVENTS_FILE"
  log "WARN" "events.jsonl not found, created empty"
fi

RECENT_EVENTS=$(tail -n 50 "$EVENTS_FILE" 2>/dev/null || true)

if [ -z "$RECENT_EVENTS" ]; then
  log "INFO" "No events to process"
else
  echo "$RECENT_EVENTS" | while IFS= read -r line; do
    [ -z "$line" ] && continue

    event_type=$(echo "$line" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('type',''))" 2>/dev/null || true)
    [ "$event_type" != "skill_execution" ] && continue

    payload=$(echo "$line" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(json.dumps(d.get('payload',{})))" 2>/dev/null || true)
    [ -z "$payload" ] && continue

    spec_id=$(echo "$payload" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('spec_id','unknown'))" 2>/dev/null || echo "unknown")
    tag=$(echo "$payload" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('tag','general'))" 2>/dev/null || echo "general")
    summary=$(echo "$payload" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('summary',''))" 2>/dev/null || echo "")
    context=$(echo "$payload" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('context',''))" 2>/dev/null || echo "")
    timestamp=$(echo "$payload" | python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('timestamp',''))" 2>/dev/null || echo "")
    [ -z "$timestamp" ] && timestamp=$(date '+%Y-%m-%dT%H:%M:%S%z')

    # Store to Engram (always)
    log "INFO" "Storing to Engram: spec_id=$spec_id tag=$tag"
    asset_id=$(engram_store "$spec_id" "$tag" "$summary" "$context" "$timestamp")
    log "INFO" "Engram asset_id=$asset_id"

    # Qdrant indexing (optional)
    if qdrant_result=$(qdrant_index "$spec_id" "$tag" "$summary" "$context" "$timestamp"); then
      log "INFO" "Qdrant index OK: $qdrant_result"
    else
      log "WARN" "Qdrant unavailable, continuing with Engram only"
    fi

    # Neo4j node creation (optional)
    if neo4j_result=$(neo4j_store "$spec_id" "$tag" "$summary" "$context" "$timestamp"); then
      log "INFO" "Neo4j node created: $neo4j_result"
    else
      log "WARN" "Neo4j unavailable, continuing with Engram only"
    fi

    # Emit knowledge_stored event
    emit_event "$(python3 -c "
import json
event = {
    'type': 'knowledge_stored',
    'asset_id': $asset_id,
    'spec_id': '$spec_id',
    'tag': '$tag',
    'timestamp': '$(date '+%Y-%m-%dT%H:%M:%S%z')'
}
print(json.dumps(event))
")"

    log "INFO" "Processed skill_execution: spec_id=$spec_id"
  done
fi

log "INFO" "=== knowledge-sync completed ==="
