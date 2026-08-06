"""create-backup — Ops Harness: backup de state crítico con verificación.
Usage: python -m ops.backup
"""
import json
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
BACKUP_DIR = BASE / "state" / "backups"

DIRECTORIES = [
    "state/registry",
    "state/events",
    "state/ops",
    "agents",
    "config",
    "skills/process",
    "harnesses",
]

RETENTION_DAYS = 30


def emit(event_type: str, payload: dict):
    try:
        from events.emitter import emit_sync
        emit_sync(event_type, payload, "ops-agent")
    except ImportError:
        pass


def create_backup() -> Path:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    archive = BACKUP_DIR / f"sdc-backup-{ts}.tar.gz"

    with tarfile.open(archive, "w:gz") as tar:
        for rel_path in DIRECTORIES:
            src = BASE / rel_path
            if src.exists():
                tar.add(src, arcname=rel_path)
                print(f"  Added: {rel_path}")

    return archive


def verify_backup(path: Path) -> bool:
    try:
        with tarfile.open(path, "r:gz") as tar:
            members = tar.getmembers()
        valid = len(members) > 0
        print(f"  Files in archive: {len(members)}")
        return valid
    except Exception as e:
        print(f"  Verification failed: {e}")
        return False


def cleanup_old():
    cutoff = datetime.now(timezone.utc).timestamp() - (RETENTION_DAYS * 86400)
    removed = 0
    for f in BACKUP_DIR.glob("sdc-backup-*.tar.gz"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    if removed:
        print(f"  Cleaned {removed} old backup(s)")


def run():
    print("=== SDC Backup ===")
    print(f"Output: {BACKUP_DIR}")

    archive = create_backup()
    size_mb = archive.stat().st_size / 1024 / 1024
    print(f"Created: {archive.name} ({size_mb:.1f} MB)")

    print("Verifying...")
    valid = verify_backup(archive)

    if valid:
        emit("system:backup:created", {
            "path": str(archive),
            "size_mb": round(size_mb, 2),
            "directories": DIRECTORIES,
        })
        print("✅ Backup verified")
    else:
        emit("system:backup:failed", {
            "path": str(archive),
            "error": "verification failed",
        })
        print("❌ Backup verification FAILED")
        sys.exit(1)

    cleanup_old()
    print("Done.")


if __name__ == "__main__":
    run()
