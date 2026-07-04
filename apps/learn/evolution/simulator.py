"""Evolution Simulator — estima impacto de una propuesta en el score [FR2]"""
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent


class EvolutionSimulator:
    def __init__(self):
        self.current_score = self._compute_current_score()

    def _compute_current_score(self) -> dict:
        try:
            sys.path.insert(0, str(REPO))
            from apps.measure.scoreboard import compute_scoreboard
            sb = compute_scoreboard()
            violations = sum(a.get("violations", 0) for a in sb)
            active = sum(1 for a in sb if a.get("status") == "active")
            total = len(sb) if sb else 1
            heuristics = self._get_heuristic_count()

            base_score = 70
            base_score += (active / total) * 15
            base_score -= min(violations * 5, 15)
            base_score += min(heuristics, 10)

            return {
                "score": round(base_score, 1),
                "agents": total,
                "active": active,
                "violations": violations,
                "heuristics": heuristics,
            }
        except Exception:
            return {"score": 70, "agents": 0, "active": 0, "violations": 0, "heuristics": 0}

    def _get_heuristic_count(self) -> int:
        try:
            from apps.learn.heuristics import extract_heuristics
            return len(extract_heuristics())
        except Exception:
            return 0

    def simulate(self, proposal: dict) -> dict:
        impact = proposal.get("estimated_impact", "low")
        impact_map = {"high": 10, "medium": 5, "low": 2, "none": 0}
        delta = impact_map.get(impact, 0)

        proposed_score = round(self.current_score["score"] + delta, 1)

        return {
            "current_score": self.current_score,
            "proposed_score": proposed_score,
            "delta": round(delta, 1),
            "improvement_pct": round((delta / max(self.current_score["score"], 1)) * 100, 1),
            "impact": impact,
            "recommendation": "approve" if delta >= 5 else "review" if delta >= 2 else "reject",
        }
