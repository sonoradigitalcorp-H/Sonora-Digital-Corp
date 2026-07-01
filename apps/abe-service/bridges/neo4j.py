import logging

log = logging.getLogger("abe.bridge.neo4j")


def _available() -> bool:
    try:
        from src.core.neo4j_store import is_available
        return is_available()
    except ImportError:
        return False


def save_memory(key: str, value: str) -> bool:
    try:
        from src.core.neo4j_store import save_memory as _save
        return _save(key, value)
    except ImportError:
        log.warning("neo4j_store not available")
        return False
    except Exception as e:
        log.warning(f"Neo4j save_memory error: {e}")
        return False


def get_memory(key: str) -> str | None:
    try:
        from src.core.neo4j_store import get_memory as _get
        return _get(key)
    except ImportError:
        return None
    except Exception as e:
        log.warning(f"Neo4j get_memory error: {e}")
        return None


def create_session(session_id: str = None, title: str = "ABE Session") -> dict | None:
    try:
        from src.core.neo4j_store import create_session as _create
        return _create(session_id, title, project="abe-music")
    except ImportError:
        return None
    except Exception as e:
        log.warning(f"Neo4j create_session error: {e}")
        return None


def add_message(session_id: str, role: str, content: str, tokens: int = 0) -> dict | None:
    try:
        from src.core.neo4j_store import add_message as _add
        return _add(session_id, role, content, tokens)
    except ImportError:
        return None
    except Exception as e:
        log.warning(f"Neo4j add_message error: {e}")
        return None


def get_session(session_id: str) -> dict | None:
    try:
        from src.core.neo4j_store import get_session as _get
        return _get(session_id)
    except ImportError:
        return None
    except Exception as e:
        log.warning(f"Neo4j get_session error: {e}")
        return None


def list_sessions(limit: int = 20) -> list[dict]:
    try:
        from src.core.neo4j_store import list_sessions as _list
        return _list(limit=limit)
    except ImportError:
        return []
    except Exception as e:
        log.warning(f"Neo4j list_sessions error: {e}")
        return []


def create_contact(phone: str, name: str = "", status: str = "lead") -> dict | None:
    try:
        from src.core.neo4j_store import create_contact as _create
        return _create(phone, name, source="abe-service", status=status)
    except ImportError:
        return None
    except Exception as e:
        log.warning(f"Neo4j create_contact error: {e}")
        return None


def search_contacts(query: str = "") -> list[dict]:
    try:
        from src.core.neo4j_store import search_contacts as _search
        return _search(query=query)
    except ImportError:
        return []
    except Exception as e:
        log.warning(f"Neo4j search_contacts error: {e}")
        return []


def contacts_summary() -> dict:
    try:
        from src.core.neo4j_store import contacts_summary as _summary
        return _summary()
    except ImportError:
        return {"total": 0, "by_status": {}}
    except Exception as e:
        log.warning(f"Neo4j contacts_summary error: {e}")
        return {"total": 0, "by_status": {}}
