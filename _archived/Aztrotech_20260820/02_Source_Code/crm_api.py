"""CRM API Router — endpoints para que César vea leads, conversaciones, métricas.

Mount on FastAPI:
    from server import app
    from crm_api import router as crm_router
    app.include_router(crm_router, prefix="/api/crm")

Endpoints:
    GET  /api/crm/leads          → lista leads con filters
    GET  /api/crm/lead/{id}      → conversación completa + métricas
    POST /api/crm/lead/{id}/cita → agendar cita
    POST /api/crm/lead/{id}/servicios → set servicios requeridos
    POST /api/crm/lead/{id}/obsidian  → crear nota en Obsidian
    POST /api/crm/survey         → recibir feedback post-conversación
    GET  /api/crm/metrics        → resumen ejecutivo
    GET  /api/crm/gamification   → puntos, badges, top referrers
"""
import json
import logging
import asyncio
import tempfile
import os
import subprocess
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from uuid import UUID

import asyncpg
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from fastapi.responses import FileResponse

from sdc_config import get_config

logger = logging.getLogger(__name__)
router = APIRouter()


async def _fetch(query: str, params: List[Any] = None, fetch_one: bool = False):
    """Connection-per-request helper (avoids asyncpg pool thread issues)."""
    cfg = get_config()
    conn = await asyncpg.connect(cfg.database_url)
    try:
        if fetch_one:
            return await conn.fetchrow(query, *(params or []))
        return await conn.fetch(query, *(params or []))
    finally:
        await conn.close()


async def _execute(query: str, params: List[Any] = None):
    cfg = get_config()
    conn = await asyncpg.connect(cfg.database_url)
    try:
        return await conn.execute(query, *(params or []))
    finally:
        await conn.close()


def _parse_jsonb(val, default):
    """Parse JSONB from asyncpg (may be str, dict/list, or None)."""
    if val is None:
        return default
    if isinstance(val, str):
        return json.loads(val) if val else default
    return val


class LeadType(str, Enum):
    cold = "cold"
    warm = "warm"
    hot = "hot"


class LeadResponse(BaseModel):
    id: UUID
    internal_user_id: UUID
    platform: str
    platform_id: str
    display_name: Optional[str]
    lead_type: Optional[str]
    lead_confidence: Optional[float]
    business_name: Optional[str]
    business_type: Optional[str]
    pain_points: List[str] = []
    budget_range: Optional[str]
    timeline: Optional[str]
    cita_agendada: Optional[datetime]
    servicios_requeridos: List[str] = []
    engagement_score: Optional[float]
    started_at: datetime
    updated_at: datetime
    message_count: int
    total_cost_usd: float
    survey_feedback: Optional[Dict[str, Any]]


