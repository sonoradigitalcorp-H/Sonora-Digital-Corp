import os

import httpx
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from webui.routes import (
    abe_router,
    app_router,
    approvals_router,
    brain_router,
    chat_router,
    commands_router,
    content_router,
    files_router,
    mysticverse_router,
    pages,
    payments_router,
    sales_router,
    score_router,
    sdc_router,
    sessions_router,
    skills_router,
    store_router,
    voice_router,
    webhooks_router,
    zamora_router,
)
from webui.routes.app_state import STATIC_DIR, app

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.post("/api/chat")
async def chat_proxy(request: Request):
    try:
        body = await request.json()
        messages = body.get("messages", [])
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        model = body.get("model", "openrouter/free")
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "messages": messages, "stream": False},
            )
            return r.json()
    except Exception as e:
        return {"error": str(e), "choices": [{"message": {"content": "Lo siento, ocurrió un error al procesar tu mensaje."}}]}


@app.get("/api/wa-qr")
async def wa_qr():
    try:
        async with httpx.AsyncClient() as client:
            wa_key = os.getenv("WHATSAPP_API_KEY", "MysticWA2026!")
            r = await client.get(
                "http://127.0.0.1:3001/qr",
                headers={"x-api-key": wa_key, "Accept": "application/json"},
                timeout=5,
            )
            return r.json()
    except Exception as e:
        return {"state": "error", "error": str(e)}


app.include_router(pages.router)
app.include_router(approvals_router.router)
app.include_router(sessions_router.router)
app.include_router(chat_router.router)
app.include_router(files_router.router)
app.include_router(skills_router.router)
app.include_router(sdc_router.router)
app.include_router(mysticverse_router.router)
app.include_router(payments_router.router)
app.include_router(abe_router.router)
app.include_router(commands_router.router)
app.include_router(voice_router.router)
app.include_router(webhooks_router.router)
app.include_router(brain_router.router)
app.include_router(store_router.router)
app.include_router(content_router.router)
app.include_router(zamora_router.router)
app.include_router(app_router.router)
app.include_router(sales_router.router)
app.include_router(score_router.router)


__all__ = ["app"]
