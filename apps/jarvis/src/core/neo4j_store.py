"""
JARVIS Neo4j Connector — Graph Database for persistent session storage.
Connects to Neo4j when available, falls back to in-memory storage.
"""

import logging
import os
import uuid
from datetime import datetime, timezone

log = logging.getLogger("jarvis.neo4j")

NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "jarvis2026")

_driver = None


def get_driver():
    """Get Neo4j driver (lazy initialization)."""
    global _driver
    if _driver is not None:
        return _driver

    try:
        from neo4j import GraphDatabase

        _driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        # Test connection
        with _driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single():
                log.info(f"Connected to Neo4j at {NEO4J_URI}")
                return _driver
    except Exception as e:
        log.warning(f"Neo4j not available: {e}")
        _driver = None
        return None

    return None


def test_connection() -> bool:
    """Test Neo4j connectivity (alias for is_available)."""
    return is_available()


def is_available() -> bool:
    """Check if Neo4j is available."""
    driver = get_driver()
    return driver is not None


def close():
    """Close Neo4j connection."""
    global _driver
    if _driver:
        _driver.close()
        _driver = None


# ===================== Memory Operations =====================


def save_memory(key: str, value: str) -> bool:
    """Save a key-value memory to Neo4j."""
    driver = get_driver()
    if not driver:
        return False

    try:
        with driver.session() as session:
            session.run(
                """
                MERGE (m:Memory {key: $key})
                SET m.value = $value,
                    m.timestamp = timestamp()
                """,
                key=key,
                value=value,
            )
            return True
    except Exception as e:
        log.warning(f"Neo4j save_memory error: {e}")
        return False


def get_memory(key: str) -> str | None:
    """Retrieve a value by key from Neo4j Memory nodes."""
    driver = get_driver()
    if not driver:
        return None

    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (m:Memory {key: $key}) RETURN m.value as value LIMIT 1", key=key
            )
            record = result.single()
            if record:
                return record["value"]
    except Exception as e:
        log.warning(f"Neo4j get_memory error: {e}")

    return None


def search_memory(text: str, limit: int = 10) -> list[dict]:
    """Search memories by key or value substring."""
    driver = get_driver()
    if not driver:
        return []

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (m:Memory)
                WHERE m.key CONTAINS $q OR m.value CONTAINS $q
                RETURN m.key as key, m.value as value, m.timestamp as timestamp
                ORDER BY m.timestamp DESC
                LIMIT $limit
                """,
                q=text,
                limit=limit,
            )
            return [dict(record) for record in result]
    except Exception as e:
        log.warning(f"Neo4j search_memory error: {e}")

    return []


def memory_stats() -> dict:
    """Get memory storage statistics."""
    driver = get_driver()
    if not driver:
        return {"status": "unavailable"}

    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (m:Memory)
                RETURN count(m) as total,
                       count(DISTINCT m.key) as unique_keys
                """)
            record = result.single()
            return {
                "total_nodes": record["total"] if record else 0,
                "unique_keys": record["unique_keys"] if record else 0,
            }
    except Exception as e:
        log.warning(f"Neo4j memory_stats error: {e}")
        return {"error": str(e)}


# ===================== Session Operations =====================


def create_session(
    session_id: str = None,
    title: str = "Nueva sesión",
    project: str = None,
    tags: list = None,
) -> dict | None:
    """Create a new session in Neo4j."""
    driver = get_driver()
    if not driver:
        return None

    sid = session_id or str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    try:
        with driver.session() as session:
            result = session.run(
                """
                CREATE (s:Session {
                    id: $id,
                    title: $title,
                    pinned: false,
                    project: $project,
                    tags: $tags,
                    archived: false,
                    created_at: datetime($created_at),
                    updated_at: datetime($updated_at),
                    token_count: 0
                })
                RETURN s
                """,
                id=sid,
                title=title,
                project=project,
                tags=tags or [],
                created_at=now,
                updated_at=now,
            )
            record = result.single()
            if record:
                return dict(record["s"])
    except Exception as e:
        log.warning(f"Neo4j create_session error: {e}")

    return None


