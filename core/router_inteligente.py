"""
Router Inteligente de Modelos — Local vs Cloud optimizado por costo.

Estrategia: 80% local, 20% cloud.
Solo gasta tokens cuando es necesario, no 24/7.

┌────────────────────────────────────────────────────────────┐
│ Actividad              │ Modelo           │ Costo por uso  │
├────────────────────────────────────────────────────────────┤
│ Wake word detection    │ openWakeWord     │ $0 (CPU local) │
│ VAD (voz activa)       │ Energy-VAD       │ $0 (CPU local) │
│ STT (transcripción)    │ Whisper base     │ $0 (CPU local) │
│ TTS (voz sintética)    │ Kokoro-82M       │ $0 (CPU local) │
│ Embeddings (RAG)       │ nomic-embed-text │ $0 (CPU local) │
│ Clasificar intención   │ tinyllama:1.1b   │ $0 (CPU local) │
│ Chat simple            │ llama3.2:3b      │ $0 (CPU local) │
│ Respuestas template    │ (sin LLM)        │ $0             │
│ ─────────────────────  │ ───────────────  │ ─────────────  │
│ Browser actions        │ deepseek-v4-flash│ $0.00026/uso   │
│ Razonamiento complejo  │ deepseek-v4-flash│ $0.00026/uso   │
│ Análisis de costos     │ deepseek-v4-flash│ $0.00052/uso   │
│ Generación contenido   │ deepseek-v4-flash│ $0.00039/uso   │
│ Búsqueda web           │ deepseek-v4-flash│ $0.00026/uso   │
└────────────────────────────────────────────────────────────┘

La IA generativa solo se llama cuando el usuario realmente interactúa.
El sistema 24/7 (wake word, monitoreo, loops) CORRE 100% LOCAL.
"""

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

log = logging.getLogger("router.inteligente")

REPO = Path(__file__).resolve().parent.parent
COST_DB = REPO / "data" / "cost_tracker.db"


@dataclass
class ModelRoute:
    activity: str
    provider: str  # "local" | "openrouter" | "freemodels"
    model: str
    cost_per_call: float  # USD
    quality: str  # "low" | "medium" | "high"
    fallback: str = ""


# ─── Routing Table ───
ROUTES = {
    # LOCAL (gratis, CPU)
    "wake_word": ModelRoute("wake_word", "local", "openWakeWord", 0.0, "high"),
    "vad": ModelRoute("vad", "local", "Energy-VAD", 0.0, "high"),
    "stt": ModelRoute("stt", "local", "whisper-base", 0.0, "high"),
    "tts": ModelRoute("tts", "local", "kokoro-82M", 0.0, "high"),
    "embeddings": ModelRoute("embeddings", "local", "nomic-embed-text", 0.0, "high"),
    "classify_intent": ModelRoute("classify_intent", "local", "tinyllama:1.1b", 0.0, "medium"),
    "simple_chat": ModelRoute("simple_chat", "local", "llama3.2:3b", 0.0, "medium"),
    "template": ModelRoute("template", "local", "none", 0.0, "high"),
    
    # CLOUD (bajo costo, solo cuando es necesario)
    "browser_action": ModelRoute("browser_action", "openrouter", "deepseek/deepseek-v4-flash", 0.00026, "high"),
    "complex_reasoning": ModelRoute("complex_reasoning", "openrouter", "deepseek/deepseek-v4-flash", 0.00026, "high"),
    "cost_analysis": ModelRoute("cost_analysis", "openrouter", "deepseek/deepseek-v4-flash", 0.00052, "high"),
    "content_gen": ModelRoute("content_gen", "openrouter", "deepseek/deepseek-v4-flash", 0.00039, "high"),
    "web_search": ModelRoute("web_search", "openrouter", "deepseek/deepseek-v4-flash", 0.00026, "high"),
    "memory_rag": ModelRoute("memory_rag", "openrouter", "deepseek/deepseek-v4-flash", 0.00026, "high"),
}

# Costo mensual estimado
MONTHLY_ESTIMATE = """
┌────────────────────────────────────────────────────────┐
│ COSTO MENSUAL ESTIMADO (10,000 interacciones/mes)      │
├────────────────────────────────────────────────────────┤
│                                                         │
│ 10,000 clasificaciones   → llama3.2:3b  → $0  (local)  │
│ 10,000 transcripciones   → Whisper      → $0  (local)   │
│ 10,000 síntesis de voz   → Kokoro       → $0  (local)   │
│                                                         │
│ 2,000 chats simples      → deepseek     → $0.52         │
│ 500 browser actions      → deepseek     → $0.13         │
│ 500 razonamientos        → deepseek     → $0.13         │
│ 200 análisis costos      → deepseek     → $0.10         │
│                                                         │
│ ─────────────────────────────────────────────────────── │
│ TOTAL OPENROUTER         →              → $0.88/mes     │
│ TOTAL INFRA FIJA         → VPS + dominio → $16.00/mes   │
│ TOTAL GENERAL            →              → $16.88/mes    │
│                                                         │
│ Por cliente (10)         →              → $1.69/cliente │
│ Margen (venta a $29/mes) →              → 94% margen    │
└────────────────────────────────────────────────────────┘
"""


