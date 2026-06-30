import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, Response
from webui.routes.app_state import sessions, store_session

router = APIRouter()


def _clean(s):
    return {k: v for k, v in s.items() if k != "messages"}


@router.get("/api/sessions")
async def list_sessions(
    pinned: bool | None = None,
    project: str | None = None,
    tag: str | None = None,
    archived: bool = False,
    limit: int = 50,
):
    result = []
    for s in sessions.values():
        if s.get("archived", False) != archived:
            continue
        if pinned is not None and s.get("pinned") != pinned:
            continue
        if project and s.get("project") != project:
            continue
        if tag and tag not in s.get("tags", []):
            continue
        result.append(_clean(s))
    result.sort(key=lambda s: (not s.get("pinned", False), s.get("updated_at", "")))
    return {"sessions": result[:limit], "total": len(result)}


@router.get("/api/sessions/search")
async def search_sessions(q: str = Query(default=None, min_length=1)):
    q_lower = (q or "").lower()
    if not q_lower:
        return {"results": [], "total": 0}
    results = []
    for s in sessions.values():
        if q_lower in s.get("title", "").lower():
            results.append(s)
            continue
        for msg in s.get("messages", []):
            if q_lower in msg.get("content", "").lower():
                results.append(s)
                break
    return {"results": [_clean(s) for s in results[:20]], "total": len(results)}


@router.post("/api/sessions")
async def create_session(data: dict):
    session_id = data.get("id", str(uuid.uuid4()))
    session = {
        "id": session_id,
        "title": data.get("title", "Nueva sesión"),
        "pinned": data.get("pinned", False),
        "project": data.get("project"),
        "tags": data.get("tags", []),
        "archived": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "token_count": 0,
        "messages": [],
    }
    sessions[session_id] = session
    store_session(session)
    return session


@router.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


@router.put("/api/sessions/{session_id}")
async def update_session(session_id: str, data: dict):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    for key in ("title", "pinned", "project", "tags"):
        if key in data:
            s[key] = data[key]
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    return s


@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    del sessions[session_id]
    store = __import__(
        "webui.routes.app_state", fromlist=["get_neo4j_store"]
    ).get_neo4j_store()
    if store:
        try:
            store["delete"](session_id)
        except Exception:
            pass
    return {"status": "deleted"}


@router.post("/api/sessions/{session_id}/pin")
async def toggle_pin(session_id: str):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s["pinned"] = not s.get("pinned", False)
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"pinned": s["pinned"]}


@router.post("/api/sessions/{session_id}/archive")
async def toggle_archive(session_id: str):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    s["archived"] = not s.get("archived", False)
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"archived": s["archived"]}


@router.post("/api/sessions/{session_id}/duplicate")
async def duplicate_session(session_id: str):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    new_id = str(uuid.uuid4())
    sessions[new_id] = {
        **s,
        "id": new_id,
        "title": f"{s['title']} (copia)",
        "pinned": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return sessions[new_id]


@router.get("/api/sessions/{session_id}/export/{fmt}")
async def export_session(session_id: str, fmt: str = "md"):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    if fmt == "json":
        return JSONResponse(content=s)
    lines = [
        f"# {s['title']}",
        "",
        f"- **Proyecto:** {s.get('project', 'N/A')}",
        f"- **Tags:** {', '.join(s.get('tags', []))}",
        f"- **Creada:** {s['created_at']}",
        f"- **Tokens:** {s['token_count']}",
        "",
        "---",
        "",
    ]
    for msg in s.get("messages", []):
        lines.append(
            f"### {'👤' if msg['role'] == 'user' else '🤖'} {msg['role'].capitalize()}\n"
        )
        lines.append(msg["content"] + "\n")
    return Response(
        content="\n".join(lines),
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="{s["title"]}.md"'},
    )


@router.post("/api/sessions/{session_id}/messages")
async def add_message(session_id: str, data: dict):
    s = sessions.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    message = {
        "id": str(uuid.uuid4()),
        "role": data.get("role", "user"),
        "content": data.get("content", ""),
        "tokens": data.get("tokens", 0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    s.setdefault("messages", []).append(message)
    s["token_count"] = sum(m.get("tokens", 0) for m in s["messages"])
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    return message
