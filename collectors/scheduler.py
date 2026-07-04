"""Scheduler — corre todos los collectors activos segun registry"""
import asyncio
import json
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTRY = REPO / "collectors" / "registry.yaml"
STATE_DIR = REPO / "collectors" / "state"
EMIT_SCRIPT = REPO / "scripts" / "emit-event.py"

COLLECTOR_MAP = {}

# Auto-register available collectors
_collector_path = Path(__file__).parent
for _subdir in _collector_path.iterdir():
    if _subdir.is_dir() and (_subdir / "collector.py").exists():
        _module_path = f"collectors.{_subdir.name}.collector"
        try:
            import importlib
            _mod = importlib.import_module(_module_path)
            for _attr in dir(_mod):
                _cls = getattr(_mod, _attr)
                if isinstance(_cls, type) and hasattr(_cls, 'platform') and _cls.platform:
                    COLLECTOR_MAP[_cls.platform] = _cls
        except Exception:
            pass


def load_registry():
    if not REGISTRY.exists():
        print(f"[scheduler] No registry at {REGISTRY}")
        return {"platforms": {}, "artists": []}
    with open(REGISTRY) as f:
        return yaml.safe_load(f)


def register_collector(platform, cls):
    COLLECTOR_MAP[platform] = cls


async def run_collector(platform, config, artist):
    if platform not in COLLECTOR_MAP:
        print(f"[scheduler] No collector registered for {platform}")
        return

    artist_id = artist["id"]
    platform_config = artist.get("platforms", {}).get(platform)
    if not platform_config:
        print(f"[scheduler] {artist_id} has no {platform} ID")
        return

    print(f"[scheduler] Collecting {platform} for {artist_id}...")
    collector_cls = COLLECTOR_MAP[platform]
    collector = collector_cls(state_dir=STATE_DIR)

    try:
        raw = await collector.collect(platform_config)
        print(f"[scheduler]  Got {len(raw)} raw metrics from {platform}")

        from collectors.base import Normalizer, MetricsEngine
        normalizer = Normalizer()
        normalized = normalizer.normalize_batch(raw)
        print(f"[scheduler]  Normalized to {len(normalized)} metrics")

        history = MetricsEngine.load_history(STATE_DIR / "history.json")
        engine = MetricsEngine(history=history)
        derived = engine.calculate(normalized, artist_id)
        print(f"[scheduler]  Calculated {len(derived)} derived metrics")

        engine.save_history(STATE_DIR / "history.json")
        collector.update_state(artist_id)

        # Emit event
        try:
            import subprocess
            subprocess.run(
                [sys.executable, str(EMIT_SCRIPT),
                 "--event", "collector.completed",
                 "--kernel", "observe",
                 "--agent", f"collector-{platform}",
                 "--subject-type", "artist",
                 "--subject-id", artist_id,
                 "--payload", json.dumps({
                     "platform": platform,
                     "artist": artist_id,
                     "raw_metrics": len(raw),
                     "normalized": len(normalized),
                     "derived": len(derived),
                 })],
                capture_output=True, timeout=5
            )
        except Exception:
            pass

    except Exception as e:
        print(f"[scheduler]  ERROR: {e}")
        try:
            import subprocess
            subprocess.run(
                [sys.executable, str(EMIT_SCRIPT),
                 "--event", "collector.failed",
                 "--kernel", "observe",
                 "--agent", f"collector-{platform}",
                 "--subject-type", "artist",
                 "--subject-id", artist_id,
                 "--payload", json.dumps({"error": str(e)})],
                capture_output=True, timeout=5
            )
        except Exception:
            pass


async def run_all(dry_run=False):
    registry = load_registry()
    platforms = {k: v for k, v in registry.get("platforms", {}).items() if v.get("enabled")}
    artists = registry.get("artists", [])

    print(f"[scheduler] Running {len(platforms)} platforms for {len(artists)} artists")

    if dry_run:
        for pname, pconfig in platforms.items():
            for artist in artists:
                pid = artist.get("platforms", {}).get(pname)
                print(f"  Would collect {pname} for {artist['id']} (ID: {pid})")
        print("[scheduler] Dry run complete")
        return

    tasks = []
    for pname, pconfig in platforms.items():
        for artist in artists:
            if pname in artist.get("platforms", {}):
                tasks.append(run_collector(pname, pconfig, artist))

    if tasks:
        await asyncio.gather(*tasks)

    print("[scheduler] All collectors done")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Artist Intelligence Scheduler")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected")
    parser.add_argument("--platform", help="Run only this platform")
    args = parser.parse_args()

    if args.dry_run:
        asyncio.run(run_all(dry_run=True))
    else:
        asyncio.run(run_all())


if __name__ == "__main__":
    main()