def get_session(session_id: str) -> dict | None:
    """Get a session with all messages from Neo4j."""
    driver = get_driver()
    if not driver:
        return None

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (s:Session {id: $id})
                OPTIONAL MATCH (s)-[:CONTAINS]->(m:Message)
                 RETURN s, collect(m) as messages
                 ORDER BY m.timestamp ASC
                """,
                id=session_id,
            )
            record = result.single()
            if record:
                session_data = dict(record["s"])
                session_data["messages"] = [dict(m) for m in record["messages"] if m]
                return session_data
    except Exception as e:
        log.warning(f"Neo4j get_session error: {e}")

    return None


def list_sessions(
    pinned: bool = None,
    project: str = None,
    tag: str = None,
    archived: bool = False,
    limit: int = 50,
) -> list[dict]:
    """List sessions from Neo4j with optional filters."""
    driver = get_driver()
    if not driver:
        return []

    query = "MATCH (s:Session) WHERE s.archived = $archived"
    params = {"archived": archived}

    if pinned is not None:
        query += " AND s.pinned = $pinned"
        params["pinned"] = pinned

    if project:
        query += " AND s.project = $project"
        params["project"] = project

    if tag:
        query += " AND $tag IN s.tags"
        params["tag"] = tag

    query += " RETURN s ORDER BY s.pinned DESC, s.updated_at DESC LIMIT $limit"
    params["limit"] = limit

    try:
        with driver.session() as session:
            result = session.run(query, **params)
            sessions_data = []
            for record in result:
                s = dict(record["s"])
                if "messages" in s:
                    del s["messages"]
                sessions_data.append(s)
            return sessions_data
    except Exception as e:
        log.warning(f"Neo4j list_sessions error: {e}")

    return []


def add_message(
    session_id: str, role: str, content: str, tokens: int = 0
) -> dict | None:
    """Add a message to a session in Neo4j."""
    driver = get_driver()
    if not driver:
        return None

    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    try:
        with driver.session() as session:
            # Create message and link to session
            result = session.run(
                """
                MATCH (s:Session {id: $session_id})
                CREATE (m:Message {
                    id: $msg_id,
                    role: $role,
                    content: $content,
                    tokens: $tokens,
                    timestamp: datetime($now)
                })
                CREATE (s)-[:CONTAINS]->(m)
                SET s.updated_at = datetime($now),
                    s.token_count = coalesce(s.token_count, 0) + $tokens
                RETURN m
                """,
                session_id=session_id,
                msg_id=msg_id,
                role=role,
                content=content,
                tokens=tokens,
                now=now,
            )
            record = result.single()
            if record:
                return dict(record["m"])
    except Exception as e:
        log.warning(f"Neo4j add_message error: {e}")

    return None


def search_sessions(query: str) -> list[dict]:
    """Full-text search in sessions."""
    driver = get_driver()
    if not driver:
        return []

    try:
        with driver.session() as session:
            result = session.run(
                """
                CALL db.index.fulltext.queryNodes("session_ft", $query)
                YIELD node, score
                RETURN node
                LIMIT 20
                """,
                query=query,
            )
            return [dict(record["node"]) for record in result]
    except Exception as e:
        log.warning(f"Neo4j search error: {e}")

    return []


def toggle_pin(session_id: str) -> bool | None:
    """Toggle pinned status of a session."""
    driver = get_driver()
    if not driver:
        return None

    try:
        with driver.session() as session:
            result = session.run(
                """
                MATCH (s:Session {id: $id})
                SET s.pinned = NOT coalesce(s.pinned, false),
                    s.updated_at = datetime()
                RETURN s.pinned as pinned
                """,
                id=session_id,
            )
            record = result.single()
            if record:
                return record["pinned"]
    except Exception as e:
        log.warning(f"Neo4j toggle_pin error: {e}")

    return None


def delete_session(session_id: str) -> bool:
    """Delete a session and its messages."""
    driver = get_driver()
    if not driver:
        return False

    try:
        with driver.session() as session:
            session.run(
                """
                MATCH (s:Session {id: $id})
                OPTIONAL MATCH (s)-[:CONTAINS]->(m:Message)
                DETACH DELETE s, m
                """,
                id=session_id,
            )
            return True
    except Exception as e:
        log.warning(f"Neo4j delete_session error: {e}")

    return False


def init_schema():
    """Initialize Neo4j schema (constraints, indexes)."""
    driver = get_driver()
    if not driver:
        log.warning("Cannot init schema: Neo4j not available")
        return False

    cypher_commands = [
        "CREATE CONSTRAINT session_id_unique IF NOT EXISTS FOR (s:Session) REQUIRE s.id IS UNIQUE",
        "CREATE CONSTRAINT message_id_unique IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE",
        "CREATE CONSTRAINT contact_phone_unique IF NOT EXISTS FOR (c:Contact) REQUIRE c.phone IS UNIQUE",
        "CREATE INDEX session_pinned IF NOT EXISTS FOR (s:Session) ON (s.pinned)",
        "CREATE INDEX session_project IF NOT EXISTS FOR (s:Session) ON (s.project)",
        "CREATE INDEX session_archived IF NOT EXISTS FOR (s:Session) ON (s.archived)",
        "CREATE INDEX session_updated IF NOT EXISTS FOR (s:Session) ON (s.updated_at)",
        "CREATE INDEX contact_name IF NOT EXISTS FOR (c:Contact) ON (c.name)",
        "CREATE INDEX contact_status IF NOT EXISTS FOR (c:Contact) ON (c.status)",
        "CREATE FULLTEXT INDEX session_ft IF NOT EXISTS FOR (s:Session) ON EACH [s.title, s.project]",
        "CREATE FULLTEXT INDEX contact_ft IF NOT EXISTS FOR (c:Contact) ON EACH [c.name, c.notes]",
    ]

    try:
        with driver.session() as session:
            for cmd in cypher_commands:
                try:
                    session.run(cmd)
                except Exception as e:
                    log.warning(f"Schema command failed: {cmd[:50]}... {e}")

        log.info("Neo4j schema initialized (constraints + indexes)")
        return True

    except Exception as e:
        log.warning(f"Schema init error: {e}")
        return False


# ── CRM: Contact Management ──────────────────────────────────────────────────


def create_contact(
    phone: str,
    name: str = "",
    source: str = "whatsapp",
    status: str = "lead",
    notes: str = "",
) -> dict | None:
    """Create or update a contact in Neo4j."""
    driver = get_driver()
    if not driver:
        return None
    try:
        with driver.session() as s:
            result = s.run(
                """
                MERGE (c:Contact {phone: $phone})
                ON CREATE SET
                    c.id = randomUUID(),
                    c.name = $name,
                    c.source = $source,
                    c.status = $status,
                    c.notes = $notes,
                    c.first_seen = datetime(),
                    c.last_seen = datetime(),
                    c.message_count = 0
                ON MATCH SET
                    c.name = CASE WHEN $name <> '' THEN $name ELSE c.name END,
                    c.last_seen = datetime(),
                    c.status = CASE WHEN c.status = 'lead' AND $status <> 'lead'
                                    THEN $status ELSE c.status END
                RETURN c {.id, .name, .phone, .source, .status, .notes,
                          .first_seen, .last_seen, .message_count}
            """,
                phone=phone,
                name=name,
                source=source,
                status=status,
                notes=notes,
            )
            record = result.single()
            return dict(record["c"]) if record else None
    except Exception as e:
        log.warning(f"create_contact error: {e}")
        return None


def get_contact(phone: str) -> dict | None:
    """Get a contact by phone number."""
    driver = get_driver()
    if not driver:
        return None
    try:
        with driver.session() as s:
            result = s.run(
                """
                MATCH (c:Contact {phone: $phone})
                OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:WaMessage)
                WITH c, count(m) as msg_count
                RETURN c {.id, .name, .phone, .source, .status, .notes,
                          .first_seen, .last_seen, .message_count},
                       msg_count as actual_message_count
            """,
                phone=phone,
            )
            record = result.single()
            if not record:
                return None
            contact = dict(record["c"])
            contact["actual_messages"] = record["actual_message_count"]
            return contact
    except Exception as e:
        log.warning(f"get_contact error: {e}")
        return None


def search_contacts(query: str = "", status: str = "") -> list[dict]:
    """Search contacts by name/phone/notes, optionally filter by status."""
    driver = get_driver()
    if not driver:
        return []
    try:
        with driver.session() as s:
            if query:
                result = s.run(
                    """
                    CALL db.index.fulltext.queryNodes('contact_ft', $query)
                    YIELD node as c, score
                    OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:WaMessage)
                    WITH c, count(m) as msg_count, score
                    ORDER BY score DESC
                    RETURN c {.id, .name, .phone, .source, .status, .notes,
                              .first_seen, .last_seen, .message_count},
                           msg_count as actual_message_count
                    LIMIT 20
                """,
                    query=query,
                )
            elif status:
                result = s.run(
                    """
                    MATCH (c:Contact {status: $status})
                    OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:WaMessage)
                    WITH c, count(m) as msg_count
                    ORDER BY c.last_seen DESC
                    RETURN c {.id, .name, .phone, .source, .status, .notes,
                              .first_seen, .last_seen, .message_count},
                           msg_count as actual_message_count
                """,
                    status=status,
                )
            else:
                result = s.run("""
                    MATCH (c:Contact)
                    OPTIONAL MATCH (c)-[:HAS_MESSAGE]->(m:WaMessage)
                    WITH c, count(m) as msg_count
                    ORDER BY c.last_seen DESC
                    RETURN c {.id, .name, .phone, .source, .status, .notes,
                              .first_seen, .last_seen, .message_count},
                           msg_count as actual_message_count
                    LIMIT 50
                """)
            return [
                dict(r["c"]) | {"actual_messages": r["actual_message_count"]}
                for r in result
            ]
    except Exception as e:
        log.warning(f"search_contacts error: {e}")
        return []


def update_contact(phone: str, updates: dict) -> bool:
    """Update contact fields. Keys: name, status, notes, tags, source."""
    driver = get_driver()
    if not driver:
        return False
    allowed = {"name", "status", "notes", "tags", "source"}
    sets = []
    params = {"phone": phone}
    for k, v in updates.items():
        if k in allowed:
            sets.append(f"c.{k} = ${k}")
            params[k] = v
    if not sets:
        return False
    sets.append("c.last_seen = datetime()")
    try:
        with driver.session() as s:
            result = s.run(
                f"MATCH (c:Contact {{phone: $phone}}) SET {', '.join(sets)} RETURN c",
                **params,
            )
            return result.single() is not None
    except Exception as e:
        log.warning(f"update_contact error: {e}")
        return False


def log_wa_message(
    phone: str, direction: str, content: str, session_id: str = ""
) -> bool:
    """Log a WhatsApp message in Neo4j linked to a Contact.
    direction: 'incoming' | 'outgoing'
    """
    driver = get_driver()
    if not driver:
        return False
    try:
        with driver.session() as s:
            # Create contact if not exists, increment counter
            s.run(
                """
                MERGE (c:Contact {phone: $phone})
                ON CREATE SET
                    c.id = randomUUID(),
                    c.name = '',
                    c.source = 'whatsapp',
                    c.status = 'lead',
                    c.first_seen = datetime(),
                    c.last_seen = datetime(),
                    c.message_count = 1
                ON MATCH SET
                    c.last_seen = datetime(),
                    c.message_count = coalesce(c.message_count, 0) + 1
            """,
                phone=phone,
            )

            # Create message and link to contact
            s.run(
                """
                MATCH (c:Contact {phone: $phone})
                CREATE (m:WaMessage {
                    id: randomUUID(),
                    direction: $direction,
                    content: $content,
                    session_id: $session_id,
                    created_at: datetime()
                })
                CREATE (c)-[:HAS_MESSAGE {at: datetime()}]->(m)
            """,
                phone=phone,
                direction=direction,
                content=content,
                session_id=session_id,
            )
            return True
    except Exception as e:
        log.warning(f"log_wa_message error: {e}")
        return False


def get_contact_history(phone: str, limit: int = 50) -> dict:
    """Get full conversation history for a contact."""
    driver = get_driver()
    if not driver:
        return {"contact": None, "messages": []}
    try:
        with driver.session() as s:
            contact = s.run(
                """
                MATCH (c:Contact {phone: $phone})
                RETURN c {.id, .name, .phone, .source, .status, .notes,
                          .first_seen, .last_seen, .message_count}
            """,
                phone=phone,
            ).single()
            if not contact:
                return {"contact": None, "messages": []}

            msgs = s.run(
                """
                MATCH (c:Contact {phone: $phone})-[:HAS_MESSAGE]->(m:WaMessage)
                RETURN m {.id, .direction, .content, .session_id, .created_at}
                ORDER BY m.created_at DESC
                LIMIT $limit
            """,
                phone=phone,
                limit=limit,
            )
            return {
                "contact": dict(contact["c"]),
                "messages": [dict(r["m"]) for r in msgs],
            }
    except Exception as e:
        log.warning(f"get_contact_history error: {e}")
        return {"contact": None, "messages": []}


def contacts_summary() -> dict:
    """Get summary statistics of all contacts."""
    driver = get_driver()
    if not driver:
        return {"total": 0, "by_status": {}}
    try:
        with driver.session() as s:
            total = s.run("MATCH (c:Contact) RETURN count(c) as total").single()[
                "total"
            ]
            by_status = s.run("""
                MATCH (c:Contact)
                RETURN c.status as status, count(c) as count
                ORDER BY count DESC
            """).data()
            return {
                "total": total,
                "by_status": {r["status"]: r["count"] for r in by_status},
            }
    except Exception as e:
        log.warning(f"contacts_summary error: {e}")
        return {"total": 0, "by_status": {}}
