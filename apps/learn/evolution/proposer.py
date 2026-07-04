"""Evolution Proposer — analiza scoreboard + heuristics + economics y genera propuestas [FR1]"""
import json
import sys
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent.parent.parent


class EvolutionProposer:
    def __init__(self):
        self.last_analysis = None

    def analyze(self) -> list[dict]:
        proposals = []

        scoreboard = self._get_scoreboard()
        heuristics = self._get_heuristics()
        economics = self._get_economics()

        proposals.extend(self._propose_from_scoreboard(scoreboard))
        proposals.extend(self._propose_from_heuristics(heuristics))
        proposals.extend(self._propose_from_economics(economics))

        if not proposals:
            proposals.append({
                "type": "info",
                "title": "No improvements needed",
                "description": "System appears stable. No actionable patterns detected.",
                "estimated_impact": "none",
            })

        self.last_analysis = {
            "scoreboard_agents": len(scoreboard),
            "heuristics_count": len(heuristics),
            "proposals_generated": len(proposals),
        }
        return proposals

    def _get_scoreboard(self) -> list[dict]:
        try:
            sys.path.insert(0, str(REPO))
            from apps.measure.scoreboard import compute_scoreboard
            return compute_scoreboard()
        except Exception:
            return []

    def _get_heuristics(self) -> list[dict]:
        try:
            sys.path.insert(0, str(REPO))
            from apps.learn.heuristics import extract_heuristics
            return extract_heuristics()
        except Exception:
            return []

    def _get_economics(self) -> dict:
        try:
            eco_db = REPO / "state" / "economics.db"
            if not eco_db.exists():
                return {}
            import sqlite3
            conn = sqlite3.connect(str(eco_db))
            rows = conn.execute(
                "SELECT agent, SUM(tokens_input + tokens_output), SUM(cost_usd), COUNT(*) "
                "FROM operations GROUP BY agent"
            ).fetchall()
            conn.close()
            return {r[0]: {"tokens": r[1], "cost": r[2], "ops": r[3]} for r in rows}
        except Exception:
            return {}

    def _propose_from_scoreboard(self, scoreboard: list[dict]) -> list[dict]:
        proposals = []
        inactive = [a for a in scoreboard if a.get("status") == "inactive"]
        if inactive:
            names = ", ".join(a["agent"] for a in inactive[:3])
            proposals.append({
                "type": "improvement",
                "title": "Reactivate inactive agents",
                "description": f"Agents {names} are inactive. Review capabilities and re-enable if needed.",
                "estimated_impact": "medium",
                "source": "scoreboard",
                "data": {"inactive_agents": [a["agent"] for a in inactive]},
            })

        high_violations = [a for a in scoreboard if a.get("violations", 0) > 0]
        if high_violations:
            proposals.append({
                "type": "improvement",
                "title": "Address compliance violations",
                "description": f"{len(high_violations)} agents have violations. Audit and fix.",
                "estimated_impact": "high",
                "source": "scoreboard",
                "data": {"agents_with_violations": [{"agent": a["agent"], "count": a["violations"]} for a in high_violations[:5]]},
            })
        return proposals

    def _propose_from_heuristics(self, heuristics: list[dict]) -> list[dict]:
        proposals = []
        error_patterns = [h for h in heuristics if h.get("type") == "error_pattern"]
        recurring = [h for h in error_patterns if h.get("count", 0) >= 2]
        if recurring:
            for h in recurring[:3]:
                proposals.append({
                    "type": "fix",
                    "title": f"Fix recurring error: {h['text'][:60]}",
                    "description": f"Error pattern '{h['text'][:100]}' has occurred {h['count']} times. Consider implementing a guard.",
                    "estimated_impact": "high",
                    "source": "heuristics",
                    "data": {"pattern": h["text"], "occurrences": h["count"], "sources": h.get("sources", [])},
                })
        return proposals

    def _propose_from_economics(self, economics: dict) -> list[dict]:
        proposals = []
        if not economics:
            return proposals
        total_cost = sum(v.get("cost", 0) for v in economics.values())
        if total_cost > 10:
            high_cost = sorted(economics.items(), key=lambda x: x[1].get("cost", 0), reverse=True)[:2]
            for agent, data in high_cost:
                proposals.append({
                    "type": "optimization",
                    "title": f"Optimize {agent} costs (${data.get('cost', 0):.2f})",
                    "description": f"{agent} has the highest cost at ${data.get('cost', 0):.2f}. Review model selection.",
                    "estimated_impact": "medium",
                    "source": "economics",
                    "data": {"agent": agent, "cost": data.get("cost", 0), "operations": data.get("ops", 0)},
                })
        return proposals
