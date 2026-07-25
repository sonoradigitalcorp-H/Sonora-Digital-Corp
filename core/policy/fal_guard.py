"""
FAL Guard — Cortafuegos de gastos para fal.ai

Cada llamada a fal.ai DEBE pasar por este guard antes de ejecutarse.
Protege contra:
  - Llamadas no autorizadas (API key leak)
  - Gastos que exceden límites diarios/por-llamada
  - Modelos no aprobados
  - Picos de gasto anómalos

Uso:
    from policy.fal_guard import FalGuard
    
    guard = FalGuard()
    
    # Verificar antes de llamar
    decision = guard.check("abe-music", "seedance-2.0", estimated_cost=4.25)
    if decision.allowed:
        result = fal_client.submit(endpoint, arguments)
        guard.record("abe-music", "seedance-2.0", actual_cost=4.25, request_id=result.request_id)
    else:
        print(f"⛔ {decision.reason}")
"""

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("policy.fal_guard")

# DB de gastos (comparte la misma DB que InferenceBudget)
DB_PATH = Path(__file__).resolve().parent.parent.parent / "state" / "budget.db"

# Límites por defecto (se sobreescriben con env vars)
DEFAULT_DAILY_LIMIT = float(os.getenv("FAL_DAILY_LIMIT", "10.0"))       # $10/día default
DEFAULT_MAX_PER_CALL = float(os.getenv("FAL_MAX_PER_CALL", "1.0"))      # $1/llamada default
DEFAULT_REQUIRE_APPROVAL_OVER = float(os.getenv("FAL_APPROVAL_OVER", "0.50"))  # pedir confirmación > $0.50
FAL_KEY = os.getenv("FAL_KEY", "")                                      # La key activa

# Costos estimados por modelo (actualizados 2026-07-24)
# Fuente: config/cost-rates.yaml + facturación real
MODEL_COST_CATALOG = {
    # Video - PREMIUM (caro)
    "bytedance/seedance-2.0/text-to-video":         {"type": "video", "estimated": 4.25, "tier": "premium"},
    "bytedance/seedance-2.0/image-to-video":         {"type": "video", "estimated": 4.25, "tier": "premium"},
    "fal-ai/veo3.1":                                  {"type": "video", "estimated": 0.40, "tier": "premium"},
    "fal-ai/veo3.1/image-to-video":                   {"type": "video", "estimated": 0.40, "tier": "premium"},
    "fal-ai/kling-video/v3/4k/text-to-video":         {"type": "video", "estimated": 0.35, "tier": "premium"},
    "fal-ai/kling-video/v2.5-turbo/pro/image-to-video": {"type": "video", "estimated": 0.20, "tier": "premium"},
    "alibaba/happy-horse/text-to-video":              {"type": "video", "estimated": 0.15, "tier": "premium"},
    
    # Video - ECONÓMICO
    "fal-ai/ltx-2.3-22b/text-to-video":              {"type": "video", "estimated": 0.05, "tier": "cheap"},
    "fal-ai/ltx-2.3-22b/image-to-video":              {"type": "video", "estimated": 0.05, "tier": "cheap"},
    "fal-ai/pixverse/v6/text-to-video":               {"type": "video", "estimated": 0.08, "tier": "cheap"},
    "fal-ai/pixverse/v6/image-to-video":               {"type": "video", "estimated": 0.08, "tier": "cheap"},
    "fal-ai/wan-25-preview/text-to-video":             {"type": "video", "estimated": 0.25, "tier": "medium"},
    "fal-ai/minimax/video-01-live":                    {"type": "video", "estimated": 0.10, "tier": "cheap"},
    "fal-ai/sync-lipsync/v3/image-to-video":           {"type": "video", "estimated": 0.08, "tier": "cheap"},
    "fal-ai/sadtalker":                                {"type": "video", "estimated": 0.01, "tier": "cheap"},
    
    # Image
    "fal-ai/flux-pro/v1.1-ultra":                      {"type": "image", "estimated": 0.04, "tier": "cheap"},
    "fal-ai/flux-pro/v1.1":                             {"type": "image", "estimated": 0.04, "tier": "cheap"},
    "fal-ai/flux/dev":                                  {"type": "image", "estimated": 0.03, "tier": "cheap"},
    "fal-ai/flux/schnell":                              {"type": "image", "estimated": 0.003, "tier": "free"},
    "fal-ai/flux-lora":                                 {"type": "image", "estimated": 0.01, "tier": "cheap"},
    "fal-ai/krea-2/turbo/lora":                         {"type": "image", "estimated": 0.01, "tier": "cheap"},
    "fal-ai/flux-pro/v1/fill":                          {"type": "image", "estimated": 0.04, "tier": "cheap"},
    "fal-ai/qwen-image":                                {"type": "image", "estimated": 0.02, "tier": "cheap"},
    
    # LoRA Training
    "fal-ai/flux-lora-fast-training":                   {"type": "train", "estimated": 4.00, "tier": "premium"},
    "fal-ai/krea-2-trainer":                            {"type": "train", "estimated": 3.00, "tier": "premium"},
    
    # Audio
    "fal-ai/playaudio/v2":                              {"type": "audio", "estimated": 0.01, "tier": "free"},
    "fal-ai/minimax-voice-clone":                       {"type": "audio", "estimated": 1.00, "tier": "medium"},
}


