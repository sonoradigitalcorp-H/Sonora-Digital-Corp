from fastapi import APIRouter
from app.db import get_tasks_by_status
from app.services.seedance import seedance
from app.config import settings

router = APIRouter()

@router.get("/studio/tasks/pending")
async def list_pending():
    tasks = get_tasks_by_status("generating", 20)
    return {"tasks": tasks, "count": len(tasks)}

@router.post("/studio/poll")
async def poll_tasks():
    tasks = get_tasks_by_status("generating", 10)
    results = []
    for t in tasks:
        sid = t.get("seedance_task_id")
        if not sid:
            continue
        try:
            remote = await seedance.get_task(sid)
            results.append({"taskId": t["id"], "status": remote.get("status")})
        except Exception as e:
            results.append({"taskId": t["id"], "error": str(e)})
    return {"polled": len(results), "results": results}
