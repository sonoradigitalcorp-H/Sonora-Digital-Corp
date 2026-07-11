import asyncio
import hashlib
import json
import os
import uuid
from pathlib import Path

import asyncpg
import httpx
import redis.asyncio as aioredis
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("sdc-content-server", port=8765)

DB_DSN = os.getenv("CONTENT_DB_DSN", "postgresql://sdc:sdc@localhost:5432/sdc_content")
CORE_DB_DSN = os.getenv("CORE_DB_DSN", "postgresql://sdc:sdc@localhost:5432/sdc")
FAL_KEY = os.getenv("FAL_KEY", "")
AGNES_API_KEY = os.getenv("AGNES_API_KEY", "")
AGNES_API_URL = "https://api.agnes.ai/v1"
FAL_API_BASE = "https://fal.run"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
PUBLIC_HOST = os.getenv("PUBLIC_HOST", "149.56.46.173")
STORAGE_BASE = Path(os.getenv("STORAGE_BASE", "/data/content"))
OMNIVOICE_URL = os.getenv("OMNIVOICE_URL", "http://localhost:3900")

_pool: asyncpg.Pool | None = None
_core_pool: asyncpg.Pool | None = None
_redis: aioredis.Redis | None = None


async def _get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DB_DSN, min_size=1, max_size=4)
    return _pool


async def _get_core_pool() -> asyncpg.Pool:
    global _core_pool
    if _core_pool is None:
        _core_pool = await asyncpg.create_pool(CORE_DB_DSN, min_size=1, max_size=4)
    return _core_pool


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            password=REDIS_PASSWORD or None,
            decode_responses=True,
        )
    return _redis


async def _db(sql: str, *args) -> list[asyncpg.Record]:
    pool = await _get_pool()
    async with pool.acquire() as conn:
        if args:
            return await conn.fetch(sql, *args)
        return await conn.fetch(sql)


async def _download_to_local(url: str, subdir: str, artist_id: str, ext: str = "jpg") -> str:
    if not url:
        return ""
    filename = f"{uuid.uuid4().hex}.{ext}"
    dest_dir = STORAGE_BASE / subdir / (artist_id or "unknown")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / filename
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.get(url)
        if r.status_code == 200:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, dest_path.write_bytes, r.content)
    public_url = f"http://{PUBLIC_HOST}:8768/{subdir}/{(artist_id or 'unknown')}/{filename}"
    return public_url


async def _download_bytes(url: str) -> bytes | None:
    if not url:
        return None
    try:
        async with httpx.AsyncClient(timeout=120) as cl:
            r = await cl.get(url)
            if r.status_code == 200:
                return r.content
    except Exception:
        return None
    return None


@mcp.tool()
async def generate_image(
    prompt: str,
    artist_id: str | None = None,
    template_id: str | None = None,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    use_lora: bool = False,
) -> dict:
    aid = artist_id or "unknown"
    if AGNES_API_KEY:
        return await _generate_agnes(prompt, negative_prompt, width, height, aid)
    if FAL_KEY:
        return await _generate_fal(prompt, negative_prompt, aid, use_lora)
    return {"error": "No API key configured (set AGNES_API_KEY or FAL_KEY)"}


async def _generate_agnes(prompt: str, neg: str, w: int, h: int, artist_id: str = "") -> dict:
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            f"{AGNES_API_URL}/images/generations",
            headers={"Authorization": f"Bearer {AGNES_API_KEY}"},
            json={
                "prompt": prompt,
                "negative_prompt": neg,
                "width": w,
                "height": h,
                "model": "flux-schnell",
                "num_images": 1,
            },
        )
        data = r.json()
        url = data.get("data", [{}])[0].get("url", "")
        local_url = await _download_to_local(url, "images", artist_id, "jpg")
        return {"provider": "agnes", "url": local_url or url, "cost": 0, "model": "flux-schnell"}


