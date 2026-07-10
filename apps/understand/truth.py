import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

CONSTITUTION_DIR = Path("constitution")


def load_constitution() -> dict:
    rules = {}
    if not CONSTITUTION_DIR.exists():
        return rules
    for f in sorted(CONSTITUTION_DIR.iterdir()):
        if f.suffix in (".yaml", ".yml", ".md"):
            try:
                content = f.read_text()
                rules[f.stem] = {"path": str(f), "size": len(content), "preview": content[:200]}
            except Exception as e:
                logger.warning("Failed to read %s: %s", f.name, e)
    return rules


def verify_against_constitution(data: dict) -> dict:
    rules = load_constitution()
    checks = {
        "has_policy": "policy" in data or "policies" in data,
        "has_owner": "agent" in data or "owner" in data,
        "has_timestamp": "timestamp" in data or "collected_at" in data,
    }
    return {
        "constitution_files": len(rules),
        "checks_passed": sum(1 for v in checks.values() if v),
        "checks_total": len(checks),
        "check_results": checks,
        "compliant": all(checks.values()),
    }
