#!/usr/bin/env python3
"""onboarding_engine.py — Motor determinista de onboarding Aztrotech (v2).

DUAL CRM: leads + lead_intelligence (resumen, objeciones, next_action).
Scoring integrado (cold/warm/hot determinista).
Feedback loop integrado.
Cero LLM en este módulo. Todo determinista.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import pytz

from lead_scoring import calculate_lead_score, ScoringResult, get_template_notificacion_cesar
from feedback_loop import FeedbackLoop, FeedbackEvent


HERMOSILLO_TZ = pytz.timezone("America/Hermosillo")
UTC_TZ = pytz.UTC


class OnboardingEngine:
    """Motor determinista de onboarding para un tenant. Dual CRM."""

    def __init__(self, db_path: str, tenant: str = "aztrotech", feedback_db: str = None):
        self.db_path = db_path
        self.tenant = tenant
        self._init_db()
        # Feedback loop
        fb_path = feedback_db or str(Path(db_path).parent / "feedback_loop.db")
        self.feedback = FeedbackLoop(fb_path)

    def _init_db(self):
        """Crea tablas leads + lead_intelligence si no existen."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # Tabla leads
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    tenant TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    nombre TEXT,
                    empresa TEXT,
                    giro TEXT,
                    tamano_equipo TEXT,
                    servicio TEXT,
                    fecha TEXT,
                    hora TEXT,
                    estado TEXT DEFAULT 'nuevo',
                    score INTEGER DEFAULT 0,
                    classification TEXT DEFAULT 'COLD',
                    canal TEXT,
                    presupuesto_mencionado INTEGER DEFAULT 0,
                    urgencia_alta INTEGER DEFAULT 0,
                    es_tomador_decisiones INTEGER DEFAULT 0,
                    respondio_voz INTEGER DEFAULT 0,
                    pidio_asset INTEGER DEFAULT 0,
                    click_diagnostico INTEGER DEFAULT 0,
                    diagnostico_completado INTEGER DEFAULT 0,
                    creado_en TEXT DEFAULT (datetime('now')),
                    actualizado_en TEXT DEFAULT (datetime('now')),
                    notas TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_tenant ON leads(tenant)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_fecha ON leads(fecha)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_leads_score ON leads(score DESC)")

            # Tabla lead_intelligence (dual CRM)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lead_intelligence (
                    lead_id TEXT PRIMARY KEY,
                    resumen_empresa TEXT,
                    objeciones TEXT DEFAULT '[]',
                    contraargumentos TEXT DEFAULT '[]',
                    dolor_detectado TEXT,
                    presupuesto_estimado TEXT DEFAULT 'unknown',
                    autoridad TEXT DEFAULT 'unknown',
                    urgency_level TEXT DEFAULT 'media',
                    servicio_recomendado TEXT,
                    caso_exito_relevante TEXT,
                    diagnostico_recomendado TEXT,
                    next_action TEXT,
                    nota_para_cesar TEXT,
                    cesar_notificado_en TEXT,
                    audio_script TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    updated_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)

            # Tabla interacciones (para engagement tracking)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interacciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    canal TEXT,
                    duracion_segundos REAL,
                    metadata TEXT DEFAULT '{}',
                    timestamp TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _now_utc(self) -> str:
        return datetime.utcnow().isoformat()

    def _to_utc(self, fecha: str, hora: str) -> str:
        local_dt = HERMOSILLO_TZ.localize(datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M"))
        utc_dt = local_dt.astimezone(UTC_TZ)
        return utc_dt.isoformat()

    def _from_utc(self, utc_iso: str) -> tuple[str, str]:
        utc_dt = datetime.fromisoformat(utc_iso.replace("Z", "+00:00"))
        if utc_dt.tzinfo is None:
            utc_dt = UTC_TZ.localize(utc_dt)
        local_dt = utc_dt.astimezone(HERMOSILLO_TZ)
        return local_dt.strftime("%Y-%m-%d"), local_dt.strftime("%H:%M")

    def capture_lead(self, tenant: str, chat_id: str, fields: dict[str, Any]) -> tuple[str, ScoringResult]:
        """Captura lead, calcula score, persiste en dual CRM. Retorna (lead_id, scoring)."""
        lead_id = str(uuid.uuid4())[:8]

        # Extraer campos booleanos
        presupuesto = fields.get("presupuesto_mencionado", False)
        urgencia = fields.get("urgencia_alta", False)
        autoridad = fields.get("es_tomador_decisiones", False)
        voz = fields.get("respondio_voz", False)
        asset = fields.get("pidio_asset", False)
        diagnostico = fields.get("click_diagnostico", False)

        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO leads (id, tenant, chat_id, nombre, empresa, giro, tamano_equipo,
                    servicio, canal, presupuesto_mencionado, urgencia_alta, es_tomador_decisiones,
                    respondio_voz, pidio_asset, click_diagnostico, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'nuevo')
            """, (
                lead_id, tenant, chat_id,
                fields.get("nombre", ""),
                fields.get("empresa", ""),
                fields.get("giro", ""),
                fields.get("tamano_equipo", ""),
                fields.get("servicio", ""),
                fields.get("canal", "telegram"),
                1 if presupuesto else 0,
                1 if urgencia else 0,
                1 if autoridad else 0,
                1 if voz else 0,
                1 if asset else 0,
                1 if diagnostico else 0,
            ))

        # Calcular score
        lead_for_scoring = {**fields, "lead_id": lead_id}
        scoring = calculate_lead_score(lead_for_scoring)

        # Actualizar score
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE leads SET score = ?, classification = ?
                WHERE id = ?
            """, (scoring.score, scoring.classification, lead_id))

        return lead_id, scoring

    def get_lead(self, lead_id: str) -> dict[str, Any] | None:
        """Obtiene lead + intelligence combinados."""
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
            if not row:
                return None
            lead = dict(row)

            # Agregar intelligence
            intel = conn.execute(
                "SELECT * FROM lead_intelligence WHERE lead_id = ?", (lead_id,)
            ).fetchone()
            if intel:
                lead["intelligence"] = dict(intel)
                if lead["intelligence"].get("objeciones"):
                    lead["intelligence"]["objeciones"] = json.loads(lead["intelligence"]["objeciones"])
                if lead["intelligence"].get("contraargumentos"):
                    lead["intelligence"]["contraargumentos"] = json.loads(lead["intelligence"]["contraargumentos"])

            # Convertir fecha/hora a local
            if lead.get("fecha"):
                try:
                    lead["fecha_local"], lead["hora_local"] = self._from_utc(lead["fecha"])
                except Exception:
                    pass

            return lead

    def update_lead(self, lead_id: str, fields: dict[str, Any]) -> bool:
        """Actualiza campos de un lead + recalcula score."""
        allowed = {"nombre", "empresa", "giro", "tamano_equipo", "servicio", "fecha", "hora",
                   "estado", "canal", "notas", "presupuesto_mencionado", "urgencia_alta",
                   "es_tomador_decisiones", "respondio_voz", "pidio_asset", "click_diagnostico",
                   "diagnostico_completado"}
        update_fields = {k: v for k, v in fields.items() if k in allowed}
        if not update_fields:
            return False

        update_fields["actualizado_en"] = self._now_utc()
        # Convertir booleanos a int
        for k in ["presupuesto_mencionado", "urgencia_alta", "es_tomador_decisiones",
                   "respondio_voz", "pidio_asset", "click_diagnostico", "diagnostico_completado"]:
            if k in update_fields:
                update_fields[k] = 1 if update_fields[k] else 0

        set_clause = ", ".join(f"{k} = ?" for k in update_fields)
        values = list(update_fields.values()) + [lead_id]

        with self._get_conn() as conn:
            conn.execute(f"UPDATE leads SET {set_clause} WHERE id = ?", values)

            # Recalcular score
            lead = dict(conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone() or {})
            if lead:
                scoring = calculate_lead_score(lead)
                conn.execute("UPDATE leads SET score = ?, classification = ? WHERE id = ?",
                           (scoring.score, scoring.classification, lead_id))

        return True

    def save_intelligence(self, lead_id: str, intelligence: dict) -> bool:
        """Guarda intelligence del lead (resumen, objeciones, next_action)."""
        objeciones = json.dumps(intelligence.get("objeciones_probables", []), ensure_ascii=False)
        contraargumentos = json.dumps(intelligence.get("contraargumentos", []), ensure_ascii=False)

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO lead_intelligence
                (lead_id, resumen_empresa, objeciones, contraargumentos, dolor_detectado,
                 presupuesto_estimado, autoridad, urgency_level, servicio_recomendado,
                 caso_exito_relevante, diagnostico_recomendado, next_action, nota_para_cesar,
                 audio_script, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                lead_id,
                intelligence.get("resumen_empresa", ""),
                objeciones,
                contraargumentos,
                intelligence.get("dolor_detectado", ""),
                intelligence.get("presupuesto_estimado", "unknown"),
                intelligence.get("autoridad", "unknown"),
                intelligence.get("urgency_level", "media"),
                intelligence.get("servicio_recomendado", ""),
                intelligence.get("caso_exito_relevante", ""),
                intelligence.get("diagnostico_recomendado", ""),
                intelligence.get("next_action", ""),
                intelligence.get("nota_para_cesar", ""),
                intelligence.get("audio_script", ""),
            ))
        return True

    def check_availability(self, fecha: str, hora: str) -> bool:
        """Verifica disponibilidad (determinista)."""
        utc_iso = self._to_utc(fecha, hora)
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT 1 FROM leads WHERE fecha = ? AND estado IN ('cita_agendada', 'confirmada')",
                (utc_iso,)
            ).fetchone()
            return row is None

    def schedule_cita(self, lead_id: str, fecha: str, hora: str) -> dict[str, Any]:
        """Agenda cita + recalcula score + retorna resultado."""
        if not self.check_availability(fecha, hora):
            return {"success": False, "error": f"Fecha {fecha} {hora} ocupada", "lead_id": lead_id}

        utc_iso = self._to_utc(fecha, hora)
        self.update_lead(lead_id, {"fecha": utc_iso, "hora": hora, "estado": "cita_agendada"})

        return {"success": True, "lead_id": lead_id, "fecha": fecha, "hora": hora, "fecha_utc": utc_iso}

    def notify_cesar(self, lead_id: str, canales: list[str] = None) -> dict[str, bool]:
        """Notifica a César con template CRM completo (resumen + objeciones + next_action)."""
        lead = self.get_lead(lead_id)
        if not lead:
            return {"telegram": False, "whatsapp": False, "error": "Lead no encontrado"}

        # Obtener intelligence
        intel = lead.get("intelligence", {})

        # Obtener scoring
        scoring = calculate_lead_score(lead)

        # Generar template CRM
        cesar_msg = get_template_notificacion_cesar(lead, scoring, intel)

        canales = canales or ["telegram", "whatsapp"]
        results = {}

        if "telegram" in canales:
            try:
                from onboarding_aztrotech import send_text, CHAT_CESAR
                results["telegram"] = send_text(cesar_msg, CHAT_CESAR)
            except Exception as e:
                print(f"[ERROR] Telegram: {e}")
                results["telegram"] = False

        if "whatsapp" in canales:
            try:
                import subprocess
                r = subprocess.run([
                    "wacli", "send_text",
                    "--to", "5216621072254",
                    "--message", cesar_msg
                ], capture_output=True, text=True, timeout=30)
                results["whatsapp"] = r.returncode == 0
            except Exception as e:
                print(f"[ERROR] WhatsApp: {e}")
                results["whatsapp"] = False

        # Marcar como notificado
        with self._get_conn() as conn:
            conn.execute("UPDATE leads SET estado = 'notificado_cesar' WHERE id = ?", (lead_id,))
            conn.execute("""
                UPDATE lead_intelligence SET cesar_notificado_en = datetime('now')
                WHERE lead_id = ?
            """, (lead_id,))

        return results

    def record_interaction(self, lead_id: str, tipo: str, canal: str = None,
                          duracion: float = None, metadata: dict = None) -> None:
        """Registra interacción + procesa feedback loop."""
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO interacciones (lead_id, tipo, canal, duracion_segundos, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (lead_id, tipo, canal, duracion, json.dumps(metadata or {}, ensure_ascii=False)))

        # Procesar feedback
        event = FeedbackEvent(
            lead_id=lead_id,
            tenant=self.tenant,
            tipo=tipo,
            valor=duracion or 1,
            metadata=metadata or {}
        )
        self.feedback.process_event(event)

    def list_leads(self, tenant: str = None, estado: str = None,
                   classification: str = None, limit: int = 50) -> list[dict]:
        """Lista leads con filtros, ordenados por score descendente."""
        tenant = tenant or self.tenant
        query = "SELECT * FROM leads WHERE tenant = ?"
        params = [tenant]

        if estado:
            query += " AND estado = ?"
            params.append(estado)
        if classification:
            query += " AND classification = ?"
            params.append(classification)

        query += " ORDER BY score DESC, creado_en DESC LIMIT ?"
        params.append(limit)

        with self._get_conn() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_leads_hoy(self) -> list[dict]:
        """Leads de hoy (zona horaria Hermosillo)."""
        hoy = datetime.now(HERMOSILLO_TZ).strftime("%Y-%m-%d")
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM leads
                WHERE tenant = ? AND date(fecha) = ?
                ORDER BY score DESC
            """, (self.tenant, hoy)).fetchall()
            return [dict(row) for row in rows]

    def get_dashboard_stats(self) -> dict:
        """Estadísticas para dashboard de César/Mystic."""
        with self._get_conn() as conn:
            total = conn.execute("SELECT COUNT(*) as c FROM leads WHERE tenant = ?",
                               (self.tenant,)).fetchone()["c"]
            by_class = conn.execute("""
                SELECT classification, COUNT(*) as c FROM leads
                WHERE tenant = ? GROUP BY classification
            """, (self.tenant,)).fetchall()
            by_estado = conn.execute("""
                SELECT estado, COUNT(*) as c FROM leads
                WHERE tenant = ? GROUP BY estado
            """, (self.tenant,)).fetchall()
            avg_score = conn.execute("""
                SELECT AVG(score) as avg FROM leads WHERE tenant = ?
            """, (self.tenant,)).fetchone()["avg"]

            return {
                "tenant": self.tenant,
                "total_leads": total,
                "por_clasificacion": {r["classification"]: r["c"] for r in by_class},
                "por_estado": {r["estado"]: r["c"] for r in by_estado},
                "score_promedio": round(avg_score or 0, 1),
            }


def main():
    """CLI simple."""
    import argparse
    ap = argparse.ArgumentParser(description="Onboarding Engine v2 CLI")
    ap.add_argument("--db", default="leads_aztrotech.db")
    ap.add_argument("--tenant", default="aztrotech")
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("stats", help="Dashboard stats")
    sub.add_parser("hoy", help="Leads de hoy")

    p_list = sub.add_parser("list", help="Listar leads")
    p_list.add_argument("--classification", choices=["COLD", "WARM", "HOT"])
    p_list.add_argument("--limit", type=int, default=10)

    p_cap = sub.add_parser("capture", help="Capturar lead")
    p_cap.add_argument("--chat", required=True)
    p_cap.add_argument("--nombre", required=True)
    p_cap.add_argument("--empresa", required=True)
    p_cap.add_argument("--giro", default="otro")
    p_cap.add_argument("--tamano", default="2-5")
    p_cap.add_argument("--servicio", default="empleado_digital")
    p_cap.add_argument("--canal", default="telegram")

    p_intel = sub.add_parser("intelligence", help="Ver intelligence de lead")
    p_intel.add_argument("--lead", required=True)

    args = ap.parse_args()
    engine = OnboardingEngine(args.db, args.tenant)

    if args.cmd == "stats":
        print(json.dumps(engine.get_dashboard_stats(), indent=2, ensure_ascii=False))
    elif args.cmd == "hoy":
        for l in engine.get_leads_hoy():
            print(f"[{l.get('classification', '?')}] {l['nombre']} ({l['empresa']}) | Score: {l.get('score', 0)} | {l.get('fecha_local', '?')}")
    elif args.cmd == "list":
        leads = engine.list_leads(classification=args.classification, limit=args.limit)
        for l in leads:
            print(f"[{l.get('classification', '?')}] {l['nombre']} ({l['empresa']}) | Score: {l.get('score', 0)} | {l['estado']}")
    elif args.cmd == "capture":
        fields = {"nombre": args.nombre, "empresa": args.empresa, "giro": args.giro,
                  "tamano_equipo": args.tamano, "servicio": args.servicio, "canal": args.canal}
        lead_id, scoring = engine.capture_lead(args.tenant, args.chat, fields)
        print(f"Lead: {lead_id} | Score: {scoring.score} | {scoring.classification}")
        print(f"Next: {scoring.next_action}")
    elif args.cmd == "intelligence":
        lead = engine.get_lead(args.lead)
        if lead:
            print(json.dumps(lead.get("intelligence", "Sin intelligence"), indent=2, ensure_ascii=False))
        else:
            print("Lead no encontrado")
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