class RouterInteligente:
    """Router que decide qué modelo usar para cada actividad."""

    def __init__(self):
        self._cost_db = COST_DB
        self._init_cost_db()
        self.stats = {"local_calls": 0, "cloud_calls": 0, "total_cost": 0.0}

    def _init_cost_db(self):
        os.makedirs(self._cost_db.parent, exist_ok=True)
        conn = sqlite3.connect(str(self._cost_db))
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS cost_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity TEXT,
                provider TEXT,
                model TEXT,
                tokens_input INTEGER DEFAULT 0,
                tokens_output INTEGER DEFAULT 0,
                cost REAL DEFAULT 0.0,
                tenant_id TEXT DEFAULT 'sonora-digital',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_cost_date ON cost_log(created_at);
            CREATE INDEX IF NOT EXISTS idx_cost_tenant ON cost_log(tenant_id);
        """)
        conn.commit()
        conn.close()

    def route(self, activity: str, tenant_id: str = "sonora-digital") -> ModelRoute:
        """Returns the best model route for an activity."""
        route = ROUTES.get(activity, ROUTES["simple_chat"])
        
        # Log for cost tracking
        self._log_call(activity, route, tenant_id)
        
        if route.provider == "local":
            self.stats["local_calls"] += 1
        else:
            self.stats["cloud_calls"] += 1
            self.stats["total_cost"] += route.cost_per_call
        
        return route

    def _log_call(self, activity: str, route: ModelRoute, tenant_id: str):
        """Register every LLM call for cost tracking."""
        try:
            conn = sqlite3.connect(str(self._cost_db))
            conn.execute(
                "INSERT INTO cost_log (activity, provider, model, cost, tenant_id) VALUES (?, ?, ?, ?, ?)",
                (activity, route.provider, route.model, route.cost_per_call if route.provider != "local" else 0.0, tenant_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            log.warning(f"Cost log failed: {e}")

    def get_cost_report(self, tenant_id: str = "") -> dict:
        """Generate cost report."""
        conn = sqlite3.connect(str(self._cost_db))
        conn.row_factory = sqlite3.Row
        
        query = """
            SELECT 
                activity,
                provider,
                COUNT(*) as calls,
                SUM(cost) as total_cost,
                SUM(tokens_input) as total_tokens_in,
                SUM(tokens_output) as total_tokens_out
            FROM cost_log
        """
        params = []
        if tenant_id:
            query += " WHERE tenant_id = ?"
            params.append(tenant_id)
        query += " GROUP BY activity, provider ORDER BY total_cost DESC"
        
        rows = conn.execute(query, params).fetchall()
        total = conn.execute(
            "SELECT SUM(cost) as t FROM cost_log" + (" WHERE tenant_id = ?" if tenant_id else ""),
            params or []
        ).fetchone()
        
        conn.close()
        
        return {
            "by_activity": [dict(r) for r in rows],
            "total": round(total["t"] or 0.0, 6) if total else 0.0,
            "period": "all_time",
            "tenant_id": tenant_id or "all",
        }

    def get_cost_summary(self) -> str:
        """Returns a human-readable cost summary."""
        report = self.get_cost_report()
        lines = ["📊 REPORTE DE COSTOS SDC", "═══════════════════════", ""]
        lines.append(f"💰 Total gastado: ${report['total']:.6f}")
        lines.append(f"☁️  Llamadas cloud: {self.stats['cloud_calls']}")
        lines.append(f"💻 Llamadas locales: {self.stats['local_calls']} (gratis)")
        lines.append("")
        lines.append("Por actividad:")
        for act in report["by_activity"]:
            lines.append(f"  · {act['activity']}: ${act['total_cost']:.6f} ({act['calls']} llamadas vía {act['provider']})")
        return "\n".join(lines)


# Singleton
_router = None

def get_router() -> RouterInteligente:
    global _router
    if _router is None:
        _router = RouterInteligente()
    return _router


if __name__ == "__main__":
    r = get_router()
    print(MONTHLY_ESTIMATE)
    print("=" * 55)
    
    # Simulate a day of activity
    activities = [
        "classify_intent", "simple_chat", "template", "wake_word",
        "browser_action", "complex_reasoning", "cost_analysis",
        "stt", "tts", "embeddings", "web_search",
    ]
    for act in activities:
        route = r.route(act, "sonora-digital")
        print(f"  {act:20s} → {route.provider:12s} {route.model:25s} ${route.cost_per_call:.6f}")
    
    print()
    print(r.get_cost_summary())
