"""
Thumbnail Generator Service — FastAPI
Generates modern, high-CTR thumbnails for YouTube/TikTok
"""
import logging
import os
import random

from fastapi import FastAPI, HTTPException
from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

app = FastAPI(title="Thumbnail Generator", version="1.0")
log = logging.getLogger("thumbnails")

TEMPLATES = {
    "modern": {"bg": "#1a1a2e", "accent": "#FFD700", "gradient": True},
    "minimal": {"bg": "#0a0a0a", "accent": "#ffffff", "gradient": False},
    "bold": {"bg": "#ff0000", "accent": "#ffffff", "gradient": True},
    "tech": {"bg": "#0d1117", "accent": "#58a6ff", "gradient": True},
}

OUTPUT_DIR = "/home/mystic/sonora-digital-corp/data/thumbnails"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class ThumbnailRequest(BaseModel):
    title: str
    subtitle: str = ""
    style: str = "modern"
    width: int = 1280
    height: int = 720
    emoji: str = "⚡"

@app.post("/generate")
async def generate_thumbnail(req: ThumbnailRequest):
    try:
        style = TEMPLATES.get(req.style, TEMPLATES["modern"])
        img = Image.new("RGB", (req.width, req.height), style["bg"])
        draw = ImageDraw.Draw(img)
        
        # Gradient overlay
        if style.get("gradient"):
            for i in range(req.height):
                alpha = int(255 * (1 - i / req.height))
                color = tuple(int(style["accent"][i:i+2], 16) for i in (1, 3, 5))
                overlay = Image.new("RGB", (req.width, 1), color)
                overlay.putalpha(alpha)
                img.paste(overlay, (0, i), overlay)
        
        # Try loading fonts, fallback to default
        font_large = None
        font_small = None
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
        except Exception:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Emoji
        draw.text((40, 40), req.emoji, fill=style["accent"], font=font_large)
        
        # Title text
        draw.text((40, 180), req.title, fill="white", font=font_large)
        if req.subtitle:
            draw.text((40, 260), req.subtitle, fill=style["accent"], font=font_small)
        
        # Bottom bar
        draw.rectangle([0, req.height-8, req.width, req.height], fill=style["accent"])
        
        # Save
        filename = f"{req.title.replace(' ', '_')[:30]}_{random.randint(1000,9999)}.png"
        path = os.path.join(OUTPUT_DIR, filename)
        img.save(path)
        
        return {"status": "ok", "path": path, "filename": filename, "size": f"{req.width}x{req.height}"}
    
    except Exception as e:
        log.error(f"Thumbnail generation failed: {e}")
        raise HTTPException(500, str(e)) from e

@app.get("/health")
async def health():
    return {"status": "ok", "service": "thumbnails"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
