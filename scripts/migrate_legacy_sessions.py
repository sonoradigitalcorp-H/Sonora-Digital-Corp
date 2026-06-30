#!/usr/bin/env python3
"""
Migrate legacy session formats to Neo4j.
Reads session backups from JSON/Markdown and stores them via Neo4j API.
"""
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")
log = logging.getLogger("jarvis.migrate")

PROJECT_DIR = Path(__file__).parent.parent
LEGACY_DIRS = [
    PROJECT_DIR / "backups" / "sessions",
    PROJECT_DIR / "cache" / "sessions",
    Path.home() / ".jarvis" / "sessions",
    Path.home() / ".hermes" / "sessions",
]


def find_legacy_sessions():
    found = []
    for d in LEGACY_DIRS:
        if d.exists():
            for ext in ("*.json", "*.md"):
                found.extend(d.glob(ext))
    return found


def parse_legacy_json(path: Path) -> dict:
    with open(path) as f:
        data = json.load(f)
    if isinstance(data, list):
        messages = data
        title = path.stem
    elif isinstance(data, dict):
        messages = data.get("messages", data.get("conversation", []))
        title = data.get("title", data.get("name", path.stem))
    else:
        raise ValueError(f"Unknown format: {type(data)}")
    return {"title": title, "messages": messages, "source": str(path)}


def parse_legacy_md(path: Path) -> dict:
    with open(path) as f:
        content = f.read()
    lines = content.strip().split("\n")
    title = path.stem
    messages = []
    current_role = None
    current_content = []
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("### ") and ("Usuario" in line or "User" in line or "👤" in line):
            if current_role and current_content:
                messages.append({"role": current_role, "content": "\n".join(current_content).strip()})
            current_role = "user"
            current_content = []
        elif line.startswith("### ") and ("Asistente" in line or "Assistant" in line or "🤖" in line or "JARVIS" in line):
            if current_role and current_content:
                messages.append({"role": current_role, "content": "\n".join(current_content).strip()})
            current_role = "assistant"
            current_content = []
        elif current_role:
            current_content.append(line)
    if current_role and current_content:
        messages.append({"role": current_role, "content": "\n".join(current_content).strip()})
    return {"title": title, "messages": messages, "source": str(path)}


def migrate_session(session_data: dict, neo4j_store):
    title = session_data.get("title", "Migrated Session")
    messages = session_data.get("messages", [])
    if not messages:
        log.warning(f"Empty session: {title}, skipping")
        return False
    session = neo4j_store.create_session(title=title, project="legacy-migration", tags=["migrated"])
    if not session:
        log.error(f"Failed to create session: {title}")
        return False
    sid = session.get("id")
    count = 0
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if content:
            neo4j_store.add_message(sid, role, content, tokens=len(content.split()))
            count += 1
    log.info(f"Migrated '{title}': {count} messages")
    return True


def main():
    from src.core.neo4j_store import add_message, create_session, get_driver, init_schema

    driver = get_driver()
    if not driver:
        log.error("Neo4j is not available. Start Docker services first.")
        sys.exit(1)

    init_schema()
    legacy_files = find_legacy_sessions()
    if not legacy_files:
        log.info("No legacy session files found.")
        return

    class Neo4jStore:
        @staticmethod
        def create_session(**kw):
            return create_session(**kw)
        @staticmethod
        def add_message(*args, **kw):
            return add_message(*args, **kw)

    log.info(f"Found {len(legacy_files)} legacy session files")
    store = Neo4jStore()
    success = 0
    for path in legacy_files:
        try:
            if path.suffix == ".json":
                data = parse_legacy_json(path)
            elif path.suffix == ".md":
                data = parse_legacy_md(path)
            else:
                continue
            if migrate_session(data, store):
                success += 1
        except Exception as e:
            log.error(f"Failed to migrate {path}: {e}")

    log.info(f"Migration complete: {success}/{len(legacy_files)} sessions migrated")


if __name__ == "__main__":
    main()
