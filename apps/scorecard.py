"""Scorecard — Module 2 of Evolution Engine (HAS-008)
Scores overall system health 0-100 based on Observer metrics.
"""
import json
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
SCORECARD_FILE = REPO / "evolution" / "scorecard.json"


def calculate(metrics: dict) -> int:
    weights = {
        "tests_passed": 0.15,
        "agents": 0.10,
        "capabilities": 0.10,
        "constitution_rules": 0.05,
        "memory_count": 0.05,
        "git_ahead": -0.05,
        "violations": -0.15,
    }
    score = 50.0
    for key, weight in weights.items():
        val = metrics.get(key, 0)
        score += val * weight
    return max(0, min(100, int(score)))


def save(score: int, metrics: dict):
    card = {
        "overall": score,
        "by_dimension": {
            "observability": metrics.get("git_ahead", 0) == 0,
            "test_health": metrics.get("tests_total", 0) > 0 and metrics.get("tests_passed", 0) == metrics.get("tests_total", 0),
            "coverage": metrics.get("tests_passed", 0) / max(metrics.get("tests_total", 1), 1) >= 0.6 if metrics.get("tests_total", 0) > 0 else False,
        },
        "metrics": metrics,
        "updated": "2026-07-08T20:00:00Z",
    }
    SCORECARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SCORECARD_FILE, "w") as f:
        json.dump(card, f, indent=2)
    return card


def load() -> dict:
    if SCORECARD_FILE.exists():
        return json.loads(SCORECARD_FILE.read_text())
    return {"overall": 0, "by_dimension": {}, "metrics": {}, "updated": ""}
