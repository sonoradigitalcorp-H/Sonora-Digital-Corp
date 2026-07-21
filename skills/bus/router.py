import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("capabilities/index.yaml")


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        logger.warning("Capability registry not found at %s", REGISTRY_PATH)
        return {"capabilities": []}
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f) or {"capabilities": []}


def get_capability(id: str) -> dict | None:
    registry = load_registry()
    for cap in registry.get("capabilities", []):
        if cap["id"] == id:
            return cap
    return None


def _build_capability_profile(cap: dict) -> dict:
    id_parts = set(cap["id"].split("-"))
    desc = cap.get("description", "").lower()
    desc_words = {w for w in desc.replace(",", "").split() if len(w) > 3}
    domain = cap.get("domain", "")
    cap_type = cap.get("type", "")
    return {
        "id_parts": id_parts,
        "desc_words": desc_words,
        "domain": domain,
        "type": cap_type,
    }


def _build_profiles() -> dict[str, dict]:
    registry = load_registry()
    profiles = {}
    for cap in registry.get("capabilities", []):
        profiles[cap["id"]] = _build_capability_profile(cap)
    return profiles


def match_intent(query: str) -> tuple[str | None, float]:
    query_lower = query.lower().strip()
    query_words = {w for w in query_lower.split() if len(w) > 2}
    profiles = _build_profiles()

    best_id = None
    best_score = 0.0

    for cap_id, profile in profiles.items():
        id_matches = query_words & profile["id_parts"]
        desc_matches = query_words & profile["desc_words"]
        domain_match = 1 if profile["domain"] in query_lower else 0
        type_match = 1 if profile["type"] in query_lower else 0

        score = (len(id_matches) * 3.0) + (len(desc_matches) * 1.0) + domain_match + type_match
        if score > best_score:
            best_score = score
            best_id = cap_id

    if best_id and best_score > 0:
        confidence = min(best_score / 10.0, 1.0)
        return best_id, confidence
    return None, 0.0


def validate_policies(capability: dict, context: dict) -> dict:
    checks = []
    cost_tier = capability.get("cost_tier", 1)
    if cost_tier >= 4 and not context.get("approved"):
        checks.append({"policy": "cost", "passed": False, "reason": f"Costo alto (tier {cost_tier}) requiere aprobación"})
    else:
        checks.append({"policy": "cost", "passed": True})

    if capability.get("status") == "experimental" and not context.get("allow_experimental"):
        checks.append({"policy": "stability", "passed": False, "reason": "Capability experimental no permitida sin flag"})
    else:
        checks.append({"policy": "stability", "passed": True})

    required_agent = capability.get("agent")
    caller_agent = context.get("agent")
    if required_agent and caller_agent and caller_agent != required_agent:
        checks.append({"policy": "agent", "passed": False, "reason": f"Requiere agent={required_agent}, recibió {caller_agent}"})
    else:
        checks.append({"policy": "agent", "passed": True})

    all_passed = all(c["passed"] for c in checks)
    return {"passed": all_passed, "checks": checks}


def route(query: str, context: dict | None = None) -> dict:
    context = context or {}
    cap_id, confidence = match_intent(query)
    if not cap_id:
        return {"status": "no_match", "query": query, "confidence": 0.0}

    capability = get_capability(cap_id)
    if not capability:
        return {"status": "capability_not_found", "capability": cap_id}

    policy_result = validate_policies(capability, context)
    if not policy_result["passed"]:
        return {
            "status": "policy_blocked",
            "capability": cap_id,
            "confidence": confidence,
            "policies": policy_result,
        }

    return {
        "status": "routed",
        "capability": cap_id,
        "domain": capability.get("domain"),
        "agent": capability.get("agent"),
        "cost_tier": capability.get("cost_tier"),
        "confidence": confidence,
        "policies": policy_result,
    }
