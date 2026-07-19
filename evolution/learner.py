"""Learner Engine — Scores sessions and extracts learning metrics.

Metrics extracted:
  - success_rate by command type
  - avg_duration by skill used
  - most_common_errors
  - improvement_over_time (is the system getting better?)
  - skill_effectiveness (which skills lead to best outcomes)
  - user_satisfaction_proxy (success rate per user)

Each session gets a score (0-10) based on:
  - success (boolean): 4 points if true
  - duration (vs average): 0-3 points
  - error details: -2 if error
  - user rephrase (if user had to clarify): -1
  - outcome completeness: 0-3 points
"""
import json
import statistics
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class SessionStore:
    """Default file-based session store."""

    def __init__(self, sessions_file=None):
        self.sessions_file = Path(sessions_file) if sessions_file else REPO / "state" / "sessions.jsonl"

    def get_all(self) -> list[dict]:
        if not self.sessions_file.exists():
            return []
        sessions = []
        with open(self.sessions_file) as f:
            for line in f:
                if line.strip():
                    sessions.append(json.loads(line))
        return sessions

    def get_unscored(self) -> list[dict]:
        return [s for s in self.get_all() if s.get("score") is None]

    def mark_scored(self, session_id: str, score: int) -> bool:
        sessions = self.get_all()
        updated = False
        with open(self.sessions_file, "w") as f:
            for s in sessions:
                if s.get("id") == session_id:
                    s["score"] = score
                    s["scored_at"] = datetime.now(timezone.utc).isoformat()
                    updated = True
                f.write(json.dumps(s) + "\n")
        return updated

    def save_session(self, session: dict) -> None:
        with open(self.sessions_file, "a") as f:
            f.write(json.dumps(session) + "\n")


