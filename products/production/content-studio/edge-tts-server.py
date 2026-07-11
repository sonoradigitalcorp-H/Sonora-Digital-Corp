import hashlib
import os
from pathlib import Path

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

app = FastAPI(title="edge-tts-server")

AUDIO_DIR = Path("/tmp/edge-tts-audio")
AUDIO_DIR.mkdir(exist_ok=True)

PUBLIC_HOST = os.getenv("PUBLIC_HOST", "localhost")
PUBLIC_PORT = os.getenv("PUBLIC_PORT", "8766")


class TTSRequest(BaseModel):
    text: str
    voice: str = "es-MX-DaliaNeural"
    language: str = "es-MX"
    rate: str = "+0%"
    pitch: str = "+0Hz"


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/tts")
async def tts(req: TTSRequest):
    key = f"{req.text}|{req.voice}|{req.rate}|{req.pitch}"
    filename = f"{hashlib.md5(key.encode()).hexdigest()}.mp3"
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        communicate = edge_tts.Communicate(req.text, req.voice, rate=req.rate, pitch=req.pitch)
        await communicate.save(str(filepath))
    return {
        "url": f"http://{PUBLIC_HOST}:{PUBLIC_PORT}/audio/{filename}",
        "filename": filename,
    }


@app.get("/audio/{filename}")
async def get_audio(filename: str):
    filepath = AUDIO_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(str(filepath), media_type="audio/mpeg")