async def _generate_fal(prompt: str, neg: str, artist_id: str = "", use_lora: bool = False) -> dict:
    payload: dict = {"prompt": prompt, "negative_prompt": neg, "num_images": 1}
    endpoint = f"{FAL_API_BASE}/fal-ai/flux/schnell"

    if use_lora:
        endpoint = f"{FAL_API_BASE}/fal-ai/flux-lora"
        rows = await _db(
            "SELECT path, scale FROM lora_weights WHERE artist_id = $1 AND active = TRUE ORDER BY created_at DESC LIMIT 5;",
            artist_id,
        )
        if rows:
            payload["lora_weights"] = [{"path": r["path"], "scale": float(r["scale"])} for r in rows]

    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            endpoint,
            headers={"Authorization": f"Key {FAL_KEY}"},
            json=payload,
        )
        data = r.json()
        url = data.get("images", [{}])[0].get("url", "")
        local_url = await _download_to_local(url, "images", artist_id, "jpg")
        return {"provider": "fal", "url": local_url or url, "cost": 0, "model": "flux-lora" if use_lora else "flux-schnell"}


@mcp.tool()
async def register_lora_weights(
    artist_id: str,
    path: str,
    scale: float = 0.8,
    name: str = "default",
) -> dict:
    sql = """
        INSERT INTO lora_weights (artist_id, name, path, scale)
        VALUES ($1, $2, $3, $4) RETURNING id;
    """
    try:
        rows = await _db(sql, artist_id, name, path, scale)
        return {"lora_weight_id": str(rows[0]["id"]), "status": "active"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def list_lora_weights(artist_id: str | None = None) -> list[dict]:
    if artist_id:
        rows = await _db(
            "SELECT id, name, path, scale, active, created_at FROM lora_weights WHERE artist_id = $1 ORDER BY created_at DESC;",
            artist_id,
        )
    else:
        rows = await _db(
            "SELECT id, artist_id, name, path, scale, active, created_at FROM lora_weights ORDER BY created_at DESC;"
        )
    return [dict(r) for r in rows]


@mcp.tool()
async def delete_lora_weights(weight_id: str) -> dict:
    await _db("UPDATE lora_weights SET active = FALSE WHERE id = $1;", weight_id)
    return {"status": "deleted"}


@mcp.tool()
async def edit_image(
    prompt: str,
    image_url: str,
    mask_url: str | None = None,
    artist_id: str | None = None,
) -> dict:
    aid = artist_id or "unknown"
    if not FAL_KEY:
        return {"error": "FAL key not configured"}
    payload: dict = {"prompt": prompt, "image_url": image_url, "num_images": 1}
    if mask_url:
        payload["mask_url"] = mask_url
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            f"{FAL_API_BASE}/fal-ai/flux-pro/v1/fill",
            headers={"Authorization": f"Key {FAL_KEY}"},
            json=payload,
        )
        data = r.json()
        url = data.get("images", [{}])[0].get("url", "")
        local_url = await _download_to_local(url, "images", aid, "jpg")
        return {"provider": "fal", "url": local_url or url, "cost": 0, "model": "flux-fill-pro"}


@mcp.tool()
async def generate_talking_head(
    image_url: str,
    script: str = "",
    audio_url: str = "",
    provider: str = "muapi",
    artist_id: str | None = None,
) -> dict:
    aid = artist_id or "unknown"
    if provider == "muapi":
        if script:
            return await _talking_head_muapi_script(image_url, script, aid)
        return await _talking_head_muapi_lipsync(image_url, audio_url, aid)
    return await _talking_head_fal(image_url, audio_url, aid)


async def _talking_head_fal(image_url: str, audio_url: str, artist_id: str = "") -> dict:
    if not FAL_KEY:
        return {"error": "FAL key not configured"}
    async with httpx.AsyncClient(timeout=300) as cl:
        r = await cl.post(
            f"{FAL_API_BASE}/fal-ai/sadtalker",
            headers={"Authorization": f"Key {FAL_KEY}"},
            json={"source_image_url": image_url, "driven_audio_url": audio_url},
        )
        data = r.json()
        video = data.get("video", {}) or data.get("output", {})
        url = video.get("url", "")
        local_url = await _download_to_local(url, "video", artist_id, "mp4")
        return {"provider": "fal", "url": local_url or url, "cost": 0.01}