@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(
    lead_type: Optional[LeadType] = Query(None),
    platform: Optional[str] = Query(None),
    has_cita: Optional[bool] = Query(None),
    min_engagement: Optional[float] = Query(None, ge=0, le=1),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    """Lista de leads con filtros — el corazón del CRM de César."""
    conditions = []
    params: List[Any] = []

    if lead_type:
        params.append(lead_type.value)
        conditions.append(f"c.lead_type = ${len(params)}")
    if platform:
        params.append(platform)
        conditions.append(f"c.platform = ${len(params)}")
    if has_cita is not None:
        if has_cita:
            conditions.append("c.cita_agendada IS NOT NULL")
        else:
            conditions.append("c.cita_agendada IS NULL")
    if min_engagement is not None:
        params.append(min_engagement)
        conditions.append(f"c.engagement_score >= ${len(params)}")
    if search:
        pat = f"%{search}%"
        conditions.append(f"(u.display_name ILIKE '{pat}' OR u.business_name ILIKE '{pat}' OR u.business_type ILIKE '{pat}')")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    params.extend([limit, offset])

    query = f"""
        SELECT c.id, c.internal_user_id, c.platform, c.platform_conversation_id,
               c.lead_type, c.lead_confidence, c.cita_agendada, c.servicios_requeridos,
               c.engagement_score, c.started_at, c.updated_at, c.survey_feedback,
               u.display_name, u.business_name, u.business_type, u.pain_points,
               u.budget_range, u.timeline,
               COUNT(m.id) as message_count,
               COALESCE(SUM(m.cost_usd), 0) as total_cost_usd
        FROM conversations c
        JOIN user_identities u ON u.internal_id = c.internal_user_id
        LEFT JOIN messages m ON m.conversation_id = c.id
        {where_clause}
        GROUP BY c.id, u.internal_id
        ORDER BY c.lead_confidence DESC NULLS LAST, c.updated_at DESC
        LIMIT ${len(params)-1} OFFSET ${len(params)}
    """

    rows = await _fetch(query, params)
    results = []
    for r in rows:
        results.append(LeadResponse(
            id=r["id"],
            internal_user_id=r["internal_user_id"],
            platform=r["platform"],
            platform_id=r["platform_conversation_id"],
            display_name=r["display_name"] or r["platform_conversation_id"],
            lead_type=r["lead_type"],
            lead_confidence=r["lead_confidence"],
            business_name=r["business_name"],
            business_type=r["business_type"],
            pain_points=_parse_jsonb(r["pain_points"], []),
            budget_range=r["budget_range"],
            timeline=r["timeline"],
            cita_agendada=r["cita_agendada"],
            servicios_requeridos=_parse_jsonb(r["servicios_requeridos"], []),
            engagement_score=r["engagement_score"],
            started_at=r["started_at"],
            updated_at=r["updated_at"],
            survey_feedback=_parse_jsonb(r["survey_feedback"], {}),
            message_count=r["message_count"] or 0,
            total_cost_usd=float(r["total_cost_usd"] or 0),
        ))
    return results


@router.get("/lead/{lead_id}", response_model=Dict[str, Any])
async def get_lead_detail(lead_id: UUID):
    """Detalle completo de conversación para César."""
    conv = await _fetch(
        """SELECT c.*, u.display_name, u.business_name, u.business_type, u.pain_points,
                  u.budget_range, u.timeline, u.preferred_contact, u.lead_type as uid_lead_type,
                  u.lead_confidence as uid_lead_confidence
           FROM conversations c
           JOIN user_identities u ON u.internal_id = c.internal_user_id
           WHERE c.id = $1""",
        [str(lead_id)], fetch_one=True,
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    msgs = await _fetch(
        """SELECT role, content, created_at, tokens_in, tokens_out, model, cost_usd, emotion_scores
           FROM messages WHERE conversation_id = $1 ORDER BY turn_number, created_at""",
        [lead_id],
    )

    return {
        "lead": {
            "id": str(conv["id"]),
            "name": conv["display_name"],
            "business_name": conv["business_name"],
            "business_type": conv["business_type"],
            "lead_type": conv["lead_type"],
            "lead_confidence": conv["lead_confidence"],
            "pain_points": _parse_jsonb(conv["pain_points"], []),
            "budget_range": conv["budget_range"],
            "timeline": conv["timeline"],
            "preferred_contact": conv["preferred_contact"],
            "platform": conv["platform"],
            "platform_id": conv["platform_conversation_id"],
            "cita_agendada": conv["cita_agendada"],
            "servicios_requeridos": _parse_jsonb(conv["servicios_requeridos"], []),
            "survey_feedback": _parse_jsonb(conv["survey_feedback"], {}),
            "engagement_score": conv["engagement_score"],
            "started_at": conv["started_at"],
        },
        "messages": [
            {
                "role": m["role"],
                "content": m["content"],
                "created_at": m["created_at"].isoformat() if m["created_at"] else None,
                "tokens_in": m["tokens_in"],
                "tokens_out": m["tokens_out"],
                "model": m["model"],
                "cost_usd": float(m["cost_usd"] or 0),
            }
            for m in msgs
        ],
    }


class CitaRequest(BaseModel):
    fecha: datetime
    tipo: str = Field("llamada", description="llamada, visita_oficina, visita_negocio")
    notas: Optional[str] = None


@router.post("/lead/{lead_id}/cita")
async def agendar_cita(lead_id: UUID, req: CitaRequest):
    """Agendar cita/reunión para un lead."""
    result = await _execute(
        "UPDATE conversations SET cita_agendada = $1, updated_at = NOW() WHERE id = $2",
        [req.fecha, str(lead_id)],
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return {"success": True, "lead_id": str(lead_id), "cita_agendada": req.fecha.isoformat()}


@router.post("/lead/{lead_id}/servicios")
async def set_servicios(lead_id: UUID, servicios: List[str]):
    """Set servicios requeridos para un lead."""
    result = await _execute(
        "UPDATE conversations SET servicios_requeridos = $1, updated_at = NOW() WHERE id = $2",
        [json.dumps(servicios), str(lead_id)],
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return {"success": True, "servicios": servicios}


class SurveyRequest(BaseModel):
    lead_id: UUID
    rating: int = Field(..., ge=1, le=5)
    recommended: bool
    servicio_interes: Optional[str] = None
    comentarios: Optional[str] = None


@router.post("/survey")
async def submit_survey(req: SurveyRequest):
    """Recibir feedback post-conversación del lead."""
    feedback = {
        "rating": req.rating,
        "recommended": req.recommended,
        "servicio_interes": req.servicio_interes,
        "comentarios": req.comentarios,
        "submitted_at": datetime.utcnow().isoformat(),
    }
    result = await _execute(
        "UPDATE conversations SET survey_feedback = $1, updated_at = NOW() WHERE id = $2",
        [json.dumps(feedback), str(req.lead_id)],
    )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Lead no encontrado")
    return {"success": True, "feedback": feedback}


@router.get("/metrics")
async def get_metrics(
    date_from: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    date_to: Optional[str] = Query(None),
):
    """Métricas ejecutivas para César — resumen rápido."""
    conditions = []
    if date_from:
        conditions.append(f"started_at >= '{date_from}'")
    if date_to:
        conditions.append(f"started_at <= '{date_to}'")
    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    stats = await _fetch(f"""
        SELECT
            COUNT(*) as total_conversations,
            COUNT(CASE WHEN lead_type = 'hot' THEN 1 END) as leads_hot,
            COUNT(CASE WHEN lead_type = 'warm' THEN 1 END) as leads_warm,
            COUNT(CASE WHEN lead_type = 'cold' THEN 1 END) as leads_cold,
            COUNT(CASE WHEN cita_agendada IS NOT NULL THEN 1 END) as citas_agendadas,
            COUNT(CASE WHEN survey_feedback != '{{}}'::jsonb THEN 1 END) as surveys_respondidos,
            AVG(lead_confidence) as avg_confidence,
            AVG(engagement_score) as avg_engagement,
            SUM(m.cost_usd) as total_cost_usd,
            COUNT(DISTINCT c.internal_user_id) as unique_users
        FROM conversations c
        LEFT JOIN messages m ON m.conversation_id = c.id
        {where}
    """, fetch_one=True)

    return {
        "total_conversations": stats["total_conversations"] or 0,
        "leads_hot": stats["leads_hot"] or 0,
        "leads_warm": stats["leads_warm"] or 0,
        "leads_cold": stats["leads_cold"] or 0,
        "citas_agendadas": stats["citas_agendadas"] or 0,
        "surveys_respondidos": stats["surveys_respondidos"] or 0,
        "avg_confidence": float(round(stats["avg_confidence"] or 0, 3)),
        "avg_engagement": float(round(stats["avg_engagement"] or 0, 3)),
        "total_cost_usd": float(stats["total_cost_usd"] or 0),
        "unique_users": stats["unique_users"] or 0,
    }


async def _find_or_create_identity(user_identifier: str, platform: str) -> str:
    """Busca o crea una identidad por platform_id, devuelve internal_user_id."""
    row = await _fetch(
        "SELECT internal_id FROM user_identities WHERE platform_id = $1",
        [user_identifier], fetch_one=True,
    )
    if row:
        return str(row["internal_id"])
    result = await _execute(
        "INSERT INTO user_identities (platform_id, platform, display_name) VALUES ($1, $2, $3) RETURNING internal_id",
        [user_identifier, platform, user_identifier],
    )
    # _execute with RETURNING doesn't work directly — do a fetch
    row = await _fetch(
        "SELECT internal_id FROM user_identities WHERE platform_id = $1",
        [user_identifier], fetch_one=True,
    )
    return str(row["internal_id"])


class ObsidianNoteRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: List[str] = []


@router.post("/lead/{lead_id}/obsidian", include_in_schema=False)
async def create_obsidian_note(
    lead_id: UUID, payload: ObsidianNoteRequest = None,
):
    """Crea una nota en Obsidian para este lead (vault path configurable via OBSIDIAN_VAULT_PATH)."""
    vault_path = get_config().obsidian_vault_path
    if not vault_path:
        raise HTTPException(
            status_code=501,
            detail="Obsidian vault no configurado. Set OBSIDIAN_VAULT_PATH in ~/.hermes/.env",
        )
    conv = await _fetch(
        """SELECT c.*, u.display_name, u.business_name, u.business_type, u.pain_points,
                   u.budget_range, u.timeline, u.phone_e164, u.platform
            FROM conversations c
            JOIN user_identities u ON u.internal_id = c.internal_user_id
            WHERE c.id = $1""",
        [str(lead_id)], fetch_one=True,
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    msgs = await _fetch(
        "SELECT role, content FROM messages WHERE conversation_id = $1 ORDER BY turn_number",
        [lead_id],
    )

    title = payload.title or f"Lead-{conv['display_name'] or conv['platform']}-{lead_id}"
    note_path = os.path.join(vault_path, f"{title}.md")

    if not os.path.exists(vault_path):
        raise HTTPException(status_code=500, detail=f"Vault no existe: {vault_path}")

    # Build note content
    if payload and payload.content:
        content = payload.content
    else:
        pain = _parse_jsonb(conv.get("pain_points"), [])
        user_msgs = "\n".join(
            f"- {m['content'][:200]}" for m in msgs if m["role"] == "user"
        )
        bot_msgs = "\n".join(
            f"- {m['content'][:200]}" for m in msgs if m["role"] == "assistant"
        )
        content = (
            f"# {title}\n\n"
            f"**Cliente**: {conv['display_name'] or conv['platform']}\n"
            f"**Plataforma**: {conv['platform']}\n"
            f"**Tipo de lead**: {conv['lead_type'] or 'desconocido'}\n"
            f"**Negocio**: {conv['business_name'] or 'N/A'}\n"
            f"**Sector**: {conv['business_type'] or 'N/A'}\n"
            f"**Pain points**: {', '.join(pain) if pain else 'No identificados'}\n"
            f"**Presupuesto**: {conv['budget_range'] or 'No especificado'}\n"
            f"**Timeline**: {conv['timeline'] or 'No especificado'}\n"
            f"**Teléfono**: {conv['phone_e164'] or 'N/A'}\n"
            f"**Total mensajes**: {len(msgs)}\n\n"
            f"## Diálogo del cliente\n{user_msgs}\n\n"
            f"## Respuestas del bot\n{bot_msgs}\n\n"
            f"## Follow-up\n- [ ] Agendar llamada\n"
            f"- [ ] Enviar propuesta\n"
            f"- [ ] Cerrar venta\n"
        )

    with open(note_path, "w") as f:
        f.write(content)

    return {
        "success": True,
        "note_path": note_path,
        "title": title,
    }


@router.get("/gamification", response_model=None)
async def gamification_dashboard():
    """Datos de gamificación para el dashboard de César."""
    rows = await _fetch(
        """SELECT u.internal_id, u.display_name, u.puntos, u.created_at,
                  EXISTS(SELECT 1 FROM points_log pl WHERE pl.internal_user_id = u.internal_id::text) as has_log
           FROM user_identities u
           ORDER BY u.puntos DESC NULLS LAST LIMIT 20""",
    )
    user_data = []
    for r in rows:
        uid = str(r["internal_id"])
        badges = []
        try:
            from gamification import create_gamification_engine
            gam = create_gamification_engine()
            status = await gam.get_user_status(uid)
            badges = status.get("badges", [])
            if gam._pool:
                await gam._pool.close()
        except Exception:
            pass
        user_data.append({
            "internal_user_id": uid,
            "display_name": r["display_name"] or r["platform_id"],
            "puntos": r["puntos"] or 0,
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "badges": [b["name"] for b in badges],
            "referral_link": None,
        })

    stats = await _fetch(
        """SELECT
              count(DISTINCT u.internal_id) as total_users,
              sum(u.puntos) as total_puntos,
              count(pl.id) as total_log_entries,
              avg(u.puntos) as avg_puntos
           FROM user_identities u
           LEFT JOIN points_log pl ON pl.internal_user_id = u.internal_id""",
        fetch_one=True,
    )

    return {
        "leaderboard": user_data,
        "stats": {
            "total_users": stats["total_users"] or 0,
            "total_puntos": stats["total_puntos"] or 0,
            "avg_puntos": float(round(stats["avg_puntos"] or 0, 1)),
        },
    }


@router.post("/lead/{lead_id}/report")
async def generate_audio_report(lead_id: UUID, background_tasks: BackgroundTasks):
    """Genera reporte de voz resumiendo la conversación y lo envía por WhatsApp a César."""
    # Fetch conversation + messages
    conv = await _fetch(
        """SELECT c.*, u.display_name, u.business_name, u.business_type, u.pain_points,
                  u.budget_range, u.timeline, u.phone_e164
           FROM conversations c
           JOIN user_identities u ON u.internal_id = c.internal_user_id
           WHERE c.id = $1""",
        [str(lead_id)], fetch_one=True,
    )
    if not conv:
        raise HTTPException(status_code=404, detail="Lead no encontrado")

    msgs = await _fetch(
        """SELECT role, content, tokens_in, tokens_out, cost_usd
           FROM messages WHERE conversation_id = $1 ORDER BY turn_number""",
        [lead_id],
    )

    # Generate summary text via LLM or heuristic
    summary_text = await _generate_summary(conv, msgs)

    # Generate audio via edge-tts
    audio_path = await _text_to_speech(summary_text, voice="es-MX-JorgeNeural")

    # Send via wacli to César's WhatsApp
    cesar_phone = os.getenv("WHATSAPP_CESAR_PHONE", "5216623538272")
    success = _send_whatsapp_voice(audio_path, cesar_phone)

    if success:
        return {
            "success": True,
            "lead_id": str(lead_id),
            "lead_name": conv["display_name"],
            "audio_path": audio_path,
            "whatsapp_sent": True,
            "to": cesar_phone,
            "summary_preview": summary_text[:200] + "..." if len(summary_text) > 200 else summary_text,
        }
    return {
        "success": False,
        "lead_id": str(lead_id),
        "audio_path": audio_path,
        "whatsapp_error": "wacli no disponible o falló envío",
        "to": cesar_phone,
        "summary": summary_text,
    }


async def _generate_summary(conv, msgs) -> str:
    """Genera resumen narrativo para reporte de audio."""
    lead_name = conv["display_name"] or conv["platform_conversation_id"]
    business = conv["business_name"] or "no especificado"
    lead_type = conv["lead_type"] or "desconocido"
    confidence = round((conv["lead_confidence"] or 0) * 100)
    pain = json.loads(conv["pain_points"] or "[]") if isinstance(conv.get("pain_points"), str) else (conv.get("pain_points") or [])

    user_msgs = [m["content"] for m in msgs if m["role"] == "user"]
    bot_msgs = [m["content"] for m in msgs if m["role"] == "assistant"]

    # Intentar LLM summary — OpenRouter primero, luego Ollama local, luego heurístico
    api_key = get_config().openrouter_api_key
    ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")

    if len(user_msgs) > 1:
        full_text = "\n".join(f"[{'Usuario' if m['role']=='user' else 'Bot'}] {m['content']}" for m in msgs)
        system_msg = (
            "Eres un analista de CRM para CEO César. Resume esta conversación WhatsApp/telegram en 7-10 líneas. "
            "Incluye: nombre cliente, servicio de interés, pain points, lead type (cold/warm/hot), "
            "intención del cliente, próximos pasos recomendados. "
            "Lenguaje español natural, tono ejecutivo directo. NO menciones IA ni tecnología. "
            "Formato: texto narrativo, no bullets."
        )
        # Try local Ollama first (zero cost, fast)
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(f"{ollama_endpoint}/api/generate", json={
                    "model": "qwen2.5:3b",
                    "prompt": full_text[:4000],
                    "system": system_msg,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_ctx": 4096},
                })
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("response", "").strip():
                        return data["response"].strip()
        except Exception as e:
            logger.debug(f"Ollama summary falló: {e}")

        # Fallback a OpenRouter solo si key disponible
        if api_key:
            try:
                prompt = [{"role": "system", "content": system_msg}, {"role": "user", "content": full_text[:4000]}]
                async with httpx.AsyncClient(timeout=30) as client:
                    resp = await client.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        json={"model": "deepseek/deepseek-v4-flash-0731", "messages": prompt, "max_tokens": 500},
                        headers={"Authorization": f"Bearer {api_key}", "HTTP-Referer": "https://aztrotech.mx"},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        if content:
                            return content
            except Exception as e:
                logger.warning(f"OpenRouter summary falló: {e}")

    # Fallback heurístico
    return (
        f"Reporte para César. Lead: {lead_name}. Tipo: {lead_type} con {confidence}% de confianza. "
        f"Negocio: {business}. Pain points: {', '.join(pain[:2]) if pain else 'No identificados'}. "
        f"Total mensajes: {len(msgs)}. Diálogo clave: "
        + "; ".join(m[:100] for m in user_msgs[:3])
        + ". Próximo paso: agendar llamada con César para cerrar venta."
    )


async def _text_to_speech(text: str, voice: str = "es-MX-JorgeNeural") -> str:
    """Convierte texto a voz con edge-tts, devuelve path del archivo MP3."""
    import edge_tts
    mp3_path = tempfile.mktemp(suffix=".mp3")
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(mp3_path)
    return mp3_path


def _send_whatsapp_voice(audio_path: str, phone: str) -> bool:
    """Envia nota de voz a WhatsApp via wacli."""
    wacli = os.path.expanduser("~/.local/bin/wacli")
    store = os.getenv("WACLI_STORE_DIR", os.path.expanduser("~/.wacli"))
    if not os.path.exists(wacli):
        logger.warning("wacli not found, no envía WhatsApp")
        return False
    try:
        ogg_path = audio_path.replace(".mp3", ".ogg")
        subprocess.run([
            "ffmpeg", "-i", audio_path, "-c:a", "libopus", "-b:a", "24k", ogg_path, "-y"
        ], capture_output=True, timeout=15)
        result = subprocess.run([
            wacli, "send", "voice", "--to", phone, "--file", ogg_path,
            "--store", store, "--json"
        ], capture_output=True, text=True, timeout=60)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"wacli send falló: {e}")
        return False
