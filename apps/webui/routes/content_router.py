"""
Content Pipeline API — Generate and deliver content across multiple formats.
"""

import logging, uuid, json, time
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

import importlib.util
_LF_PATH = Path(__file__).resolve().parent.parent.parent.parent / "sonora-enterprise-os" / "scripts" / "instrument-langfuse.py"
if _LF_PATH.exists():
    _spec = importlib.util.spec_from_file_location("instrument_langfuse", str(_LF_PATH))
    _instr = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_instr)
    _tracker = _instr._tracker
else:
    _tracker = None

log = logging.getLogger("jarvis.webui.content")
router = APIRouter(prefix="/api/content", tags=["content"])

content_store = {}


class GenerateRequest(BaseModel):
    template: str
    topic: str = ""
    text: str = ""
    research: str = ""
    script: str = ""
    voice: str = ""
    formats: list = []
    data: dict = {}


class DeliverRequest(BaseModel):
    channel: str
    content_id: str = ""


@router.post("/generate")
async def generate_content(req: GenerateRequest):
    """Generate content from template. Called by n8n workflows."""
    start = time.time()
    cid = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    if _tracker:
        _tracker.trace(
            name="content.generate.start",
            input={"template": req.template, "topic": req.topic[:100], "tenant": "sdc-core"},
            tenant="sdc-core", agent="content.pipeline",
        )

    # Route to appropriate template
    if req.template == "daily-research":
        from src.core.rag import rag

        result = rag.search(req.topic, limit=5)
        content = {
            "id": cid,
            "type": "research",
            "topic": req.topic,
            "created_at": now,
            "research": result.get("synthesis", result.get("results", [])),
            "sources": result.get("results", [])[:3],
        }
    elif req.template == "video-script":
        from src.core.llm import ask

        script = ask(
            f"Escribe un guión de video de 30 segundos sobre: {req.topic or req.text[:200]}"
        )
        content = {"id": cid, "type": "script", "script": script, "created_at": now}
    elif req.template == "podcast":
        from src.core.llm import ask
        from voice.tts import text_to_speech

        podcast_text = ask(
            f"Convierte este texto en guión de podcast: {req.text[:500]}"
        )
        audio_url = text_to_speech(podcast_text, voice=req.voice or "en-US-AriaNeural")
        content = {
            "id": cid,
            "type": "podcast",
            "text": podcast_text,
            "audio_url": audio_url,
            "created_at": now,
        }
    elif req.template == "article":
        from src.core.llm import ask

        article = ask(f"Escribe un artículo educativo basado en: {req.research[:1000]}")
        content = {"id": cid, "type": "article", "article": article, "created_at": now}
    elif req.template == "save-to-engram":
        from src.core.engram import engram

        summary = str(req.data)[:500]
        engram.store_learning(
            "content-pipeline", "content:generated", summary, json.dumps(req.data)
        )
        content = {"id": cid, "type": "memory", "status": "saved", "created_at": now}
    else:
        content = {
            "id": cid,
            "type": "unknown",
            "template": req.template,
            "created_at": now,
        }

    content_store[cid] = content

    if _tracker:
        duration = (time.time() - start) * 1000
        _tracker.trace(
            name="content.generate.done",
            input={},
            output={"content_type": content.get("type", "unknown"), "content_id": cid},
            tenant="sdc-core", agent="content.pipeline",
            duration_ms=duration,
            metadata={"template": req.template, "topic": req.topic[:100]},
        )

    return {"status": "ok", "content_id": cid, **content}


@router.post("/deliver")
async def deliver_content(req: DeliverRequest):
    """Deliver content to a channel. Called by n8n workflows."""
    content = content_store.get(
        req.content_id, {"id": req.content_id, "fallback": True}
    )

    if req.channel == "email":
        log.info(f"📧 Email deliver: {req.content_id}")
        # In production: call Brevo API
    elif req.channel == "telegram":
        log.info(f"📨 Telegram deliver: {req.content_id}")
        # In production: call Telegram bot
    elif req.channel == "whatsapp":
        log.info(f"💬 WhatsApp deliver: {req.content_id}")

    return {
        "status": "delivered",
        "channel": req.channel,
        "content_id": req.content_id,
        "delivered_at": datetime.now().isoformat(),
    }


@router.get("/templates")
async def list_templates():
    return {
        "templates": [
            "daily-research",
            "video-script",
            "podcast",
            "article",
            "save-to-engram",
        ]
    }
