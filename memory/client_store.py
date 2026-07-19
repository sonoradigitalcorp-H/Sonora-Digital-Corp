"""
Client Store — per-client learning data.

Each client has their own learning profile stored in:
  memory/clients/{client_id}/
    profile.yaml             — static info (name, niche, phone, tenant)
    interactions.jsonl       — every interaction
    patterns.yaml            — detected patterns specific to this client
    recommendations.yaml     — system recommendations for this client
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
CLIENTS_DIR = REPO / "memory" / "clients"


class ClientStore:
    DEFAULT_BASE = CLIENTS_DIR

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = (base_dir or self.DEFAULT_BASE).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _client_dir(self, client_id: str) -> Path:
        p = self.base_dir / client_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _profile_path(self, client_id: str) -> Path:
        return self._client_dir(client_id) / "profile.yaml"

    def _interactions_path(self, client_id: str) -> Path:
        return self._client_dir(client_id) / "interactions.jsonl"

    def _patterns_path(self, client_id: str) -> Path:
        return self._client_dir(client_id) / "patterns.yaml"

    def _recommendations_path(self, client_id: str) -> Path:
        return self._client_dir(client_id) / "recommendations.yaml"

    def _ensure_profile(self, client_id: str, profile: dict | None = None) -> dict:
        path = self._profile_path(client_id)
        if path.exists():
            return yaml.safe_load(path.read_text()) or {}
        default = {
            "client_id": client_id,
            "name": profile.get("name", ""),
            "phone": profile.get("phone", ""),
            "niche": profile.get("niche", ""),
            "tenant": profile.get("tenant", "sdc"),
            "first_interaction": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_interaction": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "total_interactions": 0,
            "total_tokens_spent": 0,
            "services_used": [],
            "satisfaction_score": 5.0,
            "active": True,
        }
        if profile:
            default.update(profile)
        path.write_text(yaml.dump(default, default_flow_style=False, allow_unicode=True, sort_keys=False))
        return default

    def save_interaction(self, client_id: str, interaction: dict) -> dict:
        profile = self.get_profile(client_id)
        if not profile:
            profile = self._ensure_profile(client_id, interaction.get("profile"))

        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        entry = {
            "timestamp": now,
            "type": interaction.get("type", "message"),
            "content": interaction.get("content", ""),
            "tokens_used": interaction.get("tokens_used", 0),
            "service": interaction.get("service", ""),
            "success": interaction.get("success", True),
            "duration_ms": interaction.get("duration_ms", 0),
            "satisfaction_score": interaction.get("satisfaction_score"),
        }

        path = self._interactions_path(client_id)
        with open(path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        profile["total_interactions"] = profile.get("total_interactions", 0) + 1
        profile["total_tokens_spent"] = profile.get("total_tokens_spent", 0) + entry["tokens_used"]
        profile["last_interaction"] = now
        if entry["service"] and entry["service"] not in profile.get("services_used", []):
            services = profile.get("services_used", [])
            services.append(entry["service"])
            profile["services_used"] = services
        if entry.get("satisfaction_score") is not None:
            scores = self._get_satisfaction_scores(client_id)
            profile["satisfaction_score"] = round(sum(scores) / len(scores), 1)

        self.update_profile(client_id, profile)
        return entry

    def get_profile(self, client_id: str) -> dict | None:
        path = self._profile_path(client_id)
        if path.exists():
            return yaml.safe_load(path.read_text()) or None
        return None

    def update_profile(self, client_id: str, updates: dict) -> dict:
        profile = self.get_profile(client_id) or self._ensure_profile(client_id)
        profile.update(updates)
        path = self._profile_path(client_id)
        path.write_text(yaml.dump(profile, default_flow_style=False, allow_unicode=True, sort_keys=False))
        return profile

    def get_interactions(self, client_id: str, limit: int = 50) -> list:
        path = self._interactions_path(client_id)
        if not path.exists():
            return []
        entries = []
        with open(path) as f:
            for line in f:
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
        return entries[:limit]

    def get_patterns(self, client_id: str) -> list:
        path = self._patterns_path(client_id)
        if not path.exists():
            return []
        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, list) else []

    def add_pattern(self, client_id: str, pattern: dict):
        patterns = self.get_patterns(client_id)
        pattern["detected_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        patterns.append(pattern)
        path = self._patterns_path(client_id)
        path.write_text(yaml.dump(patterns, default_flow_style=False, allow_unicode=True, sort_keys=False))

    def get_recommendations(self, client_id: str) -> list:
        path = self._recommendations_path(client_id)
        if not path.exists():
            return []
        data = yaml.safe_load(path.read_text())
        return data if isinstance(data, list) else []

    def add_recommendation(self, client_id: str, recommendation: dict):
        recommendations = self.get_recommendations(client_id)
        recommendation["created_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        recommendations.append(recommendation)
        path = self._recommendations_path(client_id)
        path.write_text(yaml.dump(recommendations, default_flow_style=False, allow_unicode=True, sort_keys=False))

    def all_clients(self) -> list[str]:
        if not self.base_dir.exists():
            return []
        return sorted(
            d.name for d in self.base_dir.iterdir()
            if d.is_dir() and (d / "profile.yaml").exists()
        )

    def stats(self) -> dict:
        clients = self.all_clients()
        total_interactions = 0
        total_patterns = 0
        active_count = 0
        niches = {}

        for cid in clients:
            profile = self.get_profile(cid)
            if profile:
                if profile.get("active", False):
                    active_count += 1
                niche = profile.get("niche", "unknown")
                niches[niche] = niches.get(niche, 0) + 1
            total_interactions += len(self.get_interactions(cid, limit=10**6))
            total_patterns += len(self.get_patterns(cid))

        return {
            "total_clients": len(clients),
            "active_clients": active_count,
            "total_interactions": total_interactions,
            "total_patterns": total_patterns,
            "niches": niches,
        }

    def _get_satisfaction_scores(self, client_id: str) -> list[float]:
        interactions = self.get_interactions(client_id, limit=10**6)
        return [
            i["satisfaction_score"] for i in interactions
            if i.get("satisfaction_score") is not None
        ]
