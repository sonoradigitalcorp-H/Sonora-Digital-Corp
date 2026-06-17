"""Shared state for all route modules."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI

log = logging.getLogger("jarvis.webui")

PROJECT_DIR = Path(__file__).parent.parent
STATIC_DIR = PROJECT_DIR / "static"
TEMPLATES_DIR = PROJECT_DIR / "templates"

app = FastAPI(title="JARVIS Web UI", version="2.0.0")

sessions: dict = {}
_neo4j_store = None
_orchestrator = None


def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        try:
            from src.core.orchestrator import get_orchestrator as _get_inst

            _orchestrator = _get_inst()
            log.info(
                f"AgentOrchestrator loaded: {len(_orchestrator.list_agents())} agents"
            )
        except Exception as e:
            log.warning(f"AgentOrchestrator not available: {e}")
    return _orchestrator


def get_neo4j_store():
    global _neo4j_store
    if _neo4j_store is None:
        try:
            from src.core.neo4j_store import (
                get_driver,
                create_session as neo_create,
                get_session as neo_get,
                list_sessions as neo_list,
                add_message as neo_msg,
                toggle_pin as neo_pin,
                delete_session as neo_del,
                init_schema,
            )

            driver = get_driver()
            if driver:
                init_schema()
                _neo4j_store = {
                    "create": neo_create,
                    "get": neo_get,
                    "list": neo_list,
                    "add_msg": neo_msg,
                    "pin": neo_pin,
                    "delete": neo_del,
                }
                log.info("Neo4j session store active")
                for s in neo_list(limit=100):
                    sid = s.get("id")
                    full = neo_get(sid)
                    if full:
                        sessions[sid] = full
            else:
                log.info("Using in-memory session store (Neo4j not available)")
        except Exception as e:
            log.warning(f"Using in-memory session store: {e}")
    return _neo4j_store


def store_session(session_data: dict):
    store = get_neo4j_store()
    if store:
        try:
            store["create"](
                session_id=session_data["id"],
                title=session_data.get("title", "Sesión"),
                project=session_data.get("project"),
                tags=session_data.get("tags", []),
            )
            for msg in session_data.get("messages", []):
                store["add_msg"](
                    session_data["id"],
                    msg["role"],
                    msg["content"],
                    msg.get("tokens", 0),
                )
        except Exception as e:
            log.warning(f"Neo4j store error: {e}")


def ensure_default_session():
    if "default" not in sessions:
        sessions["default"] = {
            "id": "default",
            "title": "Bienvenido a JARVIS",
            "pinned": True,
            "project": "JARVIS",
            "tags": ["demo", "welcome"],
            "archived": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "token_count": 0,
            "messages": [
                {
                    "id": "init",
                    "role": "assistant",
                    "content": "¡Hola! Soy **JARVIS**, tu asistente de IA. ¿En qué puedo ayudarte?\n\nPrueba los comandos: `/help`, `/status`, `/clear`",
                    "tokens": 25,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            ],
        }


ensure_default_session()