class Learner:
    """Reads sessions, scores them, extracts learning metrics."""

    def __init__(self, store=None):
        self.store = store or SessionStore()

    def score_session(self, session: dict) -> int:
        score = 0

        if session.get("success"):
            score += 4

        duration = session.get("duration")
        if duration is not None:
            all_durations = [
                s.get("duration", 0) or 0
                for s in self.store.get_all()
                if s.get("duration") is not None
            ]
            avg_duration = statistics.mean(all_durations) if all_durations else duration
            ratio = duration / max(avg_duration, 0.001)
            if ratio < 0.5:
                score += 3
            elif ratio < 0.8:
                score += 2
            elif ratio < 1.0:
                score += 1

        if session.get("error"):
            score -= 2

        if session.get("user_rephrase"):
            score -= 1

        completeness = session.get("outcome_completeness", 0)
        score += min(max(completeness, 0), 3)

        return max(0, min(score, 10))

    def score_all_pending(self) -> int:
        unscored = self.store.get_unscored()
        count = 0
        for session in unscored:
            score = self.score_session(session)
            self.store.mark_scored(session["id"], score)
            count += 1
        return count

    def get_metrics(self) -> dict:
        sessions = self.store.get_all()
        scored = [s for s in sessions if s.get("score") is not None]
        unscored = [s for s in sessions if s.get("score") is None]
        total = len(sessions)

        if not scored:
            return {
                "total_sessions": total,
                "scored": 0,
                "unscored": len(unscored),
                "overall_success_rate": 0.0,
                "by_type": {},
                "by_skill": {},
                "common_errors": [],
                "improvement_trend": [],
                "top_skills": [],
                "by_user": {},
            }

        success_count = sum(1 for s in scored if s.get("success"))
        overall_success_rate = round(success_count / len(scored), 3)

        by_type = defaultdict(lambda: {"count": 0, "success_count": 0, "durations": []})
        by_skill = defaultdict(lambda: {"count": 0, "success_count": 0, "scores": []})
        by_user = defaultdict(lambda: {"count": 0, "success_count": 0})
        errors = Counter()
        daily = defaultdict(lambda: {"total": 0, "success": 0})

        for s in scored:
            cmd_type = s.get("command_type", "unknown")
            by_type[cmd_type]["count"] += 1
            if s.get("success"):
                by_type[cmd_type]["success_count"] += 1
            dur = s.get("duration")
            if dur is not None:
                by_type[cmd_type]["durations"].append(dur)

            skill = s.get("skill_used", "unknown")
            by_skill[skill]["count"] += 1
            if s.get("success"):
                by_skill[skill]["success_count"] += 1
            score_val = s.get("score", 0)
            by_skill[skill]["scores"].append(score_val)

            user = s.get("user", "unknown")
            by_user[user]["count"] += 1
            if s.get("success"):
                by_user[user]["success_count"] += 1

            if s.get("error"):
                errors[s["error"]] += 1

            ts = s.get("timestamp", "")
            day = ts[:10] if ts else "unknown"
            daily[day]["total"] += 1
            if s.get("success"):
                daily[day]["success"] += 1

        by_type_out = {}
        for cmd, data in by_type.items():
            avg_dur = round(statistics.mean(data["durations"]), 2) if data["durations"] else 0.0
            by_type_out[cmd] = {
                "count": data["count"],
                "success_rate": round(data["success_count"] / data["count"], 3),
                "avg_duration": avg_dur,
            }

        by_skill_out = {}
        for skill, data in by_skill.items():
            by_skill_out[skill] = {
                "count": data["count"],
                "success_rate": round(data["success_count"] / data["count"], 3),
                "avg_score": round(statistics.mean(data["scores"]), 2),
            }

        by_user_out = {}
        for user, data in by_user.items():
            by_user_out[user] = {
                "count": data["count"],
                "success_rate": round(data["success_count"] / data["count"], 3),
            }

        common_errors = [
            {"error": err, "count": cnt}
            for err, cnt in errors.most_common(10)
        ]

        today = datetime.now(timezone.utc)
        improvement_trend = []
        for i in range(6, -1, -1):
            day = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            if day in daily:
                d = daily[day]
                rate = round(d["success"] / d["total"], 3) if d["total"] > 0 else 0.0
                improvement_trend.append({"date": day, "success_rate": rate})
            else:
                improvement_trend.append({"date": day, "success_rate": 0.0})

        top_skills = sorted(
            [
                {"name": skill, "success_rate": data["success_rate"], "count": data["count"]}
                for skill, data in by_skill_out.items()
            ],
            key=lambda x: (x["success_rate"], x["count"]),
            reverse=True,
        )

        return {
            "total_sessions": total,
            "scored": len(scored),
            "unscored": len(unscored),
            "overall_success_rate": overall_success_rate,
            "by_type": by_type_out,
            "by_skill": by_skill_out,
            "common_errors": common_errors,
            "improvement_trend": improvement_trend,
            "top_skills": top_skills,
            "by_user": by_user_out,
        }

    def generate_report(self, format: str = "text") -> str:
        metrics = self.get_metrics()

        if format == "json":
            return json.dumps(metrics, indent=2)

        if format == "markdown":
            lines = ["# Learner Report\n"]
            lines.append(f"- **Total Sessions**: {metrics['total_sessions']}")
            lines.append(f"- **Scored**: {metrics['scored']}")
            lines.append(f"- **Unscored**: {metrics['unscored']}")
            lines.append(f"- **Overall Success Rate**: {metrics['overall_success_rate']:.1%}\n")

            lines.append("## By Command Type\n")
            lines.append("| Type | Count | Success Rate | Avg Duration |")
            lines.append("|------|-------|-------------|--------------|")
            for cmd, data in sorted(metrics["by_type"].items()):
                lines.append(f"| {cmd} | {data['count']} | {data['success_rate']:.1%} | {data['avg_duration']}s |")

            lines.append("\n## By Skill\n")
            lines.append("| Skill | Count | Success Rate | Avg Score |")
            lines.append("|-------|-------|-------------|-----------|")
            for skill, data in sorted(metrics["by_skill"].items()):
                lines.append(f"| {skill} | {data['count']} | {data['success_rate']:.1%} | {data['avg_score']} |")

            if metrics["common_errors"]:
                lines.append("\n## Common Errors\n")
                for e in metrics["common_errors"]:
                    lines.append(f"- **{e['error']}**: {e['count']} occurrences")

            if metrics["improvement_trend"]:
                lines.append("\n## Improvement Trend\n")
                lines.append("| Date | Success Rate |")
                lines.append("|------|-------------|")
                for t in metrics["improvement_trend"]:
                    bars = "█" * int(t["success_rate"] * 20)
                    lines.append(f"| {t['date']} | {t['success_rate']:.1%} {bars}")

            return "\n".join(lines)

        lines = ["=" * 60]
        lines.append("LEARNER REPORT")
        lines.append("=" * 60)
        lines.append(f"  Total Sessions:  {metrics['total_sessions']}")
        lines.append(f"  Scored:          {metrics['scored']}")
        lines.append(f"  Unscored:        {metrics['unscored']}")
        lines.append(f"  Success Rate:    {metrics['overall_success_rate']:.1%}")
        lines.append("-" * 60)

        lines.append("\n  By Command Type:")
        for cmd, data in sorted(metrics["by_type"].items()):
            lines.append(f"    {cmd:20s}  {data['count']:3d} sessions  {data['success_rate']:.0%} success  {data['avg_duration']}s avg")

        lines.append("\n  By Skill:")
        for skill, data in sorted(metrics["by_skill"].items()):
            lines.append(f"    {skill:20s}  {data['count']:3d} uses  {data['success_rate']:.0%} success  score={data['avg_score']}")

        if metrics["common_errors"]:
            lines.append("\n  Common Errors:")
            for e in metrics["common_errors"][:5]:
                lines.append(f"    {e['error']:30s}  x{e['count']}")

        lines.append("\n  Improvement Trend (last 7 days):")
        for t in metrics["improvement_trend"]:
            bars = "█" * int(t["success_rate"] * 20)
            lines.append(f"    {t['date']}  {t['success_rate']:.0%} {bars}")

        lines.append("\n  Top Skills:")
        for skill in metrics["top_skills"][:5]:
            lines.append(f"    {skill['name']:20s}  {skill['success_rate']:.0%} ({skill['count']} sessions)")

        lines.append("=" * 60)
        return "\n".join(lines)

    def get_improvement_tip(self) -> str:
        metrics = self.get_metrics()

        if metrics["scored"] == 0:
            return "No sessions scored yet. Start scoring to get improvement tips."

        if metrics["common_errors"]:
            top_error = metrics["common_errors"][0]
            return (
                f"Fix '{top_error['error']}' — it's the most frequent error "
                f"({top_error['count']} occurrences). "
                "Consider adding better error handling or retry logic."
            )

        low_skills = [s for s in metrics["top_skills"][-3:] if s["success_rate"] < 0.5]
        if low_skills:
            return (
                f"Skill '{low_skills[-1]['name']}' has low success rate "
                f"({low_skills[-1]['success_rate']:.0%}). "
                "Review its configuration or update its prompts."
            )

        if metrics["overall_success_rate"] < 0.6:
            return "Overall success rate is below 60%. Consider auditing recent changes or rolling back problematic deployments."

        if metrics["improvement_trend"]:
            recent = metrics["improvement_trend"][-1]["success_rate"]
            if recent < 0.5:
                return "Recent success rate is dropping. Check for regressions in the latest sessions."

        improving = True
        rates = [t["success_rate"] for t in metrics["improvement_trend"] if t["success_rate"] > 0]
        if len(rates) >= 2:
            for i in range(1, len(rates)):
                if rates[i] < rates[i - 1]:
                    improving = False
                    break
            if improving:
                return "System is improving steadily. Keep up the good work!"

        return "No specific patterns detected. Continue monitoring."
