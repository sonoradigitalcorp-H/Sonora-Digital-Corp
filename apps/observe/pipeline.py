import asyncio
import importlib
import importlib.util
import logging
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

REGISTRY_PATH = Path("collectors/registry.yaml")
EVENTS_PATH = Path("state/events/events.jsonl")


def load_registry() -> dict | None:
    if not REGISTRY_PATH.exists():
        logger.warning("Collector registry not found at %s", REGISTRY_PATH)
        return None
    with open(REGISTRY_PATH) as f:
        return yaml.safe_load(f)


def emit_event(event_type: str, payload: dict) -> None:
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "event": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    with open(EVENTS_PATH, "a") as f:
        f.write(yaml.dump(entry, sort_keys=False))
    logger.info("Event emitted: %s", event_type)


async def run_collector(platform: str, artist_id: str) -> dict | None:
    try:
        collector_path = Path(f"collectors/{platform}")
        if not collector_path.exists():
            logger.warning("Collector %s not found", platform)
            return None

        spec = importlib.util.spec_from_file_location(
            f"collectors.{platform}", collector_path / "main.py"
        )
        if spec is None or spec.loader is None:
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if not hasattr(module, "collect"):
            logger.warning("Collector %s has no collect() function", platform)
            return None

        data = await module.collect(artist_id)
        return data
    except Exception as e:
        logger.error("Collector %s failed for %s: %s", platform, artist_id, e)
        return None


def normalize(platform: str, raw: dict, registry: dict) -> dict:
    mapping = registry.get("normalization", {}).get(platform, {})
    result = {"platform": platform, "_raw": raw}
    for raw_key, normalized_key in mapping.items():
        if raw_key in raw:
            result[normalized_key] = raw[raw_key]
    return result


async def run_pipeline() -> dict:
    registry = load_registry()
    if not registry:
        return {"status": "no_registry", "collected": 0, "errors": []}

    results = []
    errors = []

    for artist in registry.get("artists", []):
        artist_id = artist["id"]
        for platform, platform_config in registry.get("platforms", {}).items():
            if not platform_config.get("enabled"):
                continue
            artist_ref = artist.get("platforms", {}).get(platform)
            if not artist_ref:
                continue

            raw = await run_collector(platform, artist_ref)
            if raw is None:
                errors.append({"artist": artist_id, "platform": platform})
                continue

            normalized = normalize(platform, raw, registry)
            emit_event(f"artist.data_collected.{platform}", {
                "artist_id": artist_id,
                "data": normalized,
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
            results.append({"artist": artist_id, "platform": platform, "status": "ok"})

    return {
        "status": "completed",
        "collected": len(results),
        "errors": errors,
        "results": results,
    }
