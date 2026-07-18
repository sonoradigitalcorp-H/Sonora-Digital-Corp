"""Engram Auto-Capture System — automatic memory persistence for commands, env, git, and processes.

FR-01: Auto-captura de comandos Bash
FR-02: Snapshot de Variables de Entorno
FR-03: Snapshot de Estado Git
FR-04: Snapshot de Procesos Relevantes
FR-05: Versionado Semántico por Topic Key
FR-06: Clasificador Automático de Tipo
FR-07: Export Obsidian Live
FR-08: Recuperación de Contexto
FR-09: Systemd Service Unificado
"""
import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|auth[_-]?token)\s*=\s*['\"]?\S+"),
    re.compile(r"(?i)(sk-[a-zA-Z0-9]{20,})"),
    re.compile(r"(?i)(ghp_[a-zA-Z0-9]{36,})"),
    re.compile(r"(?i)(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})"),
]

READ_ONLY_COMMANDS = {
    "ls", "cat", "grep", "pwd", "cd", "echo", "head", "tail",
    "less", "more", "wc", "sort", "uniq", "find", "locate",
    "which", "type", "help", "man", "whatis", "apropos",
}

RELEVANT_PREFIXES = {
    "git", "npm", "pip", "docker", "kubectl", "make", "rsync", "scp",
    "ssh", "wacli", "engram", "python", "python3", "node", "npx",
    "yarn", "bun", "go", "cargo", "rustc", "systemctl", "journalctl",
    "docker-compose", "docker compose", "helm", "terraform", "ansible",
    "curl", "wget", "psql", "redis-cli", "neo4j", "qdrant", "openclaw",
}

ENV_PREFIXES = ("SDC_", "MCP_", "OPENCLAW_", "QDRANT_", "NEO4J_", "SUPABASE_", "ABE_", "WACLI_", "ENGRAM_")

TYPE_KEYWORDS = {
    "bugfix": ["error", "fail", "bug", "exception", "traceback", "fix", "crash", "panic", "null pointer", "segfault"],
    "decision": ["decid", "elegi", "opte", "tradeoff", "estrategia", "migrate", "replace", "adopt"],
    "config": ["config", "configur", "yaml", "json", "env", "variable", "setting", "parameter", "flag"],
    "pattern": ["patron", "pattern", "convencion", "estilo", "estandar", "convention", "style", "standard"],
    "learning": ["aprend", "learning", "descubr", "gotcha", "truco", "tip", "lesson", "insight", "discover"],
    "architecture": [
        "arquitect", "infra", "deploy", "servidor", "container",
        "docker", "cluster", "microservice", "api gateway",
        "load balancer", "microservicios",
    ],
}


# ─── FR-01: Auto-captura de Comandos Bash ──────────────────────────────────

def should_capture(command: str) -> bool:
    cmd = command.strip().split()[0] if command.strip() else ""
    if cmd in READ_ONLY_COMMANDS:
        return False
    cmd_base = command.strip().split(maxsplit=1)[0] if command.strip() else ""
    if cmd_base in RELEVANT_PREFIXES:
        return True
    if any(command.startswith(p) for p in RELEVANT_PREFIXES):
        return True
    return False


def sanitize_secrets(text: str) -> str:
    result = text
    for pattern in SECRET_PATTERNS:
        result = pattern.sub(r"\1=[FILTERED]", result)
    return result


def classify_command(command: str) -> str:
    cmd = command.strip().split()[0] if command.strip() else ""
    if cmd in ("git",):
        return "code_change"
    if cmd in ("npm", "yarn", "bun", "npx", "go", "cargo", "make"):
        return "build"
    if cmd in ("docker", "docker-compose", "docker compose", "helm", "kubectl"):
        return "deploy"
    if cmd in ("ssh", "rsync", "scp"):
        return "remote"
    return "other"


def capture_command_observation(command: str, exit_code: int, cwd: str, session_id: str) -> dict:
    title = f"cmd: {command[:60]}"
    content = json.dumps({
        "command": command,
        "exit_code": exit_code,
        "cwd": cwd,
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
    }, ensure_ascii=False)
    today = datetime.utcnow().strftime("%Y%m%d")
    return {
        "title": title,
        "type": "command",
        "content": sanitize_secrets(content),
        "topic_key": f"commands/{today}",
        "project": _detect_project(cwd),
    }


def _detect_project(cwd: str) -> str:
    return os.environ.get("ENGRAM_PROJECT", Path(cwd).name)


# ─── FR-02: Snapshot de Variables de Entorno ──────────────────────────────

def capture_env_snapshot() -> dict:
    relevant = {}
    for key, value in os.environ.items():
        if key.startswith(ENV_PREFIXES):
            relevant[key] = value
    return relevant


