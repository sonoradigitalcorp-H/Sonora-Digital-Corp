#!/usr/bin/env python3
"""feedback_loop.py — Auto-mejora por reacciones de leads.

Determinista: reglas de feedback → actualiza score + propone mejora prompts.
LLM solo para síntesis de patrones semanales.
"""

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import pytz

HERMOSILLO_TZ = pytz.timezone("America/Hermosillo")


@dataclass
class FeedbackEvent:
    lead_id: str
    tenant: str
    tipo: str  # click, respuesta, tiempo_respuesta, conversion, rechazo, asset_view
    valor: Any  # boolean, int (segundos), float (score)
    metadata: dict = field(default_factory=dict)
    timestamp: str = ""


# Reglas de feedback (deterministas)
FEEDBACK_RULES = {
    # Lead responde rápido (< 60s) → boost score
    "respuesta_rapida": {
        "condition": lambda e: e.tipo == "respuesta" and isinstance(e.valor, (int, float)) and e.valor < 60,
        "score_delta": +5,
        "action": "refuerzo_rapido",
        "description": "Lead respondió rápido (<60s)"
    },
    # Lead responde lento (> 3600s) → penaliza leve
    "respuesta_lenta": {
        "condition": lambda e: e.tipo == "respuesta" and isinstance(e.valor, (int, float)) and e.valor > 3600,
        "score_delta": -3,
        "action": "reengagement",
        "description": "Lead respondió lento (>1h)"
    },
    # Lead hace click en diagnóstico → boost fuerte
    "click_diagnostico": {
        "condition": lambda e: e.tipo == "click" and e.metadata.get("elemento") == "diagnostico",
        "score_delta": +15,
        "action": "priorizar_cita",
        "description": "Lead hizo click en diagnóstico"
    },
    # Lead pide asset → engagement positivo
    "pidio_asset": {
        "condition": lambda e: e.tipo == "asset_view",
        "score_delta": +5,
        "action": "refuerzo_contenido",
        "description": "Lead pidió/generó asset"
    },
    # Lead responde negativamente → bajada
    "respuesta_negativa": {
        "condition": lambda e: e.tipo == "respuesta" and isinstance(e.valor, str) and any(
            kw in e.valor.lower() for kw in ["no", "gracias", "no me interesa", "ya no", "adiós"]
        ),
        "score_delta": -10,
        "action": "nurturing",
        "description": "Lead respondió negativamente"
    },
    # Lead convierte (agendó cita) → boost máximo
    "conversion_cita": {
        "condition": lambda e: e.tipo == "conversion" and e.metadata.get("tipo") == "cita",
        "score_delta": +20,
        "action": "hot_callback",
        "description": "Lead agendó cita (conversión)"
    },
    # Lead rechaza después de ser WARM/HOT → investigar
    "rechazo_caliente": {
        "condition": lambda e: e.tipo == "rechazo",
        "score_delta": -15,
        "action": "analizar_objecion",
        "description": "Lead rechazó después de interés previo"
    },
    # Lead usa voz → engagement alto
    "uso_voz": {
        "condition": lambda e: e.tipo == "respuesta" and e.metadata.get("canal") == "voz",
        "score_delta": +3,
        "action": "priorizar_voz",
        "description": "Lead respondió por voz (engagement alto)"
    },
}


