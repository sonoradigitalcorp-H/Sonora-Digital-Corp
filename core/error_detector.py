"""Error Detector — Module 3 of Evolution Engine (HAS-008)
Detects patterns of failure/degradation across subsystems.
"""
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def detect(metrics: dict) -> list[dict]:
    issues = []

    if metrics.get("violations", 0) > 0:
        issues.append({
            "severity": "high",
            "subsystem": "constitution",
            "message": f"{metrics['violations']} constitution violations detected",
        })

    tests_total = metrics.get("tests_total", 0)
    tests_passed = metrics.get("tests_passed", 0)
    if tests_total > 0 and tests_passed < tests_total:
        issues.append({
            "severity": "high",
            "subsystem": "tests",
            "message": f"{tests_total - tests_passed} test(s) failing",
        })

    if metrics.get("git_ahead", 0) > 5:
        issues.append({
            "severity": "medium",
            "subsystem": "git",
            "message": f"{metrics['git_ahead']} commits ahead of origin/main — push needed",
        })

    if metrics.get("git_behind", 0) > 5:
        issues.append({
            "severity": "medium",
            "subsystem": "git",
            "message": f"{metrics['git_behind']} commits behind origin/main — pull needed",
        })

    if metrics.get("agents", 0) == 0:
        issues.append({
            "severity": "critical",
            "subsystem": "agents",
            "message": "No agents registered",
        })

    return issues
