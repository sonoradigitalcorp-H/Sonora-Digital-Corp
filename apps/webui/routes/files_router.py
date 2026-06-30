import subprocess

from fastapi import APIRouter, HTTPException
from webui.routes.app_state import PROJECT_DIR

router = APIRouter()


@router.get("/api/files")
async def list_files(path: str = "."):
    try:
        target = PROJECT_DIR / path
        if not target.exists():
            raise HTTPException(status_code=404, detail=f"Path not found: {path}")
        if target.is_file():
            content = target.read_text(encoding="utf-8", errors="replace")
            return {
                "type": "file",
                "name": target.name,
                "path": str(target.relative_to(PROJECT_DIR)),
                "size": target.stat().st_size,
                "content": content[:50000],
            }
        items = []
        for entry in sorted(target.iterdir()):
            if entry.name.startswith(".") or entry.name.startswith("__"):
                continue
            items.append(
                {
                    "name": entry.name,
                    "path": str(entry.relative_to(PROJECT_DIR)),
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else 0,
                }
            )
        return {
            "type": "directory",
            "name": target.name,
            "path": str(target.relative_to(PROJECT_DIR)),
            "items": items,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/files/git")
async def git_status():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR),
            timeout=5,
        )
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_DIR),
            timeout=5,
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line:
                files.append({"status": line[:2].strip(), "file": line[3:]})
        return {
            "branch": branch.stdout.strip(),
            "dirty": len(files) > 0,
            "files": files[:50],
        }
    except Exception as e:
        return {"error": str(e), "branch": "unknown", "dirty": False, "files": []}
