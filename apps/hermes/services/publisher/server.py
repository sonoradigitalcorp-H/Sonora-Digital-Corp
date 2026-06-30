"""
Multi-Platform Publisher Service — FastAPI
Julian Goldie-style cross-posting: YouTube + Instagram + TikTok + Twitter + LinkedIn
"""
import logging

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

app = FastAPI(title="Publisher Service", version="1.0")
log = logging.getLogger("publisher")

class VideoMetadata(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    category: str = "22"  # YouTube: People & Blogs
    privacy: str = "public"
    language: str = "es"
    
class PublishRequest(BaseModel):
    video_path: str
    metadata: VideoMetadata
    platforms: list[str] = ["youtube"]
    schedule: str | None = None

@app.post("/publish")
async def publish(request: PublishRequest, background: BackgroundTasks):
    results = {}
    
    for platform in request.platforms:
        if platform == "youtube":
            results[platform] = await _publish_youtube(request.video_path, request.metadata)
        elif platform == "instagram":
            results[platform] = await _publish_instagram(request.video_path, request.metadata)
        elif platform == "tiktok":
            results[platform] = await _publish_tiktok(request.video_path, request.metadata)
        elif platform == "twitter":
            results[platform] = await _publish_twitter(request.video_path, request.metadata)
        elif platform == "linkedin":
            results[platform] = await _publish_linkedin(request.video_path, request.metadata)
        else:
            results[platform] = {"status": "error", "message": f"Unknown platform: {platform}"}
    
    return {"status": "ok", "results": results, "platforms": request.platforms}

async def _publish_youtube(video_path: str, meta: VideoMetadata) -> dict:
    """YouTube upload via API or yt-dlp approach"""
    try:
        # Option A: YouTube Data API v3 (needs OAuth)
        # Option B: yt-dlp + cookies (less reliable but no OAuth setup needed now)
        result = {
            "status": "simulated",
            "platform": "youtube",
            "title": meta.title,
            "note": "Needs YouTube OAuth credentials for actual upload"
        }
        log.info(f"YouTube publish simulated: {meta.title}")
        return result
    except Exception as e:
        return {"status": "error", "platform": "youtube", "error": str(e)}

async def _publish_instagram(video_path: str, meta: VideoMetadata) -> dict:
    return {"status": "simulated", "platform": "instagram"}

async def _publish_tiktok(video_path: str, meta: VideoMetadata) -> dict:
    return {"status": "simulated", "platform": "tiktok"}

async def _publish_twitter(video_path: str, meta: VideoMetadata) -> dict:
    return {"status": "simulated", "platform": "twitter"}

async def _publish_linkedin(video_path: str, meta: VideoMetadata) -> dict:
    return {"status": "simulated", "platform": "linkedin"}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "publisher"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8766)
