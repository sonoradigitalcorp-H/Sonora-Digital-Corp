"""score-artist handler — HAS-005
Compute artist scores across dimensions: momentum, virality, tour readiness, engagement, revenue health.
"""
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent.parent.parent
SCORES_DIR = REPO / "state" / "scores"


def _ensure_dir():
    SCORES_DIR.mkdir(parents=True, exist_ok=True)


def _normalize(value: float, min_v: float, max_v: float) -> float:
    if max_v - min_v == 0:
        return 50.0
    return max(0, min(100, ((value - min_v) / (max_v - min_v)) * 100))


async def execute(context: Any) -> dict:
    _ensure_dir()
    input_data = context if isinstance(context, dict) else {}
    artist_id = input_data.get("artist_id", "unknown")
    artist_name = input_data.get("artist_name", "")

    streams = input_data.get("streams", 0) or 0
    monthly_listeners = input_data.get("monthly_listeners", 0) or 0
    revenue = input_data.get("revenue", 0) or 0
    social_followers = input_data.get("social_followers", 0) or 0
    engagement_rate = input_data.get("engagement_rate", 0.0) or 0.0
    playlist_adds = input_data.get("playlist_adds", 0) or 0
    trend_growth = input_data.get("trend_growth", 0.0) or 0.0
    days_since_release = input_data.get("days_since_release", 90) or 90

    momentum = _normalize(
        (streams * 0.3 + playlist_adds * 0.4 + trend_growth * 100 * 0.3),
        0, 1000000
    )
    virality = _normalize(
        (engagement_rate * 100 * 0.5 + social_followers * 0.3 + trend_growth * 100 * 0.2),
        0, 100000
    )
    revenue_health = _normalize(revenue, 0, 500000)
    engagement = _normalize(
        (engagement_rate * 100 * 0.6 + monthly_listeners * 0.4),
        0, 100000
    )
    recency = max(0, min(100, 100 - (days_since_release / 365 * 100)))
    tour_readiness = _normalize(
        (momentum * 0.3 + engagement * 0.3 + revenue_health * 0.2 + recency * 0.2),
        0, 100
    )
    overall = round(
        momentum * 0.20 + virality * 0.20 + engagement * 0.20 +
        revenue_health * 0.15 + tour_readiness * 0.15 + recency * 0.10,
        1
    )

    score = {
        "artist_id": artist_id,
        "artist_name": artist_name,
        "overall": overall,
        "dimensions": {
            "momentum": round(momentum, 1),
            "virality": round(virality, 1),
            "engagement": round(engagement, 1),
            "revenue_health": round(revenue_health, 1),
            "tour_readiness": round(tour_readiness, 1),
            "recency": round(recency, 1),
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    path = SCORES_DIR / f"{artist_id}.json"
    path.write_text(json.dumps(score, indent=2))
    return score
