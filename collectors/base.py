"""Base classes para el Artist Intelligence Network"""
import json
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class RawMetric:
    platform: str
    metric: str
    value: float | int
    timestamp: str
    artist_id: str
    extra: dict = field(default_factory=dict)


@dataclass
class NormalizedMetric:
    metric: str
    platform: str
    value: float | int
    raw_value: float | int
    artist_id: str
    normalized_at: str
    extra: dict = field(default_factory=dict)


@dataclass
class DerivedMetric:
    metric: str
    value: float
    artist_id: str
    source_metrics: list[str]
    computed_at: str
    extra: dict = field(default_factory=dict)


NORMALIZATION_MAP = {
    "spotify": {
        "monthly_listeners": "streams",
        "followers": "followers",
        "popularity": "popularity_score",
        "top_track_popularity": "top_track_score",
    },
    "instagram": {
        "followers_count": "followers",
        "media_count": "posts_count",
        "avg_likes": "avg_likes",
        "avg_comments": "avg_comments",
    },
    "tiktok": {
        "followers": "followers",
        "likes": "total_likes",
        "videos": "posts_count",
        "views": "total_views",
    },
    "youtube": {
        "subscribers": "followers",
        "views": "total_views",
        "videos": "posts_count",
    },
}


class Collector(ABC):
    platform: str = ""

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.state_file = state_dir / f"{self.platform}_state.json"

    @abstractmethod
    async def collect(self, artist_id: str) -> list[RawMetric]:
        ...

    def load_state(self) -> dict:
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"last_sync": None, "artists": {}}

    def save_state(self, state: dict):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, indent=2, default=str))

    def update_state(self, artist_id: str):
        state = self.load_state()
        state["last_sync"] = datetime.now(timezone.utc).isoformat()
        state["artists"][artist_id] = {"last_sync": state["last_sync"]}
        self.save_state(state)


class Normalizer:
    def normalize(self, raw: RawMetric) -> NormalizedMetric:
        platform_map = NORMALIZATION_MAP.get(raw.platform, {})
        canonical = platform_map.get(raw.metric, raw.metric)
        return NormalizedMetric(
            metric=canonical,
            platform=raw.platform,
            value=raw.value,
            raw_value=raw.value,
            artist_id=raw.artist_id,
            normalized_at=datetime.now(timezone.utc).isoformat(),
            extra=raw.extra,
        )

    def normalize_batch(self, raw_metrics: list[RawMetric]) -> list[NormalizedMetric]:
        return [self.normalize(r) for r in raw_metrics]


class MetricsEngine:
    def __init__(self, history: Optional[dict] = None):
        self.history = history or {}

    def calculate(self, current: list[NormalizedMetric], artist_id: str) -> list[DerivedMetric]:
        derived = []
        now = datetime.now(timezone.utc).isoformat()
        prev = self.history.get(artist_id, {})

        for m in current:
            key = f"{m.platform}.{m.metric}"
            prev_val = prev.get(key)

            if prev_val is not None and prev_val != 0:
                growth = ((m.value - prev_val) / prev_val) * 100
                derived.append(DerivedMetric(
                    metric=f"{m.metric}_growth_pct",
                    value=round(growth, 2),
                    artist_id=artist_id,
                    source_metrics=[key],
                    computed_at=now,
                ))

            if m.metric in ("followers", "streams", "total_views"):
                derived.append(DerivedMetric(
                    metric=f"{m.metric}_momentum",
                    value=round(m.value / max(prev_val or m.value, 1), 4),
                    artist_id=artist_id,
                    source_metrics=[key],
                    computed_at=now,
                ))

        self._update_history(artist_id, current)
        return derived

    def _update_history(self, artist_id: str, metrics: list[NormalizedMetric]):
        entry = {}
        for m in metrics:
            entry[f"{m.platform}.{m.metric}"] = m.value
        self.history[artist_id] = entry

    def save_history(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.history, indent=2, default=str))

    @classmethod
    def load_history(cls, path: Path):
        if path.exists():
            return cls(json.loads(path.read_text()))
        return cls()