class FeedbackLoop:
    """Motor de feedback loop para auto-mejora."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    tenant TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    valor TEXT,
                    metadata TEXT DEFAULT '{}',
                    timestamp TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    tenant TEXT NOT NULL,
                    rule_applied TEXT NOT NULL,
                    score_delta INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    description TEXT,
                    applied_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS prompt_improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant TEXT NOT NULL,
                    prompt_id TEXT,
                    old_score REAL,
                    new_score REAL,
                    reason TEXT,
                    status TEXT DEFAULT 'proposed',
                    created_at TEXT DEFAULT (datetime('now')),
                    approved_at TEXT
                )
            """)

    def process_event(self, event: FeedbackEvent) -> dict[str, Any]:
        """
        Procesa un evento de feedback. Aplica reglas deterministas.
        Retorna: {applied_rules: [...], score_delta_total, actions: [...]}
        """
        results = {
            "lead_id": event.lead_id,
            "applied_rules": [],
            "score_delta_total": 0,
            "actions": []
        }

        for rule_name, rule in FEEDBACK_RULES.items():
            try:
                if rule["condition"](event):
                    results["applied_rules"].append(rule_name)
                    results["score_delta_total"] += rule["score_delta"]
                    results["actions"].append({
                        "rule": rule_name,
                        "delta": rule["score_delta"],
                        "action": rule["action"],
                        "description": rule["description"]
                    })
            except Exception as e:
                print(f"[WARN] Error en regla {rule_name}: {e}")

        # Persistir evento
        self._save_event(event)

        # Persistir acciones aplicadas
        if results["applied_rules"]:
            self._save_actions(event.lead_id, event.tenant, results["actions"])

        return results

    def _save_event(self, event: FeedbackEvent):
        """Persiste evento de feedback."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO feedback_events (lead_id, tenant, tipo, valor, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                event.lead_id,
                event.tenant,
                event.tipo,
                str(event.valor),
                json.dumps(event.metadata, ensure_ascii=False),
                event.timestamp or datetime.utcnow().isoformat()
            ))

    def _save_actions(self, lead_id: str, tenant: str, actions: list[dict]):
        """Persiste acciones aplicadas."""
        with sqlite3.connect(self.db_path) as conn:
            for a in actions:
                conn.execute("""
                    INSERT INTO feedback_actions (lead_id, tenant, rule_applied, score_delta, action, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (lead_id, tenant, a["rule"], a["delta"], a["action"], a["description"]))

    def get_lead_feedback(self, lead_id: str) -> list[dict]:
        """Obtiene historial de feedback de un lead."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM feedback_events
                WHERE lead_id = ?
                ORDER BY timestamp ASC
            """, (lead_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_lead_actions(self, lead_id: str) -> list[dict]:
        """Obtiene acciones aplicadas a un lead."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM feedback_actions
                WHERE lead_id = ?
                ORDER BY applied_at ASC
            """, (lead_id,)).fetchall()
            return [dict(r) for r in rows]

    def get_tenant_metrics(self, tenant: str) -> dict:
        """Métricas de feedback para un tenant."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Total eventos
            total = conn.execute(
                "SELECT COUNT(*) as c FROM feedback_events WHERE tenant = ?", (tenant,)
            ).fetchone()["c"]

            # Por tipo
            by_tipo = conn.execute("""
                SELECT tipo, COUNT(*) as c FROM feedback_events
                WHERE tenant = ? GROUP BY tipo
            """, (tenant,)).fetchall()

            # Score delta promedio
            avg_delta = conn.execute("""
                SELECT AVG(score_delta) as avg_delta FROM feedback_actions
                WHERE tenant = ?
            """, (tenant,)).fetchone()["avg_delta"]

            # Acciones más frecuentes
            top_actions = conn.execute("""
                SELECT action, COUNT(*) as c, AVG(score_delta) as avg_delta
                FROM feedback_actions
                WHERE tenant = ?
                GROUP BY action ORDER BY c DESC LIMIT 5
            """, (tenant,)).fetchall()

            return {
                "tenant": tenant,
                "total_eventos": total,
                "por_tipo": {r["tipo"]: r["c"] for r in by_tipo},
                "score_delta_promedio": avg_delta or 0,
                "acciones_top": [{"action": r["action"], "count": r["c"], "avg_delta": r["avg_delta"]} for r in top_actions]
            }

    def propose_prompt_improvement(self, tenant: str, prompt_id: str, reason: str, old_score: float, new_score: float):
        """Propone mejora a un prompt (para aprobación humana)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO prompt_improvements (tenant, prompt_id, old_score, new_score, reason, status)
                VALUES (?, ?, ?, ?, ?, 'proposed')
            """, (tenant, prompt_id, old_score, new_score, reason))

    def get_pending_improvements(self, tenant: str = None) -> list[dict]:
        """Obtiene mejoras pendientes de aprobación."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM prompt_improvements WHERE status = 'proposed'"
            params = []
            if tenant:
                query += " AND tenant = ?"
                params.append(tenant)
            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]


