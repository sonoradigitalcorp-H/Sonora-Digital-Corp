"""Neo4j store — REST API via requests (no native driver)."""

import json
import logging
import os
from base64 import b64encode
from datetime import datetime, timezone
from typing import Any, Optional
from urllib.request import Request, urlopen

NEO4J_HTTP = os.environ.get("NEO4J_HTTP", "http://127.0.0.1:7474")
NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASS", "RezBcUz5ufu7AUXg1hZ3")
log = logging.getLogger(__name__)


def _auth() -> str:
    return f"Basic {b64encode(f'{NEO4J_USER}:{NEO4J_PASSWORD}'.encode()).decode()}"


def _post(cypher: str, params: dict = None) -> list[dict]:
    url = f"{NEO4J_HTTP}/db/neo4j/tx/commit"
    body = json.dumps({"statements": [{"statement": cypher, "parameters": params or {}}]}).encode()
    req = Request(url, data=body, headers={
        "Content-Type": "application/json", "Authorization": _auth(), "Accept": "application/json",
    }, method="POST")
    try:
        data = json.loads(urlopen(req, timeout=10).read())
        rows = []
        for r in data.get("results", []):
            cols = r.get("columns", [])
            for d in r.get("data", []):
                row = {cols[i]: d.get("row", [])[i] for i in range(min(len(cols), len(d.get("row", []))))}
                rows.append(row)
        return rows
    except Exception:
        return []


def test_connection() -> bool:
    try:
        return urlopen(Request(f"{NEO4J_HTTP}/", method="GET"), timeout=5).status == 200
    except Exception:
        return False


is_available = test_connection


def get_driver():
    return object() if test_connection() else None


def init_schema():
    for label in ("Spec", "ADR", "Knowledge", "Session", "Contact", "Decision"):
        _post(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE")


def query(cypher: str, params: dict = None) -> list:
    return _post(cypher, params)


def create_node(label: str, properties: dict) -> dict:
    keys = ", ".join(f"{k}: ${k}" for k in properties)
    rows = _post(f"CREATE (n:{label} {{{keys}}}) RETURN id(n) as id, n", properties)
    return rows[0] if rows else {}


def create_relationship(from_id: int, rel_type: str, to_id: int, properties: dict = None) -> dict:
    p = properties or {}
    props = ", ".join(f"{k}: ${k}" for k in p)
    rows = _post(
        f"MATCH (a) WHERE id(a)=$from MATCH (b) WHERE id(b)=$to CREATE (a)-[r:{rel_type} {{{props}}}]->(b) RETURN id(r) as id",
        {"from": from_id, "to": to_id, **p},
    )
    return rows[0] if rows else {}


def find_node(label: str, property_name: str, property_value: str) -> Optional[dict]:
    rows = _post(f"MATCH (n:{label} {{{property_name}: $val}}) RETURN n, id(n) as id", {"val": property_value})
    return rows[0] if rows else None


def upsert_node(label: str, match_props: dict, set_props: dict = None) -> dict:
    match_expr = ", ".join(f"n.{k} = ${k}" for k in match_props)
    sp = set_props or {}
    set_clause = "SET " + ", ".join(f"n.{k} = ${k}" for k in sp) if sp else ""
    rows = _post(f"MERGE (n:{label} {{{match_expr}}}) {set_clause} RETURN n, id(n) as id", {**match_props, **sp})
    return rows[0] if rows else {}


def delete_all() -> int:
    rows = _post("MATCH (n) DETACH DELETE n RETURN count(n) as deleted")
    return rows[0]["deleted"] if rows else 0


def get_stats() -> dict:
    n = _post("MATCH (n) RETURN count(n) as total")
    r = _post("MATCH ()-[r]->() RETURN count(r) as total")
    l = _post("MATCH (n) RETURN distinct labels(n) as label")
    return {"nodes": n[0]["total"] if n else 0, "relationships": r[0]["total"] if r else 0,
            "labels": [x.get("label", []) for x in l] if l else []}


def save_memory(*a, **kw):
    if len(a) >= 2:
        upsert_node("Knowledge", {"id": a[0]}, {"content": str(a[1]), "updated": datetime.now(timezone.utc).isoformat()})
        return True
    spec = a[0] if a else kw.get("spec_id", "")
    upsert_node("Knowledge", {"id": spec}, {"title": kw.get("title", ""), "content": kw.get("content", ""),
        "type": kw.get("memory_type", "learning"), "tags": json.dumps(kw.get("tags", [])),
        "updated": datetime.now(timezone.utc).isoformat()})
    return {"id": spec}


def get_memory(key: str) -> Optional[Any]:
    rows = _post("MATCH (n:Knowledge {id: $id}) RETURN n, id(n) as id", {"id": key})
    return rows[0] if rows else None


def search_memory(query: str = "", limit: int = 50) -> list:
    q = "MATCH (n:Knowledge) RETURN n, id(n) as id LIMIT $limit"
    p = {"limit": limit}
    if query:
        q = "MATCH (n:Knowledge) WHERE n.content CONTAINS $q OR n.title CONTAINS $q RETURN n, id(n) as id LIMIT $limit"
        p["q"] = query
    return [{"key": r.get("n", {}).get("id", ""), "value": r.get("n", {}).get("content", ""), "id": r.get("id")} for r in _post(q, p)]


def memory_stats() -> dict:
    r = _post("MATCH (n:Knowledge) RETURN count(n) as total, collect(distinct n.type) as types")
    return {"total": r[0]["total"] if r else 0, "types": r[0].get("types", []) if r else []}


def create_session(**kw) -> Optional[dict]:
    sid = kw.get("session_id") or kw.get("title", f"ses-{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    upsert_node("Session", {"id": sid}, {"user_id": kw.get("user_id", kw.get("project", "system")),
        "channel": kw.get("channel", "api"), "project": kw.get("project", ""),
        "tags": json.dumps(kw.get("tags", [])), "created": datetime.now(timezone.utc).isoformat()})
    return {"id": sid}


