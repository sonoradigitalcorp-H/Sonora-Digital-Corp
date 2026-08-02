from fastapi import APIRouter, HTTPException
from app.db import get_task

router = APIRouter()

@router.get("/studio/tasks/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return {
        "id": task["id"],
        "status": task["status"],
        "seedanceTaskId": task.get("seedance_task_id"),
        "model": task["model"],
        "credits": task["credits"],
        "resultUrl": task.get("result_url"),
        "failedReason": task.get("failed_reason"),
        "createdAt": task["created_at"],
        "completedAt": task.get("completed_at")
    }