async def _talking_head_muapi_script(image_url: str, script: str, artist_id: str = "") -> dict:
    muapi_key = os.getenv("MUAPI_KEY", "")
    if not muapi_key:
        return {"error": "Muapi key not configured"}
    async with httpx.AsyncClient(timeout=300) as cl:
        r = await cl.post(
            "https://api.muapi.ai/api/v1/infinitetalk-image-to-video",
            headers={"Authorization": f"Bearer {muapi_key}"},
            json={"image_url": image_url, "script": script},
        )
        data = r.json()
        url = data.get("outputs", [{}])[0].get("url", "")
        local_url = await _download_to_local(url, "video", artist_id, "mp4")
        return {"provider": "muapi", "model": "infinitetalk", "url": local_url or url, "cost": 0.20}


async def _talking_head_muapi_lipsync(image_url: str, audio_url: str, artist_id: str = "") -> dict:
    muapi_key = os.getenv("MUAPI_KEY", "")
    if not muapi_key:
        return {"error": "Muapi key not configured"}
    async with httpx.AsyncClient(timeout=300) as cl:
        r = await cl.post(
            "https://api.muapi.ai/api/v1/creatify-lipsync",
            headers={"Authorization": f"Bearer {muapi_key}"},
            json={"face_image_url": image_url, "audio_url": audio_url},
        )
        data = r.json()
        url = data.get("outputs", [{}])[0].get("url", "")
        local_url = await _download_to_local(url, "video", artist_id, "mp4")
        return {"provider": "muapi", "model": "creatify-lipsync", "url": local_url or url, "cost": 0.04}


@mcp.tool()
async def text_to_speech(
    text: str,
    voice_id: str = "es-MX-DaliaNeural",
    language: str = "es-MX",
    provider: str = "edge",
    artist_id: str | None = None,
) -> dict:
    aid = artist_id or "unknown"
    if provider == "edge":
        return await _tts_edge(text, voice_id, language, aid)
    elif provider == "openai":
        return await _tts_openai(text)
    return await _tts_edge(text, voice_id, language, aid)


async def _tts_edge(text: str, voice_id: str, lang: str, artist_id: str = "") -> dict:
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            "http://localhost:8766/tts",
            json={"text": text, "voice": voice_id, "language": lang},
        )
        if r.status_code != 200:
            return await _tts_openai(text)
        data = r.json()
        audio_url = data.get("url", "")
        local_url = await _download_to_local(audio_url, "audio", artist_id, "mp3")
        return {"provider": "edge", "url": local_url or audio_url, "cost": 0}


async def _tts_openai(text: str) -> dict:
    openai_key = os.getenv("OPENAI_API_KEY", "")
    if not openai_key:
        return {"error": "No TTS available (edge-tts failed and no OpenAI key)"}
    async with httpx.AsyncClient(timeout=120) as cl:
        r = await cl.post(
            "https://api.openai.com/v1/audio/speech",
            headers={"Authorization": f"Bearer {openai_key}"},
            json={
                "model": "tts-1",
                "input": text,
                "voice": "alloy",
                "response_format": "mp3",
            },
        )
        if r.status_code != 200:
            return {"error": f"OpenAI TTS failed: {r.text}"}
        return {"provider": "openai", "cost": 0.015}