# ─── FR-03: Snapshot de Estado Git ───────────────────────────────────────

def capture_git_snapshot(repo_path: str | None = None) -> dict:
    cwd = repo_path or os.getcwd()
    git_dir = Path(cwd) / ".git"
    if not git_dir.exists():
        return {"status": "", "commits": []}

    result = {"status": "", "commits": []}
    try:
        status = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, timeout=10, cwd=cwd
        )
        result["status"] = status.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    try:
        log = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True, text=True, timeout=10, cwd=cwd
        )
        result["commits"] = [c for c in log.stdout.strip().split("\n") if c]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return result


# ─── FR-04: Snapshot de Procesos Relevantes ──────────────────────────────

PROCESS_KEYWORDS = ["python", "node", "docker", "postgres", "redis", "neo4j", "qdrant", "n8n", "ollama", "wacli", "engram", "openclaw"]

def capture_process_snapshot() -> list:
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True, text=True, timeout=10
        )
        lines = result.stdout.strip().split("\n")
        relevant = []
        for line in lines[1:]:
            if any(kw in line.lower() for kw in PROCESS_KEYWORDS):
                parts = line.split(maxsplit=10)
                if len(parts) >= 11:
                    relevant.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": parts[10],
                    })
        return relevant
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


# ─── FR-05: Versionado Semántico ──────────────────────────────────────────

def format_version(revision_count: int) -> str:
    major = revision_count // 100
    minor = (revision_count % 100) // 10
    patch = revision_count % 10
    return f"v{major}.{minor}.{patch}"


class EngramVersionTracker:
    def __init__(self):
        self._counters: dict[str, int] = {}

    def next_version(self, topic_key: str) -> str:
        self._counters.setdefault(topic_key, 0)
        self._counters[topic_key] += 1
        return format_version(self._counters[topic_key])

    def next_version_meta(self, topic_key: str) -> dict:
        self._counters.setdefault(topic_key, 0)
        self._counters[topic_key] += 1
        rc = self._counters[topic_key]
        return {
            "version": format_version(rc),
            "sequence": rc,
            "topic_key": topic_key,
            "revision_count": rc,
        }


# ─── FR-06: Clasificador Automático de Tipo ──────────────────────────────

def classify_type_by_keywords(content: str) -> str:
    content_lower = content.lower()
    for obs_type, keywords in TYPE_KEYWORDS.items():
        for kw in keywords:
            if kw in content_lower:
                return obs_type
    return "discovery"


# ─── FR-07: Export Obsidian Live ──────────────────────────────────────────

class ObsidianExporter:
    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self._exported = set()
        self._state_file = self.vault / ".engram_export_state.json"

    def ensure_vault_structure(self) -> None:
        for subdir in ["Observations", "Sessions", "Projects", "Graph", "Canvas"]:
            (self.vault / subdir).mkdir(parents=True, exist_ok=True)
        self._load_state()

    def _load_state(self) -> None:
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text())
                self._exported = set(data.get("exported_ids", []))
            except (json.JSONDecodeError, KeyError):
                self._exported = set()

    def _save_state(self) -> None:
        self._state_file.write_text(json.dumps({
            "exported_ids": list(self._exported),
            "updated_at": datetime.utcnow().isoformat(),
        }))

    def mark_exported(self, obs_id: str) -> None:
        self._exported.add(obs_id)
        self._save_state()

    def is_already_exported(self, obs_id: str) -> bool:
        return obs_id in self._exported

    def export_observation(self, obs: dict) -> Path:
        title = obs.get("title", "untitled").replace("/", "-")
        md_path = self.vault / "Observations" / f"{title}.md"
        tags = ["engram", obs.get("type", "discovery")]
        frontmatter = (
            "---\n"
            f'title: {obs.get("title", "")}\n'
            f'type: {obs.get("type", "discovery")}\n'
            f'project: {obs.get("project", "")}\n'
            f'topic_key: {obs.get("topic_key", "")}\n'
            f'version: {obs.get("version", "")}\n'
            f'created_at: {obs.get("created_at", "")}\n'
            f'tags: {json.dumps(tags)}\n'
            "---\n"
        )
        md_path.write_text(frontmatter + obs.get("content", "") + "\n")
        obs_id = obs.get("id", title)
        self.mark_exported(obs_id)
        return md_path

    def export_graph(self, relations: list[tuple[str, str, str]]) -> Path:
        graph_path = self.vault / "Graph" / "relationships.md"
        lines = ["# Graph de Relaciones\n", "\n## Mermaid\n```mermaid\ngraph LR\n"]
        for source, relation, target in relations:
            lines.append(f"  {source} --{relation}--> {target}\n")
        lines.append("```\n")
        lines.append("\n## Plain Text\n")
        for source, relation, target in relations:
            lines.append(f"- {source} -> {relation} -> {target}\n")
        graph_path.write_text("".join(lines))
        return graph_path


