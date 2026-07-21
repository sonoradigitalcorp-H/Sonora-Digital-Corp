"""Observer — Module 1 of Evolution Engine (HAS-008)
Collects metrics from all subsystems: agents, capabilities, tests, violations, memory, events.
"""
import json
import sqlite3
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent


def collect():
    metrics = {
        "agents": _count_agents(),
        "capabilities": _count_capabilities(),
        "constitution_files": _count_constitution_files(),
        "constitution_rules": _count_constitution_rules(),
        "tests_passed": 0,
        "tests_total": 0,
        "violations": 0,
        "memory_count": 0,
        "events_count": 0,
        "git_ahead": 0,
        "git_behind": 0,
    }
    metrics.update(_get_test_counts())
    metrics.update(_get_git_status())
    metrics.update(_get_memory_count())
    metrics.update(_get_events_count())
    return metrics


def _count_agents():
    registry = REPO / "agents" / "registry.yaml"
    if registry.exists():
        import yaml
        data = yaml.safe_load(registry.read_text())
        return len(data.get("agents", []))
    return 0


def _count_capabilities():
    caps_dir = REPO / "capabilities"
    if caps_dir.exists():
        return len([f for f in caps_dir.iterdir() if (f / "capability.yaml").exists()])
    return 0


def _count_constitution_files():
    const_dir = REPO / "constitution"
    if const_dir.exists():
        return len(list(const_dir.glob("*.yaml")))
    return 0


def _count_constitution_rules():
    import yaml
    const_dir = REPO / "constitution"
    total = 0
    if const_dir.exists():
        for f in const_dir.glob("*.yaml"):
            try:
                data = yaml.safe_load(f.read_text())
                total += len(data.get("rules", []))
            except Exception:
                pass
    return total


def _get_test_counts():
    db = REPO / "state" / "test_results.db"
    if db.exists():
        try:
            conn = sqlite3.connect(str(db))
            c = conn.cursor()
            c.execute("SELECT SUM(passed), SUM(total) FROM test_runs WHERE date = date('now')")
            row = c.fetchone()
            conn.close()
            if row and row[0]:
                return {"tests_passed": row[0], "tests_total": row[1]}
        except Exception:
            pass
    return {}


def _get_git_status():
    try:
        import subprocess
        ahead = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        behind = subprocess.run(
            ["git", "rev-list", "--count", "origin/main..HEAD"],
            capture_output=True, text=True, timeout=5
        ).stdout.strip()
        return {"git_ahead": int(ahead or 0), "git_behind": int(behind or 0)}
    except Exception:
        return {}


def _get_memory_count():
    db = REPO / "state" / "engram.db"
    if db.exists():
        try:
            conn = sqlite3.connect(str(db))
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM memories")
            count = c.fetchone()[0]
            conn.close()
            return {"memory_count": count}
        except Exception:
            pass
    return {}


def _get_events_count():
    events_file = REPO / "state" / "events" / "events.jsonl"
    if events_file.exists():
        try:
            with open(events_file) as f:
                count = sum(1 for _ in f)
            return {"events_count": count}
        except Exception:
            pass
    return {}