@mcp.tool()
async def clone_voice(
    artist_id: str,
    audio_urls: list[str],
    name: str = "default",
    language: str = "es",
) -> dict:
    if not audio_urls:
        return {"error": "At least one audio_url required"}
    audio_bytes = await _download_bytes(audio_urls[0])
    if not audio_bytes:
        return {"error": f"Failed to download audio from {audio_urls[0]}"}
    audio_ext = os.path.splitext(audio_urls[0].split("?")[0])[1] or ".wav"
    if audio_ext not in (".wav", ".mp3", ".ogg", ".m4a", ".flac"):
        audio_ext = ".wav"
    try:
        async with httpx.AsyncClient(timeout=300) as cl:
            files = {
                "ref_audio": (f"ref{audio_ext}", audio_bytes, "audio/wav"),
            }
            data = {
                "name": name,
                "ref_text": "",
                "language": language,
                "kind": "clone",
            }
            r = await cl.post(
                f"{OMNIVOICE_URL}/profiles",
                data=data,
                files=files,
            )
            if r.status_code not in (200, 201):
                body = r.text[:500]
                return {"error": f"OmniVoice API returned {r.status_code}: {body}"}
            profile = r.json()
    except Exception as e:
        return {"error": f"OmniVoice API call failed: {str(e)}"}

    profile_id = profile.get("id", "")
    if not profile_id:
        return {"error": "OmniVoice did not return a profile id"}
    sql = """
        INSERT INTO voice_profiles (artist_id, name, provider, voice_id, language, is_cloned, sample_audio_url)
        VALUES ($1, $2, 'omnivoice', $3, $4, TRUE, $5)
        RETURNING id;
    """
    try:
        rows = await _db(sql, artist_id, name, profile_id, language, json.dumps(audio_urls))
        return {
            "voice_profile_id": str(rows[0]["id"]),
            "voice_id": profile_id,
            "provider": "omnivoice",
            "status": "cloned",
        }
    except Exception as e:
        return {"error": f"DB insert failed: {str(e)}", "omnivoice_profile_id": profile_id}


@mcp.tool()
async def ocr_image(
    image_url: str,
    language: str = "es",
    artist_id: str | None = None,
) -> dict:
    image_bytes = await _download_bytes(image_url)
    if not image_bytes:
        return {"error": "Failed to download image"}
    tmp_dir = STORAGE_BASE / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_dir / f"ocr_{uuid.uuid4().hex}.jpg"
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, tmp_path.write_bytes, image_bytes)
    try:
        import easyocr
        reader = await loop.run_in_executor(
            None,
            lambda: easyocr.Reader([language], gpu=False),
        )
        results = await loop.run_in_executor(None, lambda: reader.readtext(str(tmp_path)))
        text_parts = []
        entries = []
        for bbox, text, confidence in results:
            text_parts.append(text)
            entries.append({"text": text, "confidence": round(confidence, 3), "bbox": bbox})
        full_text = "\n".join(text_parts)
        ext = ".txt"
        ocr_dir = STORAGE_BASE / "ocr" / (artist_id or "unknown")
        ocr_dir.mkdir(parents=True, exist_ok=True)
        ocr_path = ocr_dir / f"{uuid.uuid4().hex}{ext}"
        await loop.run_in_executor(None, ocr_path.write_text, full_text)
        return {
            "text": full_text,
            "entries": entries,
            "language": language,
            "char_count": len(full_text),
        }
    except ImportError:
        return {"error": "easyocr not installed. Install with: pip install easyocr"}
    except Exception as e:
        return {"error": f"OCR failed: {str(e)}"}
    finally:
        if tmp_path.exists():
            await loop.run_in_executor(None, tmp_path.unlink)


