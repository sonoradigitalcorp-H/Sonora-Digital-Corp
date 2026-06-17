"""
JARVIS Tools Router — Dispatches tool calls by name.
"""

import json
import logging
from typing import Any, Dict

from src.core.tools.definitions import TOOL_DEFINITIONS
from src.core.tools.executors import (
    execute_command,
    read_file,
    write_file,
    list_files,
    run_tests,
    search_code,
    docker_build,
    docker_deploy,
    search_semantic,
    rag_store,
    ask_user,
)

log = logging.getLogger("jarvis.tools.router")

AVAILABLE_TOOLS = {
    "execute_command": execute_command,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "run_tests": run_tests,
    "search_code": search_code,
    "docker_build": docker_build,
    "docker_deploy": docker_deploy,
    "search_semantic": search_semantic,
    "rag_store": rag_store,
    "ask_user": ask_user,
}


def execute_tool(name: str, arguments: dict) -> Dict[str, Any]:
    log.info(f"Tool call: {name}({json.dumps(arguments)[:200]})")
    if name not in AVAILABLE_TOOLS:
        return {"status": "error", "message": f"Tool not found: {name}"}
    try:
        result = AVAILABLE_TOOLS[name](**arguments)
        log.info(f"Tool result: {json.dumps(result)[:200]}")
        return result
    except Exception as e:
        log.error(f"Tool error: {e}")
        return {"status": "error", "message": str(e)}
