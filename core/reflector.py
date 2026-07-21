"""Reflector — Module 8 of Evolution Engine (HAS-008)
Meta-cognition: analyzes the analysis, identifies patterns over time.
"""
import json
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def reflect(metrics: dict, issues: list[dict], proposals: list[dict]) -> dict:
    reflection = {
        "timestamp": datetime.now().isoformat(),
        "system_health": _assess_health(metrics),
        "issue_trends": _analyze_trends(issues),
        "recommendations": _generate_recommendations(metrics, issues),
        "score_trajectory": _calculate_trajectory(),
    }
    _save_reflection(reflection)
    return reflection


def _assess_health(metrics: dict) -> str:
    if metrics.get("violations", 0) > 0 or metrics.get("tests_total", 0) == 0:
        return "critical"
    if metrics.get("tests_passed", 0) < metrics.get("tests_total", 0):
        return "degraded"
    return "healthy"


def _analyze_trends(issues: list[dict]) -> list[str]:
    trends = []
    subsystems = {}
    for issue in issues:
        sub = issue.get("subsystem", "unknown")
        subsystems[sub] = subsystems.get(sub, 0) + 1
    for sub, count in subsystems.items():
        if count > 2:
            trends.append(f"Recurring issue in {sub} ({count}x)")
    return trends


def _generate_recommendations(metrics: dict, issues: list[dict]) -> list[str]:
    recs = []
    if metrics.get("violations", 0) > 0:
        recs.append("Run constitution-gate.py and fix violations before continuing")
    if metrics.get("git_ahead", 0) > 0:
        recs.append("Push local commits to origin/main")
    if metrics.get("git_behind", 0) > 0:
        recs.append("Pull latest changes from origin/main")
    if not issues:
        recs.append("No issues detected — consider optimizing performance")
    return recs


def _calculate_trajectory() -> str:
    scorecard = REPO / "evolution" / "scorecard.json"
    if scorecard.exists():
        try:
            data = json.loads(scorecard.read_text())
            score = data.get("overall", 50)
            if score >= 80:
                return "stable"
            if score >= 60:
                return "improving"
            return "declining"
        except Exception:
            pass
    return "unknown"


def _save_reflection(reflection: dict):
    reflections_dir = REPO / "evolution" / "reflections"
    reflections_dir.mkdir(parents=True, exist_ok=True)
    path = reflections_dir / f"reflection-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(path, "w") as f:
        json.dump(reflection, f, indent=2)