def get_suggested_prompts(tenant: str, feedback_events: list[dict]) -> list[str]:
    """
    Analiza patrones de feedback y sugiere prompts a mejorar.
    Determinista: solo reglas, cero LLM.
    """
    suggestions = []

    # Patrón: leads no responden → prompt de bienvenida podría mejorar
    no_response_count = sum(1 for e in feedback_events if e.get("tipo") == "sin_respuesta")
    if no_response_count > 5:
        suggestions.append(
            "Alta tasa de sin respuesta. Considerar mejorar prompt de bienvenida: "
            "más personalizado, pregunta abierta, urgencia sutil."
        )

    # Patrón: leads rechazan después de WARM → objeciones no están siendo manejadas
    rechazo_count = sum(1 for e in feedback_events if e.get("tipo") == "rechazo")
    if rechazo_count > 3:
        suggestions.append(
            "Alta tasa de rechazo después de interés. Revisar objeciones y contraargumentos: "
            "agregar prueba social más fuerte, ofrecer diagnóstico antes de pitch."
        )

    # Patrón: leads responden rápido pero no convierten → CTA débil
    fast_no_convert = sum(1 for e in feedback_events
                          if e.get("tipo") == "respuesta" and e.get("metadata", {}).get("rapida")
                          and not e.get("metadata", {}).get("convirtio"))
    if fast_no_convert > 3:
        suggestions.append(
            "Leads responden rápido pero no convierten. CTA podría ser más directo: "
            "en vez de '¿te parece?', usar '¿mañana a las 10 o el jueves a las 3?'."
        )

    # Patrón: uso de voz → buen indicador de engagement
    voice_count = sum(1 for e in feedback_events if e.get("tipo") == "respuesta" and e.get("metadata", {}).get("canal") == "voz")
    if voice_count > 2:
        suggestions.append(
            f"{voice_count} leads usaron voz. Considerar priorizar canal de voz "
            "y mejorar prompts de audio (más cercanos, personales)."
        )

    return suggestions


def main():
    """CLI para testing."""
    import argparse
    ap = argparse.ArgumentParser(description="Feedback Loop CLI")
    sub = ap.add_subparsers(dest="cmd")

    p_metrics = sub.add_parser("metrics", help="Métricas tenant")
    p_metrics.add_argument("--tenant", required=True)

    p_lead = sub.add_parser("lead", help="Feedback de lead")
    p_lead.add_argument("--lead-id", required=True)

    p_pending = sub.add_parser("pending", help="Mejoras pendientes")
    p_pending.add_argument("--tenant")

    p_suggest = sub.add_parser("suggest", help="Sugerir mejoras")
    p_suggest.add_argument("--tenant", required=True)

    args = ap.parse_args()

    # DB por defecto
    db = str(Path.home() / ".openclaw" / "workspace" / "feedback_loop.db")
    loop = FeedbackLoop(db)

    if args.cmd == "metrics":
        print(json.dumps(loop.get_tenant_metrics(args.tenant), indent=2, ensure_ascii=False))
    elif args.cmd == "lead":
        events = loop.get_lead_feedback(args.lead_id)
        actions = loop.get_lead_actions(args.lead_id)
        print(f"Eventos: {len(events)} | Acciones: {len(actions)}")
        for e in events:
            print(f"  [{e['timestamp']}] {e['tipo']}: {e['valor']}")
        for a in actions:
            print(f"  [{a['applied_at']}] {a['rule_applied']}: {a['score_delta']:+d} → {a['action']}")
    elif args.cmd == "pending":
        improvements = loop.get_pending_improvements(args.tenant)
        print(f"Mejoras pendientes: {len(improvements)}")
        for i in improvements:
            print(f"  [{i['prompt_id']}] {i['old_score']:.0f}→{i['new_score']:.0f}: {i['reason']}")
    elif args.cmd == "suggest":
        metrics = loop.get_tenant_metrics(args.tenant)
        suggestions = get_suggested_prompts(args.tenant, [])
        for s in suggestions:
            print(f"  → {s}")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
