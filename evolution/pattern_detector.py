"""Pattern Detector — Finds correlations and patterns in session data.

Pattern types detected:
  - FREQUENT_ERROR: skill X fails 40% when used without Y
  - SUCCESS_PATTERN: users who do X before Y have 90% success
  - TIME_CORRELATION: errors spike on weekends -> infrastructure?
  - SKILL_GAP: users ask for X but no skill handles it
  - REGRESSION: skill X success rate dropped from 90% to 60%
  - OPPORTUNITY: 3 users asked for same feature independently
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
PATTERNS_FILE = REPO / "state" / "evolution" / "patterns.json"
PATTERN_TYPES = {
    "FREQUENT_ERROR", "SUCCESS_PATTERN", "TIME_CORRELATION",
    "SKILL_GAP", "REGRESSION", "OPPORTUNITY",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()[:10]


def _today() -> str:
    return _now_iso()


def _read_json(path: Path) -> list:
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def _write_json(path: Path, data: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


class PatternDetector:
    """Finds correlations and patterns in session data."""

    def __init__(self, patterns_file: Optional[Path] = None):
        self.patterns_file = patterns_file or PATTERNS_FILE
        self._cached: Optional[list[dict]] = None

    def analyze(self, learner_metrics: dict) -> list[dict]:
        all_sessions = learner_metrics.get("_sessions", [])
        skills_available = learner_metrics.get("_skills", [])

        patterns = []
        patterns.extend(self.find_frequent_errors(all_sessions))
        patterns.extend(self.find_skill_gaps(all_sessions, skills_available))
        patterns.extend(self._find_success_patterns(all_sessions))

        metrics_by_day = self._metrics_by_day(learner_metrics)
        patterns.extend(self.find_regressions(metrics_by_day))

        patterns.extend(self.find_opportunities(all_sessions))
        patterns.extend(self.find_time_patterns(all_sessions))

        self._cached = patterns
        self._persist(patterns)
        return patterns

    def find_frequent_errors(self, sessions: list) -> list[dict]:
        if not sessions:
            return []

        error_counter: Counter = Counter()
        error_skills: dict[str, Counter] = defaultdict(Counter)
        total_by_skill: Counter = Counter()

        for s in sessions:
            if s.get("error"):
                err = s["error"]
                error_counter[err] += 1
                skill = s.get("skill_used", "unknown")
                error_skills[err][skill] += 1
            skill = s.get("skill_used", "unknown")
            total_by_skill[skill] += 1

        patterns = []
        for err, count in error_counter.most_common(10):
            total = len(sessions)
            if total == 0:
                continue
            rate = count / total
            if rate < 0.1:
                continue

            top_skill = error_skills[err].most_common(1)[0][0] if error_skills[err] else "unknown"
            skill_total = total_by_skill.get(top_skill, 1)
            skill_rate = count / skill_total if skill_total > 0 else 0

            suggestion = f"Add error handling for '{err}'"
            if skill_rate > 0.3:
                suggestion = f"Fix '{err}' in skill '{top_skill}' — occurs in {skill_rate:.0%} of its uses"

            patterns.append({
                "pattern_id": f"pat-freqerr-{len(patterns) + 1:03d}",
                "type": "FREQUENT_ERROR",
                "confidence": round(min(1.0, rate * 1.5), 2),
                "title": f"'{err}' is frequent ({count}x, {rate:.0%} of sessions)",
                "description": f"Error '{err}' occurred {count} times in {total} sessions ({rate:.0%}). "
                               f"Most common in skill '{top_skill}' ({skill_rate:.0%} of its uses).",
                "evidence": {
                    "sessions": [s.get("id", s.get("session_id", "")) for s in sessions if s.get("error") == err],
                    "count": count,
                    "total": total,
                    "top_skill": top_skill,
                    "skill_rate": skill_rate,
                },
                "suggestion": suggestion,
                "tags": [top_skill, "error", "blocker"] if skill_rate > 0.3 else [top_skill, "error"],
                "first_seen": _today(),
                "last_seen": _today(),
            })

        return patterns

    def find_skill_gaps(self, sessions: list, skills_available: list) -> list[dict]:
        if not sessions:
            return []

        skill_names = {s.get("name", s) if isinstance(s, dict) else s for s in skills_available}

        unknown_skill_counter: Counter = Counter()
        request_patterns = Counter()

        for s in sessions:
            skill = s.get("skill_used", "")
            if skill and skill not in skill_names:
                unknown_skill_counter[skill] += 1

            command = s.get("command", s.get("what", ""))
            if command and isinstance(command, str):
                for kw in ["create", "make", "build", "need", "want", "could you", "can you"]:
                    if kw in command.lower():
                        request_patterns[command[:80]] += 1

        patterns = []
        for skill_name, count in unknown_skill_counter.most_common(5):
            if count < 2:
                continue
            patterns.append({
                "pattern_id": f"pat-gap-{len(patterns) + 1:03d}",
                "type": "SKILL_GAP",
                "confidence": round(min(1.0, count / 10), 2),
                "title": f"Unknown skill '{skill_name}' referenced {count}x",
                "description": f"'{skill_name}' was used in {count} sessions but is not in the skill registry. "
                               f"Users may expect this capability to exist.",
                "evidence": {
                    "sessions": [s.get("id", s.get("session_id", "")) for s in sessions if s.get("skill_used") == skill_name],
                    "count": count,
                    "missing_skill": skill_name,
                },
                "suggestion": f"Consider creating skill '{skill_name}'",
                "tags": ["skill-gap", skill_name, "missing"],
                "first_seen": _today(),
                "last_seen": _today(),
            })

        return patterns

    def _find_success_patterns(self, sessions: list) -> list[dict]:
        if not sessions:
            return []

        patterns = []

        by_skill = defaultdict(list)
        for s in sessions:
            by_skill[s.get("skill_used", "unknown")].append(s)

        for skill, sList in by_skill.items():
            if len(sList) < 3:
                continue
            successes = [s for s in sList if s.get("success")]
            rate = len(successes) / len(sList) if sList else 0
            if rate >= 0.8:
                avg_duration_s = 0.0
                durations = [s.get("duration", 0) for s in successes if s.get("duration") is not None]
                if durations:
                    avg_duration_s = sum(durations) / len(durations)
                patterns.append({
                    "pattern_id": f"pat-success-{len(patterns) + 1:03d}",
                    "type": "SUCCESS_PATTERN",
                    "confidence": round(rate * (1 - 1 / len(sList)), 2),
                    "title": f"Skill '{skill}' has {rate:.0%} success rate ({len(sList)} sessions)",
                    "description": f"Skill '{skill}' succeeds {rate:.0%} of the time across {len(sList)} sessions. "
                                   f"This is a reliable capability.",
                    "evidence": {
                        "skill": skill,
                        "success_count": len(successes),
                        "total": len(sList),
                        "success_rate": rate,
                        "avg_duration_s": round(avg_duration_s, 2),
                    },
                    "suggestion": f"Promote '{skill}' as a primary capability",
                    "tags": [skill, "high-success", "reliable"],
                    "first_seen": _today(),
                    "last_seen": _today(),
                })

        return patterns

    def find_regressions(self, metrics_by_day: dict) -> list[dict]:
        patterns = []

        dates = sorted(metrics_by_day.keys())
        if len(dates) < 2:
            return patterns

        skill_trends: dict[str, list[float]] = defaultdict(list)
        for date_str in dates:
            day_data = metrics_by_day.get(date_str, {})
            for skill, info in day_data.get("by_skill", {}).items():
                skill_trends[skill].append(info.get("success_rate", 0))

        for skill, rates in skill_trends.items():
            if len(rates) < 2:
                continue
            initial = rates[0]
            latest = rates[-1]
            if initial > 0 and latest < initial - 0.15:
                drop = initial - latest
                patterns.append({
                    "pattern_id": f"pat-reg-{len(patterns) + 1:03d}",
                    "type": "REGRESSION",
                    "confidence": round(min(1.0, drop * 2), 2),
                    "title": f"Skill '{skill}' success rate dropped from {initial:.0%} to {latest:.0%}",
                    "description": f"Skill '{skill}' regressed by {drop:.0%} over {len(dates)} days. "
                                   f"Was at {initial:.0%}, now at {latest:.0%}.",
                    "evidence": {
                        "skill": skill,
                        "initial_rate": initial,
                        "latest_rate": latest,
                        "drop": round(drop, 3),
                        "days_analyzed": len(dates),
                    },
                    "suggestion": f"Audit recent changes to skill '{skill}'",
                    "tags": [skill, "regression", "degradation"],
                    "first_seen": _today(),
                    "last_seen": _today(),
                })

        return patterns

    def find_opportunities(self, sessions: list) -> list[dict]:
        if not sessions:
            return []

        patterns = []

        feature_requests = Counter()
        for s in sessions:
            command = s.get("command", s.get("what", ""))
            if not command or not isinstance(command, str):
                continue
            cmd_lower = command.lower()
            for trigger in ["can you", "create a", "add a", "need a", "could you", "feature", "integrate"]:
                if trigger in cmd_lower:
                    feature_requests[command[:120]] += 1
                    break

        for req_text, count in feature_requests.most_common(5):
            if count < 2:
                continue
            patterns.append({
                "pattern_id": f"pat-opp-{len(patterns) + 1:03d}",
                "type": "OPPORTUNITY",
                "confidence": round(min(1.0, count / 5), 2),
                "title": f"{count} users requested similar feature: '{req_text[:50]}...'",
                "description": f"'{req_text[:100]}' was requested {count} times independently. "
                               f"This indicates unmet user demand.",
                "evidence": {
                    "sessions": [s.get("id", s.get("session_id", "")) for s in sessions
                                 if req_text in s.get("command", s.get("what", ""))],
                    "count": count,
                    "request_excerpt": req_text[:100],
                },
                "suggestion": "Consider implementing this feature as a new skill or product",
                "tags": ["opportunity", "feature-request"],
                "first_seen": _today(),
                "last_seen": _today(),
            })

        return patterns

    def find_time_patterns(self, sessions: list) -> list[dict]:
        if not sessions:
            return []

        patterns = []

        weekday_sessions = defaultdict(list)
        for s in sessions:
            ts = s.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    weekday_sessions[dt.weekday()].append(s)
                except (ValueError, TypeError):
                    pass

        if not weekday_sessions:
            return patterns

        for day_name, day_sessions in weekday_sessions.items():
            errors = [s for s in day_sessions if s.get("error")]
            rate = len(errors) / len(day_sessions) if day_sessions else 0
            if rate > 0.4 and len(day_sessions) >= 3:
                patterns.append({
                    "pattern_id": f"pat-time-{len(patterns) + 1:03d}",
                    "type": "TIME_CORRELATION",
                    "confidence": round(min(1.0, rate), 2),
                    "title": f"Error rate spikes to {rate:.0%} on {['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][day_name]}",
                    "description": f"On {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'][day_name]}, "
                                   f"error rate is {rate:.0%} ({len(errors)}/{len(day_sessions)} sessions). "
                                   f"This is significantly above average.",
                    "evidence": {
                        "weekday": day_name,
                        "error_count": len(errors),
                        "total": len(day_sessions),
                        "error_rate": round(rate, 3),
                    },
                    "suggestion": "Investigate infrastructure or deployment patterns on this day",
                    "tags": ["time-pattern", "infrastructure"],
                    "first_seen": _today(),
                    "last_seen": _today(),
                })

        return patterns

    def _metrics_by_day(self, metrics: dict) -> dict:
        trend = metrics.get("improvement_trend", [])
        by_day = {}
        for entry in trend:
            date_str = entry.get("date", "")
            by_day[date_str] = {
                "success_rate": entry.get("success_rate", 0),
                "by_skill": metrics.get("by_skill", {}),
                "by_type": metrics.get("by_type", {}),
            }
        return by_day

    def get_patterns(self, force: bool = False) -> list[dict]:
        if force or self._cached is None:
            stored = _read_json(self.patterns_file)
            self._cached = stored
        return self._cached or []

    def patterns_summary(self) -> str:
        patterns = self.get_patterns()
        if not patterns:
            return "No patterns detected yet."

        by_type: Counter = Counter(p["type"] for p in patterns)
        lines = [
            "=" * 60,
            "PATTERN DETECTOR SUMMARY",
            "=" * 60,
            f"  Total patterns: {len(patterns)}",
            "",
        ]
        for ptype in sorted(by_type):
            lines.append(f"  {ptype}: {by_type[ptype]}")

        lines.append("")
        lines.append("-" * 60)
        lines.append("  Top patterns:")
        lines.append("")

        sorted_pats = sorted(patterns, key=lambda p: p.get("confidence", 0), reverse=True)
        for p in sorted_pats[:10]:
            conf_bar = "█" * int(p.get("confidence", 0) * 10)
            lines.append(f"  [{p.get('type', '?')}] {p.get('title', '?')}")
            lines.append(f"        confidence={p.get('confidence', 0):.2f} {conf_bar}")
            lines.append(f"        {p.get('suggestion', '')}")
            lines.append("")

        lines.append("=" * 60)
        return "\n".join(lines)

    def _persist(self, patterns: list[dict]) -> None:
        existing = _read_json(self.patterns_file)
        existing_ids = {p["pattern_id"] for p in existing}

        new_count = 0
        for p in patterns:
            if p["pattern_id"] not in existing_ids:
                existing.append(p)
                existing_ids.add(p["pattern_id"])
                new_count += 1

        _write_json(self.patterns_file, existing)
