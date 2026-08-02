#!/usr/bin/env python3
"""Auto-Improve — Analiza métricas y sugiere/mejora el sistema automáticamente.

Se ejecuta vía cron diario:
1. Analiza conversations y leads de las últimas 24h
2. Identifica patrones de conversación que funcionan
3. Sugiere mejoras al prompt_builder o lead_classifier
4. Actualiza engram con lecciones aprendidas
5. Re-entrena el eval si hay suficientes datos nuevos
"""

import os
import json
import sqlite3
import asyncpg
import logging
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("auto-improve")

DB_URL = os.getenv("DATABASE_URL", "postgresql://sdc:${POSTGRES_PASSWORD:-}@localhost:5432/sdc")
ENGRAM_DB = Path(__file__).parent.parent.parent / "sonora-digital-corp" / "ops" / "state" / "engram_aztrotech.db"
REPORT_DIR = Path(__file__).parent.parent / "ops" / "state" / "reports"


async def analyze_conversations():
    """Analyze recent conversations for patterns."""
    try:
        pool = await asyncpg.create_pool(DB_URL, min_size=1, max_size=2)
        
        # Get conversations from last 24h
        rows = await pool.fetch("""
            SELECT c.id, c.lead_type, c.lead_confidence, c.language,
                   COUNT(m.id) as msg_count,
                   AVG(m.tokens_in + m.tokens_out) as avg_tokens
            FROM conversations c
            JOIN messages m ON m.conversation_id = c.id
            WHERE c.started_at > NOW() - INTERVAL '24 hours'
            GROUP BY c.id, c.lead_type, c.lead_confidence, c.language
        """)
        
        # Get lead conversion stats
        lead_stats = await pool.fetchrow("""
            SELECT 
                COUNT(*) as total_leads,
                COUNT(*) FILTER (WHERE lead_score >= 70) as hot_leads,
                COUNT(*) FILTER (WHERE lead_score >= 30 AND lead_score < 70) as warm_leads,
                COUNT(*) FILTER (WHERE lead_score < 30) as cold_leads,
                AVG(lead_score) as avg_score
            FROM leads WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        
        await pool.close()
        
        return {
            "conversations": len(rows),
            "lead_stats": dict(lead_stats) if lead_stats else {},
            "avg_tokens": float(rows[0]["avg_tokens"]) if rows else 0,
        }
    except Exception as e:
        logger.error(f"analyze_conversations error: {e}")
        return {}


async def check_lead_accuracy():
    """Run eval to check if lead accuracy is still good."""
    try:
        import subprocess
        result = subprocess.run(
            ["python3", str(Path(__file__).parent.parent / "scripts" / "evals" / "run_eval.py"),
             "--dataset", str(Path(__file__).parent.parent / "scripts" / "evals" / "dataset_v1.jsonl"),
             "--no-llm"],
            capture_output=True, text=True, timeout=60,
        )
        # Parse output
        for line in result.stdout.split("\n"):
            if "Lead accuracy" in line:
                pct = line.split(":")[1].strip().split("%")[0]
                return float(pct)
        return 0
    except Exception as e:
        logger.error(f"check_lead_accuracy error: {e}")
        return 0


def save_to_engram(key: str, value: str, layer: int = 3, importance: int = 3, tags: str = ""):
    """Save insight to engram."""
    try:
        import time
        now = time.time()
        conn = sqlite3.connect(str(ENGRAM_DB))
        conn.execute("""
            INSERT OR REPLACE INTO memories (key, value, layer, importance, tags, created_at, accessed_at, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, '')
        """, (key, value, layer, importance, tags, now, now))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"engram save error: {e}")


async def main():
    logger.info("🔄 Auto-improve: analyzing last 24h...")
    
    # 1. Analyze conversations
    conv_stats = await analyze_conversations()
    logger.info(f"Conversations: {conv_stats.get('conversations', 0)}")
    
    # 2. Check lead accuracy
    accuracy = await check_lead_accuracy()
    logger.info(f"Lead accuracy: {accuracy}%")
    
    # 3. Generate insights
    insights = []
    
    if conv_stats.get("lead_stats", {}).get("hot_leads", 0) > 0:
        hot = conv_stats["lead_stats"]["hot_leads"]
        insights.append(f"{hot} leads hot en 24h — pipeline funciona")
    
    if accuracy >= 85:
        insights.append(f"Lead accuracy {accuracy}% — por encima del objetivo 85%")
    else:
        insights.append(f"Lead accuracy {accuracy}% — BAJO objetivo, revisar classifier")
    
    if conv_stats.get("avg_tokens", 0) > 0:
        avg = conv_stats["avg_tokens"]
        cost = avg * 0.0000002  # deepseek-v4-flash cost
        insights.append(f"Avg tokens/mensaje: {avg:.0f} — costo ~${cost:.6f}")
    
    # 4. Save insights to engram
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M")
    save_to_engram(
        f"auto-improve:{timestamp}",
        "; ".join(insights),
        layer=3,
        importance=3,
        tags="auto-improve,metricas,insights",
    )
    
    # 5. Save report
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(),
        "conversations": conv_stats.get("conversations", 0),
        "lead_accuracy": accuracy,
        "lead_stats": conv_stats.get("lead_stats", {}),
        "insights": insights,
    }
    report_file = REPORT_DIR / f"auto-improve-{timestamp}.json"
    report_file.write_text(json.dumps(report, indent=2))
    logger.info(f"Report saved: {report_file}")
    
    return report


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())