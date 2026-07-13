from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI(title="ABE Studio Webhook")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STUDIO_API_URL = "http://studio-api:3020"

@app.post("/studio/webhook")
async def webhook(req: Request):
    body = await req.json()
    print(f"[Webhook] Received: {body.get('status')} for task {body.get('id')}")
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{STUDIO_API_URL}/studio/webhook", json=body)
        return resp.json()

@app.get("/health")
async def health():
    return {"status": "ok", "service": "abe-studio-webhook"}