@mcp.tool()
async def queue_content(
    artist_id: str,
    prompt: str,
    media_type: str = "image",
    template_id: str | None = None,
    platform: str = "telegram",
    nsfw: bool = False,
    schedule_hours: int = 0,
) -> dict:
    gen_id = str(uuid.uuid4())
    gen_sql = """
        INSERT INTO generations (id, artist_id, template_id, media_type, prompt, nsfw)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id;
    """
    queue_sql = """
        INSERT INTO content_queue (artist_id, generation_id, platform,
            scheduled_for, status)
        VALUES ($1, $2, $3,
            CASE WHEN $4 > 0 THEN now() + ($4 || ' hours')::interval ELSE now() END,
            'pending')
        RETURNING id;
    """
    try:
        gen_rows = await _db(gen_sql, gen_id, artist_id, template_id, media_type, prompt, nsfw)
        queue_rows = await _db(queue_sql, artist_id, gen_id, platform, schedule_hours)
        return {
            "generation_id": str(gen_rows[0]["id"]),
            "queue_id": str(queue_rows[0]["id"]),
            "status": "queued",
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def process_queue(batch_size: int = 1) -> dict:
    r = await _get_redis()
    queue_key = "content:queue:pending"
    processed = 0
    for _ in range(batch_size):
        item = await _db("""
            SELECT cq.id, cq.generation_id, cq.platform,
                   g.prompt, g.media_type, g.artist_id
            FROM content_queue cq
            JOIN generations g ON g.id = cq.generation_id
            WHERE cq.status = 'pending'
              AND (cq.scheduled_for IS NULL OR cq.scheduled_for <= now())
            ORDER BY cq.priority DESC, cq.created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED;
        """)
        if not item:
            break
        item = item[0]
        await _db("UPDATE content_queue SET status = 'running' WHERE id = $1;", item["id"])
        gen_id = str(item["generation_id"])
        await _db("UPDATE generations SET status = 'processing' WHERE id = $1;", gen_id)
        result = await generate_image(item["prompt"], str(item["artist_id"]))
        if result.get("url"):
            await _db(
                "UPDATE generations SET status = 'completed', output_urls = $1, completed_at = now() WHERE id = $2;",
                json.dumps([result["url"]]), gen_id,
            )
            await _db(
                "UPDATE content_queue SET status = 'completed', published_at = now() WHERE id = $1;",
                item["id"],
            )
            await r.publish("content:generated", json.dumps({
                "queue_id": str(item["id"]),
                "generation_id": gen_id,
                "url": result["url"],
                "platform": item["platform"],
            }))
            payload = {
                "event": "generation.completed",
                "generation_id": gen_id,
                "artist_id": str(item["artist_id"]),
                "url": result["url"],
                "media_type": item["media_type"],
                "platform": item["platform"],
            }
            asyncio.create_task(_deliver_webhooks("generation.completed", gen_id, payload))
            processed += 1
        else:
            await _db("UPDATE generations SET status = 'failed', error = $1 WHERE id = $2;",
                      result.get("error", "unknown"), gen_id)
            await _db("UPDATE content_queue SET status = 'failed' WHERE id = $1;", item["id"])
    return {"processed": processed}


@mcp.tool()
async def get_generation_status(generation_id: str) -> dict:
    rows = await _db("SELECT * FROM generations WHERE id = $1;", generation_id)
    if not rows:
        return {"error": "not found"}
    return dict(rows[0])


@mcp.tool()
async def list_templates(category: str | None = None) -> list[dict]:
    if category:
        rows = await _db(
            "SELECT id, name, category, engine, cost_estimate_usd, virality_score, is_nsfw FROM templates WHERE category = $1 ORDER BY virality_score DESC;",
            category,
        )
    else:
        rows = await _db(
            "SELECT id, name, category, engine, cost_estimate_usd, virality_score, is_nsfw FROM templates ORDER BY virality_score DESC;"
        )
    return [dict(r) for r in rows]


@mcp.tool()
async def list_artists() -> list[dict]:
    pool = await _get_core_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT id, name, genre, status, streams, revenue FROM artists ORDER BY name;")
    return [dict(r) for r in rows]


@mcp.tool()
async def get_product_tiers() -> list[dict]:
    rows = await _db(
        "SELECT id, name, price_usd, setup_fee_usd, max_generations, has_lora, has_voice_clone, has_nsfw, white_label FROM product_tiers ORDER BY price_usd;"
    )
    return [dict(r) for r in rows]


@mcp.tool()
async def get_artist_summary(artist_id: str) -> dict:
    core_pool = await _get_core_pool()
    async with core_pool.acquire() as conn:
        artist = await conn.fetch("SELECT * FROM artists WHERE id = $1;", artist_id)
    stats = await _db(
        """
        SELECT
            COUNT(*) FILTER (WHERE status = 'completed') as completed,
            COUNT(*) FILTER (WHERE status = 'queued') as queued,
            COUNT(*) FILTER (WHERE status = 'failed') as failed,
            COALESCE(SUM(cost_usd), 0) as total_cost
        FROM generations WHERE artist_id = $1;
        """,
        artist_id,
    )
    return {
        "artist": dict(artist[0]) if artist else None,
        "generations": dict(stats[0]) if stats else {},
    }


@mcp.tool()
async def create_template(
    name: str,
    category: str,
    prompt_template: str,
    engine: str = "agnes",
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 30,
    cfg_scale: float = 7.0,
    use_lora: bool = False,
    use_voice: bool = False,
    is_nsfw: bool = False,
) -> dict:
    sql = """
        INSERT INTO templates (name, category, engine, prompt_template, negative_prompt,
            width, height, steps, cfg_scale, use_lora, use_voice, is_nsfw)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        RETURNING id;
    """
    try:
        rows = await _db(
            sql,
            name,
            category,
            engine,
            prompt_template,
            negative_prompt,
            width,
            height,
            steps,
            cfg_scale,
            use_lora,
            use_voice,
            is_nsfw,
        )
        return {"id": str(rows[0]["id"]), "name": name}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def register_webhook(
    artist_id: str,
    url: str,
    secret: str = "",
    events: list[str] | None = None,
) -> dict:
    if events is None:
        events = ["generation.completed"]
    sql = """
        INSERT INTO content_webhooks (artist_id, url, secret, events)
        VALUES ($1, $2, $3, $4) RETURNING id;
    """
    try:
        rows = await _db(sql, artist_id, url, secret, events)
        return {"webhook_id": str(rows[0]["id"]), "status": "active"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
async def list_webhooks(artist_id: str | None = None) -> list[dict]:
    if artist_id:
        rows = await _db("SELECT * FROM content_webhooks WHERE artist_id = $1 AND active = TRUE;", artist_id)
    else:
        rows = await _db("SELECT * FROM content_webhooks WHERE active = TRUE;")
    return [dict(r) for r in rows]


@mcp.tool()
async def delete_webhook(webhook_id: str) -> dict:
    await _db("UPDATE content_webhooks SET active = FALSE WHERE id = $1;", webhook_id)
    return {"status": "deleted"}


async def _deliver_webhooks(event: str, generation_id: str, payload: dict):
    wh_rows = await _db(
        "SELECT id, url, secret FROM content_webhooks WHERE $1 = ANY(events) AND active = TRUE;",
        event,
    )
    for wh in wh_rows:
        dlv_sql = """
            INSERT INTO content_deliveries (webhook_id, generation_id, event, payload, status)
            VALUES ($1, $2, $3, $4, 'pending') RETURNING id;
        """
        dlv = await _db(dlv_sql, wh["id"], generation_id, event, json.dumps(payload))
        dlv_id = str(dlv[0]["id"])
        try:
            async with httpx.AsyncClient(timeout=30) as cl:
                r = await cl.post(
                    wh["url"],
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
            await _db(
                "UPDATE content_deliveries SET status = 'delivered', response_code = $1, delivered_at = now() WHERE id = $2;",
                r.status_code, dlv_id,
            )
            await _db(
                "UPDATE content_webhooks SET last_delivery_at = now(), failure_count = 0 WHERE id = $1;",
                wh["id"],
            )
        except Exception as e:
            await _db(
                "UPDATE content_deliveries SET status = 'failed', response_body = $1 WHERE id = $2;",
                str(e), dlv_id,
            )
            await _db(
                "UPDATE content_webhooks SET failure_count = failure_count + 1 WHERE id = $1;",
                wh["id"],
            )


app = mcp.sse_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8765, log_level="info")
