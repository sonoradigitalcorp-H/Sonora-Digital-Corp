"""Aztrotech Dashboard — Monitoreo de tokens, leads, modelos y memoria."""
import os
import json
import logging
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard")

app = FastAPI(title="Aztrotech Dashboard")

DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:sdc_local_dev@localhost:5432/sdc")


async def get_db():
    return await asyncpg.create_pool(DB_URL, min_size=2, max_size=5)


@app.get("/api/stats")
async def get_stats():
    pool = await get_db()
    try:
        # Model usage
        models = await pool.fetch("""
            SELECT model, COUNT(*) as count, 
                   COALESCE(SUM(tokens_in),0) as total_in, 
                   COALESCE(SUM(tokens_out),0) as total_out, 
                   COALESCE(SUM(cost_usd),0) as total_cost
            FROM messages WHERE model IS NOT NULL AND model != ''
            GROUP BY model ORDER BY total_cost DESC
        """)
        
        # Total tokens today
        today = await pool.fetchrow("""
            SELECT COALESCE(SUM(tokens_in),0) as tin, COALESCE(SUM(tokens_out),0) as tout,
                   COALESCE(SUM(cost_usd),0) as cost, COUNT(*) as msgs
            FROM messages WHERE created_at > CURRENT_DATE
        """)
        
        # Total this month
        month = await pool.fetchrow("""
            SELECT COALESCE(SUM(tokens_in),0) as tin, COALESCE(SUM(tokens_out),0) as tout,
                   COALESCE(SUM(cost_usd),0) as cost, COUNT(*) as msgs
            FROM messages WHERE created_at > date_trunc('month', NOW())
        """)
        
        # Leads
        leads_total = await pool.fetchval("SELECT COUNT(*) FROM leads")
        leads_hot = await pool.fetchval("SELECT COUNT(*) FROM leads WHERE lead_type = 'hot'")
        leads_warm = await pool.fetchval("SELECT COUNT(*) FROM leads WHERE lead_type = 'warm'")
        leads_cold = await pool.fetchval("SELECT COUNT(*) FROM leads WHERE lead_type = 'cold'")
        leads_today = await pool.fetchval("SELECT COUNT(*) FROM leads WHERE created_at > CURRENT_DATE")
        
        # Recent leads
        recent_leads = await pool.fetch("""
            SELECT name, phone, source, lead_score, lead_type, created_at 
            FROM leads ORDER BY created_at DESC LIMIT 10
        """)
        
        # Conversations
        convos_total = await pool.fetchval("SELECT COUNT(*) FROM conversations")
        convos_today = await pool.fetchval("SELECT COUNT(*) FROM conversations WHERE started_at > CURRENT_DATE")
        
        # User identities (memory)
        users_total = await pool.fetchval("SELECT COUNT(*) FROM user_identities")
        
        # Embedding check (Qdrant)
        import httpx
        qdrant_ok = False
        embed_model = "unknown"
        points = 0
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                r = await client.get("http://localhost:6333/collections/sdc_knowledge")
                if r.status_code == 200:
                    qdrant_ok = True
                    data = r.json().get("result", {})
                    points = data.get("points_count", 0)
                    embed_model = "paraphrase-multilingual-MiniLM-L12-v2"
        except:
            pass
        
        # Daily metrics
        daily = await pool.fetch("""
            SELECT day, total_conversations, total_messages, leads_cold, leads_warm, leads_hot,
                   tokens_in, tokens_out, cost_usd
            FROM daily_metrics ORDER BY day DESC LIMIT 7
        """)
        
        return {
            "models": [dict(m) for m in models],
            "today": dict(today) if today else {},
            "month": dict(month) if month else {},
            "leads": {
                "total": leads_total or 0,
                "hot": leads_hot or 0,
                "warm": leads_warm or 0,
                "cold": leads_cold or 0,
                "today": leads_today or 0
            },
            "recent_leads": [dict(l) for l in recent_leads],
            "conversations": {"total": convos_total or 0, "today": convos_today or 0},
            "users_total": users_total or 0,
            "embeddings": {"ok": qdrant_ok, "model": embed_model, "points": points},
            "daily": [dict(d) for d in daily],
            "openrouter_usage": any("openrouter" in (m.get("model") or "").lower() for m in models),
            "llm_active": len(models) > 0,
            "timestamp": datetime.now().isoformat()
        }
    finally:
        await pool.close()


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "dashboard"}


# Serve dashboard HTML
@app.get("/{path:path}")
async def serve(path: str):
    if path.startswith("api/"):
        return {"error": "not found"}
    return FileResponse(os.path.join(os.path.dirname(__file__), "index.html"))