# ─── FR-08: Recuperación de Contexto ──────────────────────────────────────

class EngramClientAdapter:
    def __init__(self):
        self._client = None
        try:
            from engram import EngramClient
            self._client = EngramClient()
            self.available = True
        except (ImportError, ModuleNotFoundError):
            self.available = False

    def search(self, project: str, since: str, limit: int = 100) -> list[dict]:
        if not self.available:
            return self._fallback_search(project, since, limit)
        return self._client.search(project=project, since=since, limit=limit)

    def _fallback_search(self, project: str, since: str, limit: int = 100) -> list[dict]:
        results = []
        engram_dir = Path.home() / ".engram"
        db_path = engram_dir / "engram.db"
        if not db_path.exists():
            return results
        try:
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(
                "SELECT id, title, type, content, topic_key, project, created_at "
                "FROM observations "
                "WHERE project = ? AND created_at >= ? "
                "ORDER BY created_at DESC LIMIT ?",
                (project, since, limit),
            )
            for row in cur.fetchall():
                results.append(dict(row))
            conn.close()
        except (ImportError, sqlite3.Error):
            pass
        return results


class ContextRecovery:
    def __init__(self, client: EngramClientAdapter | None = None):
        self.client = client or EngramClientAdapter()

    def recover(self, project: str, days: int = 7, types: list[str] | None = None) -> dict:
        result = {
            "decisions": [],
            "bugs_fixed": [],
            "configs": [],
            "git_activity": "",
            "env_changes": [],
            "processes": [],
            "llm_summary": "",
        }

        cutoff = datetime.utcnow() - timedelta(days=days)

        observations = self.client.search(
            project=project,
            since=cutoff.isoformat(),
            limit=100,
        )

        for obs in observations:
            obs_type = obs.get("type", "")
            if types and obs_type not in types:
                continue
            if obs_type == "decision":
                result["decisions"].append(obs)
            elif obs_type == "bugfix":
                result["bugs_fixed"].append(obs)
            elif obs_type == "config":
                result["configs"].append(obs)
            elif obs_type == "architecture":
                result["env_changes"].append(obs)

        try:
            git = capture_git_snapshot()
            result["git_activity"] = git.get("status", "")
            result["processes"] = capture_process_snapshot()
        except Exception:
            pass

        total = len(result["decisions"]) + len(result["bugs_fixed"]) + len(result["configs"])
        if total == 0:
            result["llm_summary"] = "No hay actividad reciente en este proyecto."
        else:
            result["llm_summary"] = f"Actividad reciente: {total} observaciones en {days} días."

        return result


# ─── Rate Limiter ──────────────────────────────────────────────────────────

class rate_limiter:
    def __init__(self, max_per_minute: int = 30, window_seconds: int = 60):
        self.max_per_minute = max_per_minute
        self.window_seconds = window_seconds
        self._windows: dict[str, list[float]] = {}

    def allow(self, session_id: str) -> bool:
        now = time.time()
        window = self._windows.setdefault(session_id, [])
        cutoff = now - self.window_seconds
        self._windows[session_id] = [t for t in window if t > cutoff]
        if len(self._windows[session_id]) >= self.max_per_minute:
            return False
        self._windows[session_id].append(now)
        return True


# ─── CLI Entry Point ──────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Engram Auto-Capture System")
    parser.add_argument("--obsidian-export", nargs="?", const="/tmp/obsidian-vault", help="Export to Obsidian vault")
    parser.add_argument("--vault", default="/tmp/obsidian-vault", help="Obsidian vault path")
    parser.add_argument("--watch", action="store_true", help="Watch for changes")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    parser.add_argument("--context", nargs="?", const="sonora-digital-corp", help="Recover project context")
    parser.add_argument("--days", type=int, default=7, help="Days for context recovery")
    parser.add_argument("--snapshot", choices=["env", "git", "processes"], help="Take a snapshot")
    parser.add_argument("--format-version", type=int, help="Format a revision_count as version string")
    args = parser.parse_args()

    if args.format_version is not None:
        print(format_version(args.format_version))
        return

    if args.obsidian_export:
        vault = args.obsidian_export or args.vault
        exporter = ObsidianExporter(vault_path=vault)
        exporter.ensure_vault_structure()
        print(f"Obsidian vault ready at {vault}")
        return

    if args.context:
        cr = ContextRecovery()
        result = cr.recover(args.context, days=args.days)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    if args.snapshot == "env":
        print(json.dumps(capture_env_snapshot(), indent=2))
    elif args.snapshot == "git":
        print(json.dumps(capture_git_snapshot(), indent=2))
    elif args.snapshot == "processes":
        print(json.dumps(capture_process_snapshot(), indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
