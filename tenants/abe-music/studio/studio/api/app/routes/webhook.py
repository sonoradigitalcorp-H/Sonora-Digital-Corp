from fastapi import APIRouter, HTTPException, Request
import json
from app.db import update_task, get_task
from app.services.storage import storage

router = APIRouter()

@router.post("/studio/webhook")
async def webhook_handler(req: Request):
    body = await req.json()
    task_id = body.get("id")
    status = body.get("status")

    if not task_id:
        return {"received": False, "error": "missing id"}

    if status == "completed":
        data = body.get("data", {})
        results = data.get("results", [])
        result_url = results[0] if results else None

        permanent_url = None
        if result_url:
            try:
                permanent_url = await storage.save_video(task_id, result_url)
            except Exception as e:
                print(f"Storage save failed: {e}")

        update_task(task_id, {
            "status": "completed",
            "result_url": permanent_url or result_url,
            "processing_time": data.get("processing_time"),
            "result_expires_at": data.get("video_expires_at"),
            "billing_status": "charged",
            "completed_at": "datetime('now')"
        })

    elif status == "failed":
        data = body.get("data", {})
        update_task(task_id, {
            "status": "failed",
            "failed_reason": data.get("failed_reason", "unknown"),
            "billing_status": "refunded",
            "completed_at": "datetime('now')"
        })

    return {"received": True}
