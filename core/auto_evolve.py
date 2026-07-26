#!/usr/bin/env python3
"""Auto-Evolve Loop — The central improvement cycle for Sonora OS.

Pipeline:
    sessions → learner → score → pattern_detector → proposals → apply → verify → report

The loop runs:
  - On demand (run_once)
  - Daily via systemd timer (run_daily)
  - Low-risk proposals are auto-applied
  - A report is generated and stored
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from evolution.learner import Learner
from evolution.pattern_detector import PatternDetector
from evolution.proposal_generator import ProposalGenerator
from evolution.client_learner import ClientLearner

logger = logging.getLogger(__name__)

STATE_DIR = REPO / "state" / "evolution"
REPORT_FILE = STATE_DIR / "report.json"
STATUS_FILE = STATE_DIR / "status.json"
LOW_RISK_THRESHOLD = 0.6


class AutoEvolve:
    """The evolution loop. Runs the full improvement pipeline."""

    def __init__(
        self,
        learner: Optional[Learner] = None,
        pattern_detector: Optional[PatternDetector] = None,
        proposal_generator: Optional[ProposalGenerator] = None,
        client_learner: Optional[ClientLearner] = None,
    ):
        self.learner = learner or Learner()
        self.pattern_detector = pattern_detector or PatternDetector()
        self.proposal_generator = proposal_generator or ProposalGenerator()
        self.client_learner = client_learner or ClientLearner()
        STATE_DIR.mkdir(parents=True, exist_ok=True)

    def run_once(self) -> dict:
        scored = self.learner.score_all_pending()
        metrics = self.learner.get_metrics()

        metrics["_sessions"] = self.learner.store.get_all()
        skills_dir = REPO / "skills"
        metrics["_skills"] = [p.stem for p in skills_dir.glob("*.skill.md")] if skills_dir.exists() else []

        patterns = self.pattern_detector.analyze(metrics)
        proposals = self.proposal_generator.generate(patterns)

        client_analysis = self.client_learner.analyze_all()
        niche_insights = self.client_learner.get_niche_insights()

        applied = []
        for prop in proposals:
            risk = prop.get("risk", "medium")
            if risk == "low":
                result = self.auto_apply(prop)
                applied.append(result)

        enterprise_score = self._run_enterprise_score()

        report = self._build_report(scored, metrics, patterns, proposals, applied, enterprise_score,
                                     client_analysis=client_analysis, niche_insights=niche_insights)
        self._save_report(report)

        return report

    def auto_apply(self, proposal: dict) -> dict:
        risk = proposal.get("risk", "medium")
        if risk != "low":
            return {
                "proposal_id": proposal.get("proposal_id"),
                "status": "skipped",
                "reason": f"risk level '{risk}' requires human review",
            }

        proposal["status"] = "applied"
        proposal["applied_at"] = datetime.now(timezone.utc).isoformat()
        self.proposal_generator.save_proposal(proposal)

        logger.info("Auto-applied proposal %s: %s", proposal.get("proposal_id"), proposal.get("title"))
        return {
            "proposal_id": proposal.get("proposal_id"),
            "status": "applied",
            "title": proposal.get("title"),
            "estimated_score_impact": proposal.get("estimated_score_impact"),
        }

    def run_daily(self) -> dict:
        report = self.run_once()
        self._notify(report)
        return report

    def status(self) -> dict:
        state = {}
        if STATUS_FILE.exists():
            try:
                state = json.loads(STATUS_FILE.read_text())
            except (json.JSONDecodeError, OSError):
                pass

        metrics = self.learner.get_metrics()
        patterns = self.pattern_detector.get_patterns()
        pending = self.proposal_generator.list_proposals(status="pending")

        client_stats = self.client_learner.analyze_all()
        return {
            "last_run": state.get("last_run", "never"),
            "total_sessions": metrics.get("total_sessions", 0),
            "overall_success_rate": metrics.get("overall_success_rate", 0),
            "patterns_found": len(patterns),
            "pending_proposals": len(pending),
            "reports_generated": state.get("reports_generated", 0),
            "proposals_applied": state.get("proposals_applied", 0),
            "enterprise_score": state.get("enterprise_score"),
            "clients_tracked": client_stats.get("total_clients", 0),
            "client_interactions": client_stats.get("total_interactions", 0),
        }

    def get_report(self) -> str:
        if not REPORT_FILE.exists():
            return "No evolution report generated yet."

        try:
            data = json.loads(REPORT_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return "Error reading evolution report."

        lines = [
            "=" * 60,
            "EVOLUTION REPORT",
            "=" * 60,
            f"  Timestamp:        {data.get('timestamp', 'N/A')}",
            f"  Sessions scored:  {data.get('sessions_scored', 0)}",
            f"  Patterns found:   {data.get('patterns_found', 0)}",
            f"  Proposals gen:    {data.get('proposals_generated', 0)}",
            f"  Proposals applied:{data.get('proposals_applied', 0)}",
            f"  Success rate:     {data.get('overall_success_rate', 0):.1%}",
            f"  Enterprise score: {data.get('enterprise_score', {}).get('enterprise_score', 'N/A')}",
            "-" * 60,
            "",
        ]

        patterns = data.get("patterns", [])
        if patterns:
            lines.append("  Patterns Detected:")
            for p in patterns[:10]:
                lines.append(f"    [{p.get('type', '?')}] {p.get('title', '?')} "
                             f"(confidence: {p.get('confidence', 0):.0%})")
            lines.append("")

        proposals = data.get("proposals", [])
        if proposals:
            lines.append("  Proposals Generated:")
            for p in proposals[:10]:
                lines.append(f"    [{p.get('type', '?')}] {p.get('title', '?')} "
                             f"(risk: {p.get('risk', '?')}, impact: +{p.get('estimated_score_impact', 0)})")
            lines.append("")

        applied = data.get("applied", [])
        if applied:
            lines.append("  Auto-Applied:")
            for a in applied:
                lines.append(f"    ✅ {a.get('proposal_id', '?')} — {a.get('title', '?')}")
            lines.append("")

        enterprise = data.get("enterprise_score", {})
        if enterprise:
            lines.append(f"  Enterprise Score: {enterprise.get('enterprise_score', 'N/A')}/100")
            if enterprise.get("threshold_met"):
                lines.append("  Threshold (>=60): PASS")
            else:
                lines.append("  Threshold (>=60): FAIL")
            lines.append("")

        client = data.get("client_analysis")
        if client:
            lines.append("  Client Learning:")
            lines.append(f"    Clients:       {client.get('total_clients', 0)}")
            lines.append(f"    Interactions:  {client.get('total_interactions', 0)}")
            lines.append(f"    Niches:        {client.get('niche_count', 0)}")
            insights = client.get("niche_insights", [])
            if insights:
                lines.append("    Niche Insights:")
                for ins in insights[:5]:
                    lines.append(f"      • {ins.get('insight', '')}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _run_enterprise_score(self) -> dict:
        try:
            from metrics.enterprise_score import compute_enterprise_score
            return compute_enterprise_score()
        except Exception as e:
            logger.warning("Enterprise score computation failed: %s", e)
            return {"enterprise_score": 0, "threshold_met": False, "error": str(e)}

    def _build_report(
        self, scored: int, metrics: dict, patterns: list[dict],
        proposals: list[dict], applied: list[dict], enterprise_score: dict,
        client_analysis: dict | None = None, niche_insights: list | None = None,
    ) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sessions_scored": scored,
            "total_sessions": metrics.get("total_sessions", 0),
            "overall_success_rate": metrics.get("overall_success_rate", 0),
            "patterns_found": len(patterns),
            "proposals_generated": len(proposals),
            "proposals_applied": len(applied),
            "patterns": patterns[:20],
            "proposals": proposals[:20],
            "applied": applied,
            "enterprise_score": enterprise_score,
            "client_analysis": {
                "total_clients": (client_analysis or {}).get("total_clients", 0),
                "total_interactions": (client_analysis or {}).get("total_interactions", 0),
                "niche_count": len((client_analysis or {}).get("niches", {})),
                "niche_insights": (niche_insights or [])[:10],
            } if client_analysis else None,
        }

    def _save_report(self, report: dict) -> None:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")

        status = {
            "last_run": report["timestamp"],
            "reports_generated": report.get("sessions_scored", 0) + 1,
            "proposals_applied": len(report.get("applied", [])),
            "enterprise_score": report.get("enterprise_score", {}).get("enterprise_score"),
        }
        if STATUS_FILE.exists():
            try:
                prev = json.loads(STATUS_FILE.read_text())
                status["reports_generated"] = prev.get("reports_generated", 0) + 1
                status["proposals_applied"] = prev.get("proposals_applied", 0) + len(report.get("applied", []))
            except (json.JSONDecodeError, OSError):
                pass
        STATUS_FILE.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n")

    def _notify(self, report: dict) -> None:
        n_proposals = report.get("proposals_generated", 0)
        n_applied = report.get("proposals_applied", 0)
        score = report.get("enterprise_score", {}).get("enterprise_score", "N/A")
        logger.info(
            "Evolution daily: %d proposals generated, %d auto-applied, enterprise score: %s",
            n_proposals, n_applied, score,
        )


def main():
    parser = argparse.ArgumentParser(description="Sonora Auto-Evolve Loop")
    parser.add_argument("--daily", action="store_true", help="Run daily cycle (called by systemd)")
    parser.add_argument("--once", action="store_true", help="Run one evolution cycle")
    parser.add_argument("--status", action="store_true", help="Show current evolution status")
    parser.add_argument("--report", action="store_true", help="Show last evolution report")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    evo = AutoEvolve()

    if args.status:
        s = evo.status()
        if args.json:
            print(json.dumps(s, indent=2))
        else:
            print(f"Last run:          {s['last_run']}")
            print(f"Total sessions:    {s['total_sessions']}")
            print(f"Success rate:      {s['overall_success_rate']:.1%}")
            print(f"Patterns found:    {s['patterns_found']}")
            print(f"Pending proposals: {s['pending_proposals']}")
            print(f"Proposals applied: {s['proposals_applied']}")
            if s.get("enterprise_score"):
                print(f"Enterprise score:  {s['enterprise_score']}/100")
        return

    if args.report:
        print(evo.get_report())
        return

    if args.daily:
        report = evo.run_daily()
    else:
        report = evo.run_once()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(evo.get_report())


if __name__ == "__main__":
    main()
