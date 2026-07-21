from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from clients.talking_head import generate_talking_head
from clients.tts_client import generate_tts
from clients.lora_client import train_lora, generate_with_lora

app = FastAPI(title="FAL Wrapper - Clon Digital")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TalkingHeadRequest(BaseModel):
    image_url: str
    audio_url: str
    face_restoration: bool = True
    upscale: bool = True
    model: str = "sync-lipsync-v3"

class TTSRequest(BaseModel):
    text: str
    reference_audio: Optional[str] = None
    language: str = "es"
    voice: str = "seed-audio"

class LoRATrainRequest(BaseModel):
    image_urls: list[str]
    trigger_word: str = "person"
    name: Optional[str] = None

class LoRAInferRequest(BaseModel):
    prompt: str
    lora_url: str
    trigger_word: str = "person"
    num_images: int = 1

@app.post("/v1/talking-head")
async def talking_head(req: TalkingHeadRequest):
    try:
        result = generate_talking_head(
            image_url=req.image_url,
            audio_url=req.audio_url,
            face_restoration=req.face_restoration,
            upscale=req.upscale,
            model=req.model,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"Talking head generation failed: {str(e)}")

@app.post("/v1/tts")
async def tts(req: TTSRequest):
    try:
        result = generate_tts(
            text=req.text,
            reference_audio=req.reference_audio,
            language=req.language,
            voice=req.voice,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"TTS generation failed: {str(e)}")

@app.post("/v1/train-lora")
async def train_lora_endpoint(req: LoRATrainRequest):
    try:
        result = train_lora(
            image_urls=req.image_urls,
            trigger_word=req.trigger_word,
            name=req.name,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"LoRA training failed: {str(e)}")

@app.post("/v1/generate-with-lora")
async def generate_with_lora_endpoint(req: LoRAInferRequest):
    try:
        result = generate_with_lora(
            prompt=req.prompt,
            lora_url=req.lora_url,
            trigger_word=req.trigger_word,
            num_images=req.num_images,
        )
        return result
    except Exception as e:
        raise HTTPException(500, f"LoRA inference failed: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "fal-wrapper"}