@dataclass
class GuardDecision:
    """Resultado de la verificación del guardia de gastos."""
    allowed: bool
    reason: str = ""
    estimated_cost: float = 0.0
    daily_used: float = 0.0
    daily_limit: float = 0.0
    requires_approval: bool = False
    alerts: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "estimated_cost": self.estimated_cost,
            "daily_used": self.daily_used,
            "daily_limit": self.daily_limit,
            "requires_approval": self.requires_approval,
            "alerts": self.alerts,
        }


class FalGuard:
    """
    Guardia de gastos para fal.ai.
    
    Pipeline:
        1. API Key check → 2. Modelo permitido → 3. Costo por llamada →
        4. Límite diario → 5. Umbral de aprobación → 6. Detección de anomalías
    
    Cada gate puede bloquear la ejecución.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DB_PATH
        self._ensure_db()
        self._daily_limit = DEFAULT_DAILY_LIMIT
        self._max_per_call = DEFAULT_MAX_PER_CALL
        self._approval_over = DEFAULT_REQUIRE_APPROVAL_OVER
        self._alerts: list = []
    
    def _ensure_db(self):
        """Asegura que la DB de gastos exista con la tabla fal_usage."""
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fal_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant TEXT NOT NULL,
                model TEXT NOT NULL,
                endpoint TEXT DEFAULT '',
                cost REAL NOT NULL,
                request_id TEXT DEFAULT '',
                source TEXT DEFAULT '',
                timestamp INTEGER NOT NULL,
                metadata TEXT DEFAULT '{}'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fal_limits (
                tenant TEXT PRIMARY KEY,
                daily_cap REAL DEFAULT 10.0,
                max_per_call REAL DEFAULT 1.0,
                approval_over REAL DEFAULT 0.50,
                blocked_models TEXT DEFAULT '[]',
                blocked_hours TEXT DEFAULT '[]'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fal_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant TEXT NOT NULL,
                severity TEXT DEFAULT 'warning',
                message TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                acknowledged INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        conn.close()
    
    # ─── Configuración de límites ──────────────────────────────────────
    
    def set_limits(self, tenant: str, daily_cap: float = 10.0, 
                   max_per_call: float = 1.0, approval_over: float = 0.50,
                   blocked_models: Optional[list] = None):
        """Configura límites para un tenant."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute(
            """INSERT OR REPLACE INTO fal_limits 
               (tenant, daily_cap, max_per_call, approval_over, blocked_models)
               VALUES (?, ?, ?, ?, ?)""",
            (tenant, daily_cap, max_per_call, approval_over,
             json.dumps(blocked_models or [])),
        )
        conn.commit()
        conn.close()
        logger.info(f"[{tenant}] Límites FAL: ${daily_cap}/día, ${max_per_call}/call, "
                    f"approval >${approval_over}")
    
    def get_limits(self, tenant: str) -> dict:
        """Obtiene límites de un tenant."""
        conn = sqlite3.connect(str(self._db_path))
        row = conn.execute(
            "SELECT daily_cap, max_per_call, approval_over, blocked_models FROM fal_limits WHERE tenant = ?",
            (tenant,),
        ).fetchone()
        conn.close()
        if row:
            return {
                "daily_cap": row[0],
                "max_per_call": row[1],
                "approval_over": row[2],
                "blocked_models": json.loads(row[3]) if row[3] else [],
            }
        return {
            "daily_cap": self._daily_limit,
            "max_per_call": self._max_per_call,
            "approval_over": self._approval_over,
            "blocked_models": [],
        }
    
    # ─── Consultas ─────────────────────────────────────────────────────
    
    def today_usage(self, tenant: str) -> float:
        """Gasto acumulado del tenant hoy en FAL."""
        today_start = int(time.time()) - (int(time.time()) % 86400)
        conn = sqlite3.connect(str(self._db_path))
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM fal_usage WHERE tenant = ? AND timestamp >= ?",
            (tenant, today_start),
        ).fetchone()
        conn.close()
        return row[0] if row else 0.0
    
    def last_calls(self, tenant: str, n: int = 20) -> list[dict]:
        """Últimas N llamadas a FAL."""
        conn = sqlite3.connect(str(self._db_path))
        rows = conn.execute(
            """SELECT model, endpoint, cost, request_id, source, timestamp 
               FROM fal_usage WHERE tenant = ? 
               ORDER BY id DESC LIMIT ?""",
            (tenant, n),
        ).fetchall()
        conn.close()
        return [
            {
                "model": r[0], "endpoint": r[1], "cost": r[2],
                "request_id": r[3], "source": r[4], "timestamp": r[5],
            }
            for r in rows
        ]
    
    def total_usage(self, tenant: str) -> float:
        """Gasto total histórico."""
        conn = sqlite3.connect(str(self._db_path))
        row = conn.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM fal_usage WHERE tenant = ?",
            (tenant,),
        ).fetchone()
        conn.close()
        return row[0] if row else 0.0
    
    # ─── Pipeline de verificación ──────────────────────────────────────
    
    def estimate_cost(self, model_or_endpoint: str) -> float:
        """Estima el costo de un modelo. Si no está catalogado, usa máximo por defecto."""
        if model_or_endpoint in MODEL_COST_CATALOG:
            return MODEL_COST_CATALOG[model_or_endpoint]["estimated"]
        # Si no conocemos el costo, asumimos premium para ser conservadores
        return self._max_per_call
    
    def check(self, tenant: str, model_or_endpoint: str, 
              estimated_cost: Optional[float] = None,
              source: str = "unknown",
              context: Optional[dict] = None) -> GuardDecision:
        """
        Pipeline completo de verificación.
        
        Args:
            tenant: Identificador del tenant (ej: "abe-music", "aztrotech")
            model_or_endpoint: Model ID o endpoint completo
            estimated_cost: Costo estimado (auto-calculado si no se provee)
            source: Origen de la llamada (ej: "hermes-video", "mcp-media")
            context: Contexto adicional (ej: {"user": "..."})
        
        Returns:
            GuardDecision con .allowed=True/False
        """
        if not FAL_KEY:
            return GuardDecision(
                allowed=False,
                reason="FAL_KEY no está configurada. No se pueden hacer llamadas a fal.ai.",
            )
        
        context = context or {}
        limits = self.get_limits(tenant)
        cost = estimated_cost if estimated_cost is not None else self.estimate_cost(model_or_endpoint)
        alerts = []
        
        # ── Gate 1: API Key presente ──
        # (ya validado arriba)
        
        # ── Gate 2: Modelo bloqueado ──
        blocked = limits.get("blocked_models", [])
        for b in blocked:
            if b in model_or_endpoint:
                return GuardDecision(
                    allowed=False,
                    reason=f"Modelo '{model_or_endpoint}' está BLOQUEADO para tenant '{tenant}'.",
                    estimated_cost=cost,
                    alerts=alerts,
                )
        
        # ── Gate 3: Límite por llamada ──
        if cost > limits["max_per_call"]:
            return GuardDecision(
                allowed=False,
                reason=(
                    f"⛔ Costo estimado ${cost:.2f} excede el máximo por llamada "
                    f"(${limits['max_per_call']:.2f}) para '{tenant}'. "
                    f"Modelo: {model_or_endpoint}"
                ),
                estimated_cost=cost,
                daily_limit=limits["daily_cap"],
                alerts=alerts,
            )
        
        # ── Gate 4: Límite diario ──
        used = self.today_usage(tenant)
        if used + cost > limits["daily_cap"]:
            remaining = max(0, limits["daily_cap"] - used)
            self._add_alert(tenant, "critical",
                f"❌ Límite diario de ${limits['daily_cap']:.2f} ALCANZADO para '{tenant}'. "
                f"Usado: ${used:.2f}, intento: ${cost:.2f}, modelo: {model_or_endpoint}")
            return GuardDecision(
                allowed=False,
                reason=(
                    f"⛔ Límite diario de ${limits['daily_cap']:.2f} alcanzado. "
                    f"Usado: ${used:.2f}, restante: ${remaining:.2f}. "
                    f"Intento: ${cost:.2f} para {model_or_endpoint}"
                ),
                estimated_cost=cost,
                daily_used=used,
                daily_limit=limits["daily_cap"],
                alerts=alerts,
            )
        
        # ── Gate 5: Costo requiere aprobación ──
        requires_approval = cost >= limits.get("approval_over", 0.50)
        if requires_approval:
            alerts.append(f"⚠️ Costo ${cost:.2f} requiere confirmación (umbral: ${limits['approval_over']:.2f})")
        
        # ── Gate 6: Detección de anomalías ──
        anomalies = self._detect_anomalies(tenant, cost, model_or_endpoint)
        alerts.extend(anomalies)
        
        # ── Gate 6b: Seedance sin aprobación explícita siempre bloquea ──
        # Seedance es el modelo más caro a $4.25/llamada
        if "seedance" in model_or_endpoint.lower() and not context.get("approved"):
            return GuardDecision(
                allowed=False,
                reason=(
                    f"⛔ Seedance ({model_or_endpoint}) requiere APROBACIÓN EXPLÍCITA. "
                    f"Cuesta ~${cost:.2f} por llamada. "
                    f"Usá context={{'approved': True}} solo con confirmación humana."
                ),
                estimated_cost=cost,
                daily_used=used,
                daily_limit=limits["daily_cap"],
                requires_approval=True,
                alerts=alerts + [f"🔴 Seedance requiere autorización manual - ${cost:.2f}/call"],
            )
        
        # ── Todo OK ──
        return GuardDecision(
            allowed=True,
            reason=f"✅ Permitido. ${cost:.2f} para {model_or_endpoint}",
            estimated_cost=cost,
            daily_used=used,
            daily_limit=limits["daily_cap"],
            requires_approval=requires_approval,
            alerts=alerts,
        )
    
    def _detect_anomalies(self, tenant: str, cost: float, model: str) -> list:
        """Detecta patrones anómalos de gasto."""
        alerts = []
        
        # 1. Múltiples llamadas caras en pocos minutos
        recent = self.last_calls(tenant, 5)
        recent_expensive = [c for c in recent if c["cost"] > 1.0]
        if len(recent_expensive) >= 3:
            total_recent = sum(c["cost"] for c in recent_expensive)
            alerts.append(
                f"🚨 {len(recent_expensive)} llamadas >$1 en las últimas 5 llamadas "
                f"(total: ${total_recent:.2f}). Posible fuga."
            )
        
        # 2. Seedance o modelos premium sin historial
        if "seedance" in model.lower() or cost > 2.0:
            total_hist = self.total_usage(tenant)
            if total_hist < 1.0:
                alerts.append(
                    f"⚠️ Primera vez que '{tenant}' usa {model} (${cost:.2f}). "
                    f"Sin historial previo de gasto."
                )
        
        return alerts
    
    # ─── Registro ──────────────────────────────────────────────────────
    
    def record(self, tenant: str, model: str, actual_cost: float,
               request_id: str = "", endpoint: str = "", source: str = "unknown",
               metadata: Optional[dict] = None):
        """Registra una llamada a FAL después de ejecutada."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute(
            """INSERT INTO fal_usage 
               (tenant, model, endpoint, cost, request_id, source, timestamp, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (tenant, model, endpoint, actual_cost, request_id, source,
             int(time.time()), json.dumps(metadata or {})),
        )
        conn.commit()
        conn.close()
        
        # Log
        logger.info(f"[FAL][{tenant}] ${actual_cost:.4f} — {model} ({source})")
        
        # Verificar si debemos alertar
        used = self.today_usage(tenant)
        limits = self.get_limits(tenant)
        if used > limits["daily_cap"] * 0.8:
            self._add_alert(tenant, "warning",
                f"⚠️ '{tenant}' ha usado ${used:.2f} de ${limits['daily_cap']:.2f} "
                f"({used/limits['daily_cap']*100:.0f}%) del límite diario.")
        
        # Seedance siempre genera alerta informativa
        if "seedance" in model.lower():
            self._add_alert(tenant, "info",
                f"ℹ️ Seedance usado por '{tenant}': ${actual_cost:.2f} — {model}")
    
    # ─── Alertas ───────────────────────────────────────────────────────
    
    def _add_alert(self, tenant: str, severity: str, message: str):
        """Registra una alerta en la DB."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute(
            "INSERT INTO fal_alerts (tenant, severity, message, timestamp) VALUES (?, ?, ?, ?)",
            (tenant, severity, message, int(time.time())),
        )
        conn.commit()
        conn.close()
        logger.warning(f"[FAL-ALERT][{tenant}] {severity.upper()}: {message}")
    
    def get_alerts(self, tenant: str, unacknowledged_only: bool = True, limit: int = 20) -> list[dict]:
        """Obtiene alertas de un tenant."""
        conn = sqlite3.connect(str(self._db_path))
        if unacknowledged_only:
            rows = conn.execute(
                """SELECT id, severity, message, timestamp 
                   FROM fal_alerts WHERE tenant = ? AND acknowledged = 0
                   ORDER BY id DESC LIMIT ?""",
                (tenant, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT id, severity, message, timestamp 
                   FROM fal_alerts WHERE tenant = ?
                   ORDER BY id DESC LIMIT ?""",
                (tenant, limit),
            ).fetchall()
        conn.close()
        return [
            {"id": r[0], "severity": r[1], "message": r[2], "timestamp": r[3]}
            for r in rows
        ]
    
    def acknowledge_alert(self, alert_id: int):
        """Marca una alerta como leída."""
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("UPDATE fal_alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
        conn.commit()
        conn.close()
    
    # ─── Dashboard / Reportes ──────────────────────────────────────────
    
    def report(self, tenant: str) -> dict:
        """Reporte completo de actividad FAL para un tenant."""
        used = self.today_usage(tenant)
        limits = self.get_limits(tenant)
        calls = self.last_calls(tenant, 10)
        alerts = self.get_alerts(tenant)
        total = self.total_usage(tenant)
        
        # Gasto por modelo
        conn = sqlite3.connect(str(self._db_path))
        rows = conn.execute(
            """SELECT model, COUNT(*), SUM(cost) 
               FROM fal_usage WHERE tenant = ? AND timestamp >= ?
               GROUP BY model ORDER BY SUM(cost) DESC""",
            (tenant, int(time.time()) - 86400 * 7),
        ).fetchall()
        conn.close()
        
        return {
            "tenant": tenant,
            "daily_used": round(used, 4),
            "daily_limit": limits["daily_cap"],
            "daily_remaining": round(max(0, limits["daily_cap"] - used), 4),
            "daily_pct": round(used / limits["daily_cap"] * 100, 1) if limits["daily_cap"] > 0 else 0,
            "total_historical": round(total, 4),
            "active_alerts": len(alerts),
            "alerts": alerts[:5],
            "recent_calls": calls[:5],
            "by_model": [
                {"model": r[0], "count": r[1], "total": round(r[2], 4)}
                for r in rows
            ],
            "max_per_call": limits["max_per_call"],
            "approval_over": limits["approval_over"],
        }


# ─── Atajo de línea de comandos ───────────────────────────────────────

def print_report(tenant: str = "default"):
    """Imprime reporte en consola."""
    guard = FalGuard()
    report = guard.report(tenant)
    print(f"\n{'='*60}")
    print(f"📊  REPORTE FAL GUARD — {tenant}")
    print(f"{'='*60}")
    print(f"  Gasto hoy:    ${report['daily_used']:.2f} / ${report['daily_limit']:.2f} "
          f"({report['daily_pct']}%)")
    print(f"  Restante:     ${report['daily_remaining']:.2f}")
    print(f"  Total hist:   ${report['total_historical']:.2f}")
    print(f"  Alertas act:  {report['active_alerts']}")
    print(f"  Máx/call:     ${report['max_per_call']:.2f}")
    print(f"  Aprueba >$:   ${report['approval_over']:.2f}")
    if report["by_model"]:
        print(f"\n  Gasto por modelo (7 días):")
        for m in report["by_model"]:
            print(f"    {m['model']:<50s} {m['count']:>3d}x  ${m['total']:>7.2f}")
    if report["alerts"]:
        print(f"\n  Alertas activas:")
        for a in report["alerts"]:
            sev = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(a["severity"], "•")
            print(f"    {sev} [{a['severity']}] {a['message'][:80]}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    tenant = sys.argv[1] if len(sys.argv) > 1 else "default"
    print_report(tenant)
