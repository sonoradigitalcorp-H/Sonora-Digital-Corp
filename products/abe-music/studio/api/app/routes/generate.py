import json, uuid
from fastapi import APIRouter, HTTPException
from app.models import GenerateRequest
from app.services.seedance import seedance
from app.db import create_task, update_task
from app.config import settings

router = APIRouter()

@router.post("/studio/generate")
async def generate(req: GenerateRequest):
    inp = req.input
    gen_type = inp.get("generation_type", "text-to-video")

    # Guardar en DB
    task_id = create_task({
        **inp,
        "model": req.model,
        "callback_url": req.callback_url or settings.webhook_base_url
    })

    # Preparar payload para Seedance
    payload = {
        "model": req.model,
        "input": inp
    }
    if req.callback_url:
        payload["callback_url"] = req.callback_url
    else:
        payload["callback_url"] = f"{settings.webhook_base_url}/studio/webhook"

    try:
        result = await seedance.create_generation(payload)
        seedance_task_id = result["taskId"]
        credits = result.get("credits", 0)
        update_task(task_id, {
            "seedance_task_id": seedance_task_id,
            "credits": credits,
            "status": "generating"
        })
        return {"taskId": task_id, "seedanceTaskId": seedance_task_id, "credits": credits}
    except Exception as e:
        update_task(task_id, {"status": "failed", "failed_reason": str(e)})
        raise HTTPException(502, f"Seedance error: {str(e)}")
