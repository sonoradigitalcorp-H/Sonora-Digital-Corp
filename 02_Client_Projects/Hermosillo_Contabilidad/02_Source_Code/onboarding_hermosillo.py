#!/usr/bin/env python3
"""onboarding_hermosillo.py — Motor determinista de onboarding para Hermosillo Contabilidad (Nathaly).

Dual CRM: leads + lead_intelligence (resumen, siguiente acción).
Scoring integrado (cold/warm/hot determinista, reusa lead_scoring genérico).
Cero LLM en este módulo. Todo determinista.
Zona horaria: America/Hermosillo.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pytz

# Reuso del scoring genérico de SDD 0004
import sys
INFRA = Path(__file__).resolve().parent.parent.parent.parent / "01_Core_Platform" / "03_Agentic_Infrastructure"
sys.path.insert(0, str(INFRA))
from lead_scoring import calculate_lead_score, ScoringResult  # noqa: E402

HERMOSILLO_TZ = pytz.timezone("America/Hermosillo")
UTC_TZ = pytz.UTC

# Servicios oficiales (espejo del OKF hermosillo-cont.servicios)
SERVICIOS = [
    "contabilidad",
    "administracion",
    "manifestacion_importacion",
    "marketing",
    "consultas_sat",
    "citas_sat",
]

SERVICIOS_ALIAS = {
    "manifestacion": "manifestacion_importacion",
    "importacion": "manifestacion_importacion",
    "pedimento": "manifestacion_importacion",
    "cita ante el sat": "citas_sat",
    "cita sat": "citas_sat",
    "citas sat": "citas_sat",
    "citas": "citas_sat",
    "consulta sat": "consultas_sat",
    "contabilidad": "contabilidad",
    "cuentas": "contabilidad",
    "declaracion": "contabilidad",
    "impuestos": "contabilidad",
    "iva": "contabilidad",
    "isr": "contabilidad",
    "administracion": "administracion",
    "administrativo": "administracion",
    "nomina": "administracion",
    "marketing": "marketing",
    "publicidad": "marketing",
    "sat": "consultas_sat",
}


def normalizar_servicio(texto: str) -> Optional[str]:
    """Mapa alias → servicio canónico. None si no coincide."""
    if not texto:
        return None
    t = texto.lower().strip()
    for alias, servicio in SERVICIOS_ALIAS.items():
        if alias in t:
            return servicio
    # match directo
    if t in SERVICIOS:
        return t
    return None


class OnboardingHermosillo:
    """Motor determinista de onboarding del tenant hermosillo-cont."""

    def __init__(self, db_path: str, tenant: str = "hermosillo-cont"):
        self.db_path = db_path
        self.tenant = tenant
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id TEXT PRIMARY KEY,
                    tenant TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    nombre TEXT,
                    negocio TEXT,
                    servicio TEXT,
                    fecha TEXT,
                    hora TEXT,
                    estado TEXT DEFAULT 'nuevo',
                    score INTEGER DEFAULT 0,
                    classification TEXT DEFAULT 'COLD',
                    canal TEXT,
                    urgencia_alta INTEGER DEFAULT 0,
                    diagnostico_aceptado INTEGER DEFAULT 0,
                    creado_en TEXT,
                    actualizado_en TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lead_intelligence (
                    lead_id TEXT PRIMARY KEY,
                    resumen TEXT,
                    next_action TEXT,
                    notificado_en TEXT,
                    FOREIGN KEY (lead_id) REFERENCES leads(id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversaciones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tenant TEXT NOT NULL,
                    chat_id TEXT NOT NULL,
                    canal TEXT DEFAULT 'telegram',
                    rol TEXT NOT NULL,
                    texto TEXT,
                    intencion TEXT,
                    creado_en TEXT
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_convs_chat ON conversaciones(chat_id, creado_en)")
            conn.commit()

    def registrar_conversacion(self, chat_id: str, rol: str, texto: str, canal: str = "telegram", intencion: str = ""):
        """Registra cada mensaje real de la conversación (historial)."""
        try:
            now = datetime.now(UTC_TZ).isoformat()
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT INTO conversaciones (tenant, chat_id, canal, rol, texto, intencion, creado_en) VALUES (?,?,?,?,?,?,?)",
                    (self.tenant, chat_id, canal, rol, texto, intencion, now)
                )
                conn.commit()
        except Exception as e:
            print(f"[CONV] error: {e}")

    def historial_chat(self, chat_id: str, limit: int = 20) -> list[dict]:
        """Devuelve historial real de conversación de un chat."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM conversaciones WHERE chat_id=? ORDER BY id DESC LIMIT ?",
                (chat_id, limit)
            ).fetchall()
        return [dict(r) for r in reversed(rows)]

    def registrar_lead(self, chat_id: str, datos: dict, canal: str = "telegram") -> dict:
        """Registra/actualiza lead y calcula score. Retorna lead completo."""
        now = datetime.now(UTC_TZ).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT * FROM leads WHERE chat_id=? AND tenant=?",
                (chat_id, self.tenant)
            ).fetchone()
            if row:
                lead_id = row[0]
                conn.execute(
                    """UPDATE leads SET nombre=?, negocio=?, servicio=?, fecha=?, hora=?,
                       urgencia_alta=?, diagnostico_aceptado=?, estado='nuevo', canal=?,
                       actualizado_en=? WHERE id=?""",
                    (datos.get("nombre"), datos.get("negocio"), datos.get("servicio"),
                     datos.get("fecha"), datos.get("hora"),
                     1 if datos.get("urgencia_alta") else 0,
                     1 if datos.get("diagnostico_aceptado") else 0,
                     canal, now, lead_id)
                )
            else:
                lead_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO leads (id, tenant, chat_id, nombre, negocio, servicio,
                       fecha, hora, estado, canal, urgencia_alta, diagnostico_aceptado,
                       creado_en, actualizado_en)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (lead_id, self.tenant, chat_id, datos.get("nombre"), datos.get("negocio"),
                     datos.get("servicio"), datos.get("fecha"), datos.get("hora"),
                     "nuevo", canal, 1 if datos.get("urgencia_alta") else 0,
                     1 if datos.get("diagnostico_aceptado") else 0, now, now)
                )

        # Scoring determinista
        lead_scoring = calculate_lead_score({
            "nombre": datos.get("nombre"),
            "empresa": datos.get("negocio"),
            "servicio": datos.get("servicio"),
            "fecha": datos.get("fecha"),
            "hora": datos.get("hora"),
            "urgencia_alta": datos.get("urgencia_alta"),
            "presupuesto_mencionado": datos.get("presupuesto_mencionado"),
            "es_tomador_decisiones": datos.get("es_tomador_decisiones"),
            "respondio_voz": datos.get("respondio_voz"),
            "click_diagnostico": datos.get("click_diagnostico"),
        })
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE leads SET score=?, classification=? WHERE id=?",
                (lead_scoring.score, lead_scoring.classification, lead_id)
            )
            conn.commit()

        lead = {
            "id": lead_id,
            "tenant": self.tenant,
            "chat_id": chat_id,
            **datos,
            "score": lead_scoring.score,
            "classification": lead_scoring.classification,
            "factores": lead_scoring.factores,
            "next_action": lead_scoring.next_action,
        }
        return lead

    def agendar_cita(self, chat_id: str, fecha: str, hora: str, servicio: str = "citas_sat") -> dict:
        """Agenda cita con validación de zona America/Hermosillo. Retorna cita o error."""
        try:
            dt_str = f"{fecha} {hora}"
            dt = HERMOSILLO_TZ.localize(datetime.strptime(dt_str, "%Y-%m-%d %H:%M"))
        except Exception:
            return {"ok": False, "error": "Formato de fecha inválido. Usa YYYY-MM-DD y HH:MM (24h)."}
        if dt < datetime.now(HERMOSILLO_TZ):
            return {"ok": False, "error": "La fecha ya pasó. Elige una fecha futura."}

        now = datetime.now(UTC_TZ).isoformat()
        lead_id = None
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id FROM leads WHERE chat_id=? AND tenant=? ORDER BY creado_en DESC LIMIT 1",
                (chat_id, self.tenant)
            ).fetchone()
            if row:
                lead_id = row[0]
                conn.execute(
                    "UPDATE leads SET fecha=?, hora=?, servicio=?, estado='cita_agendada', actualizado_en=? WHERE id=?",
                    (fecha, hora, servicio, now, lead_id)
                )
            else:
                lead_id = str(uuid.uuid4())
                conn.execute(
                    """INSERT INTO leads (id, tenant, chat_id, servicio, fecha, hora, estado, canal, creado_en, actualizado_en)
                       VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (lead_id, self.tenant, chat_id, servicio, fecha, hora, "cita_agendada", "telegram", now, now)
                )
            conn.commit()

        # Recalcular score (cita agendada = +15)
        with sqlite3.connect(self.db_path) as conn:
            lead_row = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
        if lead_row:
            sr = calculate_lead_score({
                "nombre": lead_row[3], "empresa": lead_row[4], "servicio": lead_row[5],
                "fecha": lead_row[6], "hora": lead_row[7],
            })
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("UPDATE leads SET score=?, classification=? WHERE id=?", (sr.score, sr.classification, lead_id))
                conn.commit()
            return {
                "ok": True,
                "lead_id": lead_id,
                "fecha": fecha, "hora": hora, "servicio": servicio,
                "score": sr.score, "classification": sr.classification,
                "tz": "America/Hermosillo",
            }
        return {"ok": False, "error": "Lead no encontrado"}

    def get_template_notificacion(self, lead: dict) -> str:
        """Template CRM para notificar a Nathaly."""
        return (
            f"📋 LEAD {lead.get('classification', 'COLD')} (score {lead.get('score', 0)}) | "
            f"{lead.get('nombre', '?')} ({lead.get('negocio', '?')}) | "
            f"Servicio: {lead.get('servicio', '?')} | "
            f"Cita: {lead.get('fecha', '-')} {lead.get('hora', '-')} | "
            f"Canal: {lead.get('canal', 'telegram')}"
        )

    def get_nombre(self, chat_id: str) -> str:
        """Devuelve el nombre conocido del chat (memoria) o '' si no se conoce."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute(
                    "SELECT nombre FROM leads WHERE chat_id=? AND tenant=? AND nombre IS NOT NULL "
                    "AND nombre != '' ORDER BY creado_en DESC LIMIT 1",
                    (chat_id, self.tenant)
                ).fetchone()
            return row[0] if row else ""
        except Exception:
            return ""

    def guardar_nombre(self, chat_id: str, nombre: str, canal: str = "telegram"):
        """Persiste/actualiza el nombre del lead por chat_id (memoria de identidad)."""
        if not nombre:
            return None
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id FROM leads WHERE chat_id=? AND tenant=? ORDER BY creado_en DESC LIMIT 1",
                (chat_id, self.tenant)
            ).fetchone()
            now = datetime.now(UTC_TZ).isoformat()
            if row:
                conn.execute(
                    "UPDATE leads SET nombre=?, actualizado_en=?, canal=? WHERE id=?",
                    (nombre, now, canal, row[0])
                )
            else:
                lead_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO leads (id, tenant, chat_id, nombre, estado, canal, creado_en, actualizado_en) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (lead_id, self.tenant, chat_id, nombre, "nuevo", canal, now, now)
                )
            conn.commit()
        return nombre


