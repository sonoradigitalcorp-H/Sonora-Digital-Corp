"""Event emitter for Decision Engine events — writes to state/events/events.jsonl."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from planner.models import CapabilityResult

log = logging.getLogger("planner.events")

BASE = Path(__file__).resolve().parent.parent
EVENTS_PATH = BASE / "state" / "events" / "events.jsonl"


def _emit(event: str, payload: dict[str, Any]):
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = json.dumps({
        "event": event,
        "producer": "decision-engine",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "payload": payload,
    })
    with open(EVENTS_PATH, "a") as f:
        f.write(entry + "\n")
    log.debug("Event: %s | %s", event, json.dumps(payload)[:150])


def emit_capability_executed(result: CapabilityResult):
    _emit("CapabilityExecuted", {
        "capability_id": result.capability_id,
        "provider_id": result.provider_id,
        "success": result.success,
        "latency_ms": round(result.latency_ms, 2),
        "cost_estimate": result.cost_estimate,
    })


def emit_provider_failed(provider_id: str, capability_id: str, error: str):
    _emit("ProviderFailed", {
        "provider_id": provider_id,
        "capability_id": capability_id,
        "error": error[:300],
    })


def emit_provider_degraded(provider_id: str, latency_ms: float, threshold_ms: float = 2000):
    _emit("ProviderDegraded", {
        "provider_id": provider_id,
        "latency_ms": round(latency_ms, 2),
        "threshold_ms": threshold_ms,
    })


def emit_provider_recovered(provider_id: str, downtime_seconds: float):
    _emit("ProviderRecovered", {
        "provider_id": provider_id,
        "downtime_seconds": round(downtime_seconds, 2),
    })


def emit_no_provider(capability_id: str):
    _emit("NoProviderAvailable", {
        "capability_id": capability_id,
    })


def emit_registry_updated(capability_count: int, provider_count: int, version: str = "2.0.0"):
    _emit("RegistryUpdated", {
        "capability_count": capability_count,
        "provider_count": provider_count,
        "version": version,
    })


def emit_sync_started(artist_count: int, capabilities: list[str]):
    _emit("SyncCycleStarted", {
        "artist_count": artist_count,
        "capabilities": capabilities,
    })


def emit_sync_completed(artists_synced: int, total_duration_ms: float):
    _emit("SyncCycleCompleted", {
        "artists_synced": artists_synced,
        "total_duration_ms": round(total_duration_ms, 2),
    })
