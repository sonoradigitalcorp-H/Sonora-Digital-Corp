#!/usr/bin/env python3
"""Verification Event Emitter — emite eventos de verificación al bus unificado (HAS-009)

Usage:
  python3 scripts/emit-verification-event.py \
    --event adr_verification_completed \
    --passed true \
    --details '{"count":5,"valid":3}'

  python3 scripts/emit-verification-event.py \
    --event spec_verification_completed \
    --passed true \
    --details '{"spec_id":"SPEC-001","coverage_pct":80.0}'
"""

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
EMIT_SCRIPT = REPO / "scripts" / "emit-event.py"


def emit_adr_verified(adr_id: str, passed: bool, details: dict | None = None) -> dict:
    """Emite un evento de verificación de ADR al event bus."""
    import subprocess
    payload = {
        "adr_id": adr_id,
        "passed": passed,
        "details": details or {},
    }
    result = subprocess.run(
        [
            sys.executable, str(EMIT_SCRIPT),
            "--type", "adr.verified",
            "--source", "verify-adr",
            "--subject-type", "adr",
            "--subject-id", adr_id,
            "--payload", json.dumps(payload),
        ],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        logger.error("Failed to emit adr.verified: %s", result.stderr)
        return {"success": False, "error": result.stderr}
    logger.info("Event adr.verified emitted for %s (passed=%s)", adr_id, passed)
    return {"success": True, "event": "adr.verified", "adr_id": adr_id}


def emit_spec_verified(spec_id: str, coverage: dict) -> dict:
    """Emite un evento de verificación de SPEC al event bus."""
    import subprocess
    payload = {
        "spec_id": spec_id,
        "coverage": coverage,
    }
    result = subprocess.run(
        [
            sys.executable, str(EMIT_SCRIPT),
            "--type", "spec.verified",
            "--source", "verify-adr",
            "--subject-type", "spec",
            "--subject-id", spec_id,
            "--payload", json.dumps(payload),
        ],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        logger.error("Failed to emit spec.verified: %s", result.stderr)
        return {"success": False, "error": result.stderr}
    logger.info("Event spec.verified emitted for %s", spec_id)
    return {"success": True, "event": "spec.verified", "spec_id": spec_id}


def emit_batch(events: list[dict]) -> dict:
    """Emite múltiples eventos de verificación en lote."""
    results = []
    for evt in events:
        event_type = evt.get("event", "")
        if event_type == "adr.verified":
            results.append(emit_adr_verified(
                evt.get("adr_id", "unknown"),
                evt.get("passed", False),
                evt.get("details"),
            ))
        elif event_type == "spec.verified":
            results.append(emit_spec_verified(
                evt.get("spec_id", "unknown"),
                evt.get("coverage", {}),
            ))
        else:
            results.append({"success": False, "error": f"Unknown event type: {event_type}"})
    return {"success": all(r["success"] for r in results), "results": results}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Emit verification events (HAS-009)")
    parser.add_argument("--event", required=True,
                        choices=["adr_verification_completed", "spec_verification_completed",
                                 "adr.verified", "spec.verified"],
                        help="Event type")
    parser.add_argument("--passed", default="true", choices=["true", "false"],
                        help="Whether verification passed")
    parser.add_argument("--details", default="{}", help="JSON details payload")
    parser.add_argument("--adr-id", help="ADR ID for adr.verified events")
    parser.add_argument("--spec-id", help="SPEC ID for spec.verified events")
    args = parser.parse_args()

    details = json.loads(args.details)
    passed = args.passed == "true"

    event_type = args.event
    if event_type == "adr_verification_completed":
        event_type = "adr.verified"
    elif event_type == "spec_verification_completed":
        event_type = "spec.verified"

    if event_type == "adr.verified":
        result = emit_adr_verified(args.adr_id or "batch", passed, details)
    elif event_type == "spec.verified":
        result = emit_spec_verified(args.spec_id or "batch", details)
    else:
        logger.error("Unknown event type: %s", event_type)
        sys.exit(1)

    if not result.get("success"):
        sys.exit(1)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