def get_session(session_id: str) -> Optional[dict]:
    r = _post("MATCH (s:Session {id: $id}) RETURN s, id(s) as id", {"id": session_id})
    return r[0] if r else None


def list_sessions(limit: int = 20) -> list:
    return _post("MATCH (s:Session) RETURN s, id(s) as id ORDER BY s.created DESC LIMIT $limit", {"limit": limit})


def search_sessions(query: str = "") -> list:
    if not query:
        return list_sessions()
    return _post("MATCH (s:Session) WHERE s.id CONTAINS $q OR s.user_id CONTAINS $q RETURN s, id(s) as id LIMIT 20", {"q": query})


def toggle_pin(session_id: str) -> Optional[dict]:
    r = _post("MATCH (s:Session {id: $id}) SET s.pinned = CASE WHEN s.pinned IS NULL OR s.pinned = false THEN true ELSE false END RETURN s", {"id": session_id})
    return r[0] if r else None


def delete_session(session_id: str) -> bool:
    r = _post("MATCH (s:Session {id: $id}) DETACH DELETE s RETURN count(s) as deleted", {"id": session_id})
    return bool(r and r[0].get("deleted", 0) > 0)


def add_message(session_id: str, role: str, content: str, tokens: int = 0) -> Optional[dict]:
    mid = f"msg-{session_id}-{datetime.now().strftime('%H%M%S%f')}"
    r = _post("MATCH (s:Session {id: $sid}) CREATE (m:Message {id: $id, role: $role, content: $content, tokens: $tokens, created: $ts}) MERGE (s)-[:HAS_MESSAGE]->(m) RETURN m, id(m) as id",
              {"sid": session_id, "id": mid, "role": role, "content": content, "tokens": tokens, "ts": datetime.now(timezone.utc).isoformat()})
    return r[0] if r else None


def link_session_to_spec(session_id: str, spec_id: str) -> dict:
    r = _post("MATCH (s:Session {id: $sid}) MATCH (sp:Spec {id: $spid}) MERGE (s)-[:COMPLETED]->(sp) RETURN s, sp",
              {"sid": session_id, "spid": spec_id})
    return r[0] if r else {}


def save_contact(data: dict) -> dict:
    return upsert_node("Contact", {"id": f"contact:{data.get('phone', '')}"},
                       {"phone": data.get("phone", ""), "name": data.get("name", ""),
                        "status": data.get("status", "lead"), "source": data.get("source", ""),
                        "notes": data.get("notes", ""), "updated": datetime.now(timezone.utc).isoformat()})


def get_contacts(label: str = "Contact") -> list:
    return _post(f"MATCH (n:{label}) RETURN n, id(n) as id ORDER BY n.updated DESC")


def create_contact(phone: str, name: str = "", source: str = "", status: str = "lead") -> Optional[dict]:
    return upsert_node("Contact", {"id": f"contact:{phone}"},
                       {"phone": phone, "name": name, "source": source, "status": status,
                        "updated": datetime.now(timezone.utc).isoformat()})


def get_contact(phone: str) -> Optional[dict]:
    r = _post("MATCH (n:Contact {id: $id}) RETURN n, id(n) as id", {"id": f"contact:{phone}"})
    return r[0] if r else None


def search_contacts(query: str = "", status: str = "") -> list:
    where, p = [], {}
    if query:
        where.append("(n.name CONTAINS $q OR n.phone CONTAINS $q)"); p["q"] = query
    if status:
        where.append("n.status = $status"); p["status"] = status
    w = "WHERE " + " AND ".join(where) if where else ""
    return _post(f"MATCH (n:Contact) {w} RETURN n, id(n) as id ORDER BY n.updated DESC", p)


def contacts_summary() -> dict:
    t = _post("MATCH (n:Contact) RETURN count(n) as total")
    bs = _post("MATCH (n:Contact) RETURN n.status as status, count(n) as cnt ORDER BY cnt DESC")
    return {"total": t[0]["total"] if t else 0,
            "by_status": {s["status"] or "unknown": s["cnt"] for s in bs} if bs else {}}


def get_contact_history(phone: str) -> dict:
    c = get_contact(phone)
    m = _post("MATCH (n:Contact {id: $id})-[r:HAS_MESSAGE]->(m:Message) RETURN m ORDER BY m.created DESC",
              {"id": f"contact:{phone}"})
    return {"contact": c, "messages": m}


def log_wa_message(phone: str, direction: str, content: str) -> bool:
    mid = f"wa-{phone}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    r = _post("MATCH (n:Contact {id: $cid}) CREATE (m:Message {id: $id, role: $dir, content: $content, channel: 'whatsapp', created: $ts}) MERGE (n)-[:HAS_MESSAGE]->(m) RETURN m",
              {"cid": f"contact:{phone}", "id": mid, "dir": direction, "content": content,
               "ts": datetime.now(timezone.utc).isoformat()})
    return bool(r)


def update_contact(phone: str, updates: dict) -> bool:
    set_clause = "SET " + ", ".join(f"n.{k} = ${k}" for k in updates)
    r = _post(f"MATCH (n:Contact {{id: $id}}) {set_clause} RETURN n", {"id": f"contact:{phone}", **updates})
    return bool(r)
