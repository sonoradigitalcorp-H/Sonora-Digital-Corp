"""Proposer — Module 4 of Evolution Engine (HAS-008)
Generates improvement proposals when score < 70.
"""
import json
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = REPO / "evolution" / "proposals"


def propose(metrics: dict, issues: list[dict]) -> list[dict]:
    PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)
    proposals = []

    for issue in issues:
        proposal = _generate_proposal(issue, metrics)
        if proposal:
            proposals.append(proposal)
            _save_proposal(proposal)

    return proposals


def _generate_proposal(issue: dict, metrics: dict) -> dict | None:
    templates = {
        "constitution": {
            "title": "Fix constitution violations",
            "description": f"Resolve {metrics.get('violations', 0)} active constitution violations",
            "impact": "high",
            "effort": "medium",
        },
        "tests": {
            "title": "Fix failing tests",
            "description": f"Repair {metrics.get('tests_total', 0) - metrics.get('tests_passed', 0)} failing tests",
            "impact": "high",
            "effort": "low",
        },
        "git": {
            "title": "Sync with origin/main",
            "description": f"Repository is {metrics.get('git_ahead', 0)} ahead, {metrics.get('git_behind', 0)} behind",
            "impact": "medium",
            "effort": "low",
        },
        "agents": {
            "title": "Register agents",
            "description": "No agents registered in system",
            "impact": "critical",
            "effort": "high",
        },
    }

    template = templates.get(issue["subsystem"])
    if not template:
        return None

    return {
        "id": f"PROP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "status": "proposed",
        "subsystem": issue["subsystem"],
        "severity": issue["severity"],
        "title": template["title"],
        "description": template["description"],
        "impact": template["impact"],
        "effort": template["effort"],
        "created": datetime.now().isoformat(),
    }


def _save_proposal(proposal: dict):
    path = PROPOSALS_DIR / f"{proposal['id']}.json"
    with open(path, "w") as f:
        json.dump(proposal, f, indent=2)