# ─── Paquetes (3) — LIBERTAD DE TIEMPO ─────────────────────────────
# Sin precios: la cotización exacta la da Nathaly (regla del agente).
PAQUETES = [
    {
        "id": "basico",
        "nombre": "Orden",
        "titulo": "Paquete Orden — Tu contabilidad al día",
        "beneficios": [
            "Contabilidad mensual (estados financieros, IVA e ISR al día)",
            "Declaraciones sin sorpresas del SAT",
            "Acompañamiento y resolución de dudas por WhatsApp",
        ],
        "tiempo": "Recupera ~8 horas al mes dedicadas a recibos y trámites",
        "cta": "Cotización exacta por WhatsApp con Nathaly",
    },
    {
        "id": "pro",
        "nombre": "Control",
        "titulo": "Paquete Control — Tu negocio administrado",
        "beneficios": [
            "Todo lo del paquete Orden",
            "Administración: nómina, flujo de caja, control de gastos",
            "Asistente IA para TI: dashboard y recordatorios fiscales",
            "Consulta mensual con Nathaly",
        ],
        "tiempo": "Recupera +16 horas al mes y decisiones con datos claros",
        "cta": "Cotiza por WhatsApp →",
    },
    {
        "id": "empresa",
        "nombre": "Crecimiento",
        "titulo": "Paquete Crecimiento — Todo tu negocio liberado",
        "beneficios": [
            "Todo lo del paquete Control",
            "Manifestación de importación y citas SAT gestionadas",
            "Asistente IA para tus CLIENTES (chat 24/7 en tu negocio)",
            "Asistente IA para tu equipo interno",
            "Educación y acompañamiento en nuevas tecnologías",
        ],
        "tiempo": "Libera tu tiempo para enfocarte en crecer",
        "cta": "Agenda una demo del sistema →",
    },
]


