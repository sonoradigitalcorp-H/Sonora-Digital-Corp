#!/usr/bin/env python3
"""Session Store — records every interaction as structured YAML files.

Structure:
  memory/session-store/YYYY-MM-DD/ses-{uuid}.yaml
  memory/session-store/index.json

Each session has:
  - session_id, timestamp, user, type (comando/respuesta/evento/error)
  - command/what was done
  - success (bool), duration_ms, tokens_used
  - outcome (text)
  - improvement (suggestion for next time)
  - client_impact (bool)
  - skills_used (list)
  - files_changed (list)
  - score (0-10) — set by learner later
"""

import json
import uuid
from datetime import datetime
from pathlib import Path

import yaml


class SessionStore:
    DEFAULT_BASE = Path("memory/session-store")

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = (base_dir or self.DEFAULT_BASE).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_index()

    def _index_path(self) -> Path:
        return self.base_dir / "index.json"

    def _ensure_index(self):
        if not self._index_path().exists():
            self._write_index([])

    def _read_index(self) -> list:
        return json.loads(self._index_path().read_text())

    def _write_index(self, entries: list):
        self._index_path().write_text(json.dumps(entries, indent=2, ensure_ascii=False))

    def _date_dir(self, dt: datetime | None = None) -> Path:
        d = (dt or datetime.utcnow()).strftime("%Y-%m-%d")
        p = self.base_dir / d
        p.mkdir(parents=True, exist_ok=True)
        return p

    def save(self, session: dict) -> str:
        session_id = f"ses-{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow()
        session.setdefault("session_id", session_id)
        session.setdefault("timestamp", now.isoformat() + "Z")
        session.setdefault("user", "system")
        session.setdefault("type", "evento")
        session.setdefault("command", "")
        session.setdefault("success", True)
        session.setdefault("duration_ms", 0)
        session.setdefault("tokens_used", 0)
        session.setdefault("outcome", "")
        session.setdefault("improvement", "")
        session.setdefault("client_impact", False)
        session.setdefault("skills_used", [])
        session.setdefault("files_changed", [])
        session.setdefault("score", 0)

        date_dir = self._date_dir(now)
        file_path = date_dir / f"{session_id}.yaml"
        file_path.write_text(
            yaml.dump(session, default_flow_style=False, allow_unicode=True, sort_keys=False)
        )

        index = self._read_index()
        index.append({
            "session_id": session_id,
            "timestamp": session["timestamp"],
            "user": session["user"],
            "type": session["type"],
            "command": session["command"],
            "success": session["success"],
            "duration_ms": session["duration_ms"],
            "tokens_used": session["tokens_used"],
            "date": now.strftime("%Y-%m-%d"),
        })
        self._write_index(index)

        return session_id

    def get(self, session_id: str) -> dict | None:
        index = self._read_index()
        for entry in index:
            if entry["session_id"] == session_id:
                file_path = self.base_dir / entry["date"] / f"{session_id}.yaml"
                if file_path.exists():
                    return yaml.safe_load(file_path.read_text())
        return None

    def list(self, since: str | None = None, user: str | None = None, limit: int = 50) -> list:
        index = self._read_index()
        since_dt = self._parse_iso(since) if since else None

        filtered = []
        for entry in index:
            if since_dt and self._parse_iso(entry["timestamp"]) < since_dt:
                continue
            if user and entry["user"] != user:
                continue
            filtered.append(entry)

        filtered.sort(key=lambda e: e["timestamp"], reverse=True)
        return filtered[:limit]

    def count(self, since: str | None = None) -> int:
        return len(self.list(since=since, limit=10**6))

    def success_rate(self, since: str | None = None) -> float:
        sessions = self.list(since=since, limit=10**6)
        if not sessions:
            return 0.0
        success_count = sum(1 for s in sessions if s["success"])
        return success_count / len(sessions)

    def by_type(self, since: str | None = None) -> dict:
        sessions = self.list(since=since, limit=10**6)
        result: dict = {}
        for s in sessions:
            t = s["type"]
            result[t] = result.get(t, 0) + 1
        return result

    def recent_errors(self, limit: int = 20) -> list:
        index = self._read_index()
        errors = [e for e in index if not e["success"]]
        errors.sort(key=lambda e: e["timestamp"], reverse=True)
        result = []
        for e in errors[:limit]:
            s = self.get(e["session_id"])
            if s:
                result.append(s)
        return result

    def stats(self) -> dict:
        index = self._read_index()
        total = len(index)
        by_type: dict = {}
        success_count = 0
        total_duration = 0
        for entry in index:
            t = entry["type"]
            by_type[t] = by_type.get(t, 0) + 1
            if entry["success"]:
                success_count += 1
            total_duration += entry.get("duration_ms", 0)
        recent_sessions = self.list(limit=10)
        return {
            "total": total,
            "by_type": by_type,
            "success_rate": success_count / total if total else 0.0,
            "avg_duration_ms": total_duration / total if total else 0.0,
            "recent": recent_sessions,
        }

    @staticmethod
    def _parse_iso(ts: str) -> datetime:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
