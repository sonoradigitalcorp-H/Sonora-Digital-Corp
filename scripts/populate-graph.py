#!/usr/bin/env python3
"""Knowledge Graph — pobla Neo4j desde eventos, specs, ADRs, fleet.yml [FR31-FR34]"""
import json
import os
import sys
import yaml
import subprocess
import urllib.request
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent
EVENTS_FILE = REPO / "state" / "events" / "events.jsonl"
NEO4J_URL = os.environ.get("NEO4J_URL", "http://127.0.0.1:7474")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASS = os.environ.get("NEO4J_PASS", "sdc2026prod")


def neo4j_query(cypher, params=None):
    """Ejecuta query Cypher via REST API"""
    url = f"{NEO4J_URL}/db/neo4j/tx/commit"
    payload = {"statements": [{"statement": cypher, "parameters": params or {}}]}
    auth = f"{NEO4J_USER}:{NEO4J_PASS}"
    b64 = __import__("base64").b64encode(auth.encode()).decode()

    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Basic {b64}",
            "Accept": "application/json"
        },
        method="POST"
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except Exception as e:
        print(f"Neo4j query failed: {e}", file=sys.stderr)
        return None


def create_constraints():
    """Crea constraints de unicidad"""
    constraints = [
        "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Feature) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Spec) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (a:ADR) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (ag:Agent) REQUIRE ag.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (sv:Service) REQUIRE sv.name IS UNIQUE",
        "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Decision) REQUIRE d.id IS UNIQUE",
    ]
    for cypher in constraints:
        result = neo4j_query(cypher)
        if result:
            print(f"  Constraint created: {cypher.split(' ')[-1]}", file=sys.stderr)


def populate_from_events():
    """Crea nodos y relaciones desde el event bus"""
    if not EVENTS_FILE.exists():
        print("  No events file found", file=sys.stderr)
        return 0

    count = 0
    with open(EVENTS_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                evt = json.loads(line)
                event_type = evt.get("event", "")
                subject = evt.get("subject", {})
                source = evt.get("source", {})

                # Create nodes based on event type
                if event_type.startswith("spec."):
                    cypher = (
                        "MERGE (s:Spec {id: $id}) "
                        "SET s.name = $name, s.updated = $ts"
                    )
                    neo4j_query(cypher, {
                        "id": subject.get("id", ""),
                        "name": subject.get("id", ""),
                        "ts": evt.get("timestamp", "")
                    })
                    count += 1

                elif event_type.startswith("module."):
                    # Create module node and link to spec
                    module_id = subject.get("id", "")
                    spec_id = "SPEC-20260703-A"
                    cypher = (
                        "MERGE (m:Module {id: $id}) "
                        "SET m.name = $name, m.status = $status"
                    )
                    neo4j_query(cypher, {
                        "id": module_id,
                        "name": module_id,
                        "status": "completed" if "completed" in event_type else "active"
                    })
                    # Link to spec
                    link = (
                        "MATCH (s:Spec {id: $spec_id}) "
                        "MATCH (m:Module {id: $module_id}) "
                        "MERGE (s)-[:HAS_MODULE]->(m)"
                    )
                    neo4j_query(link, {"spec_id": spec_id, "module_id": module_id})
                    count += 1

                elif event_type.startswith("agent."):
                    agent_name = source.get("agent", "unknown")
                    cypher = (
                        "MERGE (a:Agent {name: $name}) "
                        "SET a.last_seen = $ts"
                    )
                    neo4j_query(cypher, {
                        "name": agent_name,
                        "ts": evt.get("timestamp", "")
                    })
                    count += 1

            except Exception:
                pass

    return count


def populate_from_specs():
    """Lee SPEC-*.md y crea nodos Spec"""
    count = 0
    for spec_file in sorted((REPO / "process" / "completed").rglob("SPEC-*.md")):
        spec_id = spec_file.stem
        cypher = (
            "MERGE (s:Spec {id: $id}) "
            "SET s.path = $path, s.updated = $ts"
        )
        neo4j_query(cypher, {
            "id": spec_id,
            "path": str(spec_file.relative_to(REPO)),
            "ts": datetime.now().isoformat()
        })
        count += 1
    return count


def populate_from_adrs():
    """Lee ADR-*.md y crea nodos ADR"""
    count = 0
    for adr_file in sorted((REPO / "process" / "completed").rglob("ADR-*.md")):
        adr_id = adr_file.stem
        cypher = (
            "MERGE (a:ADR {id: $id}) "
            "SET a.path = $path"
        )
        neo4j_query(cypher, {
            "id": adr_id,
            "path": str(adr_file.relative_to(REPO))
        })
        count += 1
    return count


def populate_from_fleet():
    """Lee fleet.yml y crea nodos Service"""
    fleet = REPO / "fleet.yml"
    if not fleet.exists():
        return 0

    with open(fleet) as f:
        data = yaml.safe_load(f)

    count = 0
    for svc in data.get("services", []):
        name = svc.get("name", "unknown")
        cypher = (
            "MERGE (s:Service {name: $name}) "
            "SET s.port = $port, s.protocol = $protocol, s.machine = $machine"
        )
        neo4j_query(cypher, {
            "name": name,
            "port": str(svc.get("port", "")),
            "protocol": svc.get("protocol", ""),
            "machine": svc.get("machine", "")
        })
        count += 1
    return count


def main():
    print("populate-graph: Starting Neo4j population...", file=sys.stderr)

    dry_run = "--dry-run" in sys.argv
    if dry_run:
        print("DRY RUN: skipping Neo4j writes", file=sys.stderr)

    # Step 1: Create constraints
    print("\n1. Creating constraints...", file=sys.stderr)
    if not dry_run:
        create_constraints()

    # Step 2: Populate from events
    print("\n2. Populating from events...", file=sys.stderr)
    if not dry_run:
        n = populate_from_events()
        print(f"   {n} nodes from events", file=sys.stderr)

    # Step 3: Populate from specs
    print("\n3. Populating from specs...", file=sys.stderr)
    if not dry_run:
        n = populate_from_specs()
        print(f"   {n} specs created", file=sys.stderr)

    # Step 4: Populate from ADRs
    print("\n4. Populating from ADRs...", file=sys.stderr)
    if not dry_run:
        n = populate_from_adrs()
        print(f"   {n} ADRs created", file=sys.stderr)

    # Step 5: Populate from fleet.yml
    print("\n5. Populating from fleet.yml...", file=sys.stderr)
    if not dry_run:
        n = populate_from_fleet()
        print(f"   {n} services created", file=sys.stderr)

    # Emit event
    if not dry_run:
        try:
            subprocess.run(
                [sys.executable, str(REPO / "scripts" / "emit-event.py"),
                 "--event", "graph.populated",
                 "--kernel", "knowledge",
                 "--agent", "populate-graph",
                 "--subject-type", "graph",
                 "--subject-id", "neo4j",
                 "--payload", json.dumps({
                     "from_events": True,
                     "from_specs": True,
                     "from_adrs": True,
                     "from_fleet": True
                 })],
                capture_output=True, timeout=5
            )
        except Exception:
            pass

    print("\nDone!", file=sys.stderr)


if __name__ == "__main__":
    main()
