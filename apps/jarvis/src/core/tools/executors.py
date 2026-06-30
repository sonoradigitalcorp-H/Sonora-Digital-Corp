"""
JARVIS Tools Executors — Each tool's implementation.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from src.core.tools.definitions import ALLOWED_COMMANDS

log = logging.getLogger("jarvis.tools.executors")
PROJECT_DIR = Path(__file__).parent.parent.parent.parent.parent.parent

_rate_limits: dict[str, list] = {}

_rag = None


def _get_rag():
    global _rag
    if _rag is None:
        from src.core.rag import rag

        _rag = rag
    return _rag


def rate_limit(key: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
    now = time.time()
    if key not in _rate_limits:
        _rate_limits[key] = []
    _rate_limits[key] = [t for t in _rate_limits[key] if now - t < window_seconds]
    if len(_rate_limits[key]) >= max_requests:
        return False
    _rate_limits[key].append(now)
    return True


def execute_command(command: str, timeout: int = 30) -> dict[str, Any]:
    base_cmd = command.split()[0] if command else ""
    allowed = any(command.startswith(cmd) for cmd in ALLOWED_COMMANDS)
    if not allowed:
        return {
            "status": "error",
            "message": f"Comando no permitido: {base_cmd}",
            "allowed_commands": ALLOWED_COMMANDS[:10],
        }
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(PROJECT_DIR),
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout[-3000:] if result.stdout else "",
            "error": result.stderr[-1000:] if result.stderr else None,
            "return_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": f"Timeout ({timeout}s)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def read_file(path: str, max_lines: int = 100) -> dict[str, Any]:
    full_path = PROJECT_DIR / path
    if not full_path.exists():
        return {"status": "error", "message": f"Archivo no encontrado: {path}"}
    if not full_path.is_file():
        return {"status": "error", "message": f"No es un archivo: {path}"}
    try:
        with open(full_path) as f:
            lines = f.readlines()
        content = "".join(lines[:max_lines])
        return {
            "status": "success",
            "path": path,
            "content": content,
            "total_lines": len(lines),
            "lines_shown": min(max_lines, len(lines)),
            "truncated": len(lines) > max_lines,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def write_file(path: str, content: str) -> dict[str, Any]:
    full_path = PROJECT_DIR / path
    try:
        full_path.resolve().relative_to(PROJECT_DIR.resolve())
    except ValueError:
        return {"status": "error", "message": "No se puede escribir fuera del proyecto"}
    try:
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        return {
            "status": "success",
            "path": path,
            "bytes_written": len(content),
            "lines_written": len(content.splitlines()),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_files(path: str = ".", pattern: str | None = None) -> dict[str, Any]:
    full_path = PROJECT_DIR / path
    if not full_path.exists():
        return {"status": "error", "message": f"Ruta no encontrada: {path}"}
    try:
        if pattern:

            items = [str(p.relative_to(PROJECT_DIR)) for p in PROJECT_DIR.glob(pattern)]
            return {
                "status": "success",
                "path": path,
                "items": items,
                "count": len(items),
            }
        items = []
        for entry in sorted(full_path.iterdir()):
            if entry.name.startswith("."):
                continue
            items.append(
                {
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else 0,
                }
            )
        return {"status": "success", "path": path, "items": items, "count": len(items)}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_tests(path: str = "tests/", verbose: bool = False) -> dict[str, Any]:
    cmd = f"python3 -m pytest {path} {'-v' if verbose else '-q'} --tb=short 2>&1 | tail -20"
    return execute_command(cmd, timeout=120)


def search_code(pattern: str, path: str = ".", include: str = "*.py") -> dict[str, Any]:
    cmd = f"grep -rn --include='{include}' '{pattern}' {path} 2>/dev/null | head -30"
    return execute_command(cmd)


def docker_build(path: str = ".", tag: str = "jarvis/service:latest") -> dict[str, Any]:
    return execute_command(f"docker build -t {tag} {path} 2>&1 | tail -20", timeout=300)


def docker_deploy(path: str = ".", service: str | None = None) -> dict[str, Any]:
    cmd = (
        f"docker compose -f {path}/docker-compose.yml up -d {service} 2>&1 | tail -20"
        if service
        else f"docker compose -f {path}/docker-compose.yml up -d 2>&1 | tail -20"
    )
    return execute_command(cmd, timeout=120)


def search_semantic(query: str, limit: int = 5) -> dict[str, Any]:
    r = _get_rag()
    return r.search(query, limit=limit)


def rag_store(text: str, source: str = "conversación") -> dict[str, Any]:
    r = _get_rag()
    return r.store(text, {"source": source})


def ask_user(question: str) -> dict[str, Any]:
    log.info(f"JARVIS pregunta: {question}")
    try:
        answer = input("➤ Tu respuesta: ")
        return {"status": "success", "question": question, "answer": answer}
    except (EOFError, KeyboardInterrupt):
        return {
            "status": "error",
            "question": question,
            "message": "No response available",
        }