def get_paquetes() -> list[dict]:
    """Devuelve los 3 paquetes (copia segura)."""
    return [dict(p) for p in PAQUETES]


def formato_paquetes() -> str:
    """Formato lista legible de los 3 paquetes para mostrarlos."""
    salida = ["📦 **Paquetes Hermosillo Contabilidad**\n"]
    for p in PAQUETES:
        salida.append(f"**{p['titulo']}**")
        salida.append(p['tiempo'])
        for b in p['beneficios']:
            salida.append(f"  ✅ {b}")
        salida.append(f"  → {p['cta']}\n")
    salida.append("💬 El costo exacto te lo da Nathaly en WhatsApp — el diagnóstico inicial es GRATIS.")
    return "\n".join(salida)


if __name__ == "__main__":
    import tempfile
    db = tempfile.mktemp(suffix=".db")
    eng = OnboardingHermosillo(db)
    lead = eng.registrar_lead("12345", {"nombre": "Juan", "negocio": "Ferret", "servicio": "contabilidad", "fecha": "2026-08-20", "hora": "10:00"})
    print(json.dumps(lead, indent=2, ensure_ascii=False))
    print("Notif:", eng.get_template_notificacion(lead))
    cita = eng.agendar_cita("12345", "2026-08-21", "11:30")
    print("Cita:", json.dumps(cita, indent=2, ensure_ascii=False))
    print("Leads hoy:", len(eng.leads_hoy()))