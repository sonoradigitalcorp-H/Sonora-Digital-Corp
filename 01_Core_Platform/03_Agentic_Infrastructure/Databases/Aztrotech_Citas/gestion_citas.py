#!/usr/bin/env python3
"""gestion_citas.py — Agente de citas de Aztrotech (bot @Aztro_tech_bot).

Centraliza el ciclo de vida de una cita:
  alta  -> scoring cold/warm/hot + aviso a César y al usuario
  agenda -> recordatorios con anticipación + pedir confirmación/cambio de hora
  DB: SQLite local (leads y citas), multilingüe es/en/fr

Uso:
    python3 gestion_citas.py add --nombre "Pepe" --telefono "6621112233" \
        --empresa "Tacos El Güero" --servicio "Empleado Digital" \
        --fecha "2026-08-08" --hora "11:00" --idioma es --chat 12345678

    python3 gestion_citas.py list            # todas
    python3 gestion_citas.py recordar        # recordatorios vencidos HOY (cron)
    python3 gestion_citas.py score --recompute
"""
import argparse, json, os, sqlite3, sys
from datetime import datetime, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE / "citas.db"
LEADS_DIR = BASE / "leads"          # JSONs que escribe el agente (fs) al confirmar cita
SEG = 24 * 3600                     # segundos por día

# --- Telegram bot AztroTech ---
TELE = Path.home() / ".openclaw" / "secrets" / "telegram-aztroc.token"
CHAT_CESAR = "6621072254"           # WhatsApp César (msm via wacli)
CHAT_USUARIO = None                 # se llena por --chat

# scoring simple: cold/warm/hot según completitud y urgencia
SCORE_RULES = {
    "cold":   {"minutos": 7 * 24 * 60},   # sin teléfono/empresa/servicio -> seguimiento semanal
    "warm":   {"minutos": 3 * 24 * 60},   # datos completos -> seguimiento en 3 días
    "hot":    {"minutos": 24 * 60},       # cita agendada -> aviso inmediato + recordatorio 24h antes
}

PLANTILLAS = {
    "es": {
        "recibida": "📅 ¡Cita agendada {fecha} {hora}! Te confirmo por aquí. "
                    "César te manda la cotización a la medida. ¿Confirmas?",
        "recordatorio_6h": "⏰ {nombre}, tu cita con César (Aztrotech) es en "
                           "6 horas ({fecha} a las {hora}). ¿Confirmas o prefieres cambiar la hora?",
        "confirmado": "✅ ¡Confirmado! Te esperamos {fecha} {hora}. César te manda los datos.",
        "cambia": "🔄 Entendido. ¿Qué fecha y hora te acomoda?",
        "cesar_aviso": "📋 Cita {score}: {nombre} ({empresa}) — {servicio} — {fecha} {hora}. Tel: {telefono}",
    },
    "en": {
        "recibida": "📅 Appointment booked {fecha} {hora}! Confirming here. "
                    "César will send you a tailored quote. Confirm?",
        "recordatorio_6h": "⏰ {nombre}, your appointment with César (Aztrotech) "
                           "is in 6 hours ({fecha} at {hora}). Confirm or reschedule?",
        "confirmado": "✅ Confirmed! See you {fecha} {hora}. César will send the details.",
        "cambia": "🔄 Got it. What date and time works for you?",
        "cesar_aviso": "📋 {score} lead: {nombre} ({empresa}) — {servicio} — {fecha} {hora}. Tel: {telefono}",
    },
    "fr": {
        "recibida": "📅 Rendez-vous pris {fecha} {hora} ! Je confirme ici. "
                    "César vous envoie un devis sur mesure. Vous confirmez ?",
        "recordatorio_6h": "⏰ {nombre}, votre rendez-vous avec César (Aztrotech) "
                        "est dans 6 heures ({fecha} à {hora}). Confirmez ou changez l'heure ?",
        "confirmado": "✅ Confirmé ! À {fecha} {hora}. César vous envoie les détails.",
        "cambia": "🔄 Compris. Quelle date et heure vous conviennent ?",
        "cesar_aviso": "📋 {score} lead : {nombre} ({empresa}) — {servicio} — {fecha} {hora}. Tél : {telefono}",
    },
}


def con():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, telefono TEXT, empresa TEXT, servicio TEXT,
            fecha TEXT, hora TEXT, idioma TEXT DEFAULT 'es',
            chat TEXT, score TEXT DEFAULT 'warm',
            status TEXT DEFAULT 'pendiente',      -- pendiente|confirmada|cambiada|cancelada
            creado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            recordado_6h INTEGER DEFAULT 0
        )
    """)
    # migración: si la tabla vieja tenía recordado_dia/horas, la dejamos (legacy)
    try:
        cols = [r[1] for r in c.execute("PRAGMA table_info(citas)")]
        if "recordado_dia" in cols and "recordado_6h" not in cols:
            c.execute("ALTER TABLE citas ADD COLUMN recordado_6h INTEGER DEFAULT 0")
    except Exception:
        pass
    c.commit()
    return c


def score_lead(nombre, telefono, empresa, servicio, fecha):
    """cold/warm/hot: datos + fecha definida."""
    datos = sum(1 for v in (nombre, telefono, empresa, servicio) if v)
    if datos >= 4 and fecha:
        return "hot"
    if datos >= 3:
        return "warm"
    return "cold"


def telegram_token():
    return TELE.read_text().strip()


def send_telegram(chat, text):
    import requests
    r = requests.post(
        f"https://api.telegram.org/bot{telegram_token()}/sendMessage",
        data={"chat_id": chat, "text": text}, timeout=60)
    ok = r.json().get("ok", False)
    print(f"[TXT {'OK' if ok else 'FAIL'}] {chat}: {text[:50]}...")
    return ok


def notify_cesar(text):
    # WhatsApp César via wacli (CLI). wacli send-text falla en algunos contactos:
    # usar send-voice/file. Aquí probamos text y si falla, mejor por el pipeline de voz.
    import subprocess
    try:
        r = subprocess.run(["wacli", "send", "text", "--to", CHAT_CESAR,
                            "--message", text], capture_output=True, text=True, timeout=60)
        print(f"[WACLI {'OK' if r.returncode == 0 else 'FAIL'}] César: {text[:50]}...")
        if r.returncode != 0:
            print("  stderr:", r.stderr[-200:])
    except Exception as e:
        print("[WACLI ERROR]", e)


def add(args):
    c = con()
    score = score_lead(args.nombre, args.telefono, args.empresa, args.servicio, args.fecha)
    cur = c.execute("""
        INSERT INTO citas (nombre, telefono, empresa, servicio, fecha, hora,
                           idioma, chat, score)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, (args.nombre, args.telefono, args.empresa, args.servicio,
          args.fecha, args.hora, args.idioma, args.chat, score))
    c.commit()
    cid = cur.lastrowid
    print(f"[ALTA] #{cid} {score.upper()}: {args.nombre} | {args.fecha} {args.hora} | {args.empresa}")

    t = PLANTILLAS.get(args.idioma, PLANTILLAS["es"])
    if args.chat:
        send_telegram(args.chat, t["recibida"].format(
            fecha=args.fecha, hora=args.hora, nombre=args.nombre or ""))

    # Aviso a César SIEMPRE (WhatsApp) + mensaje resumen por texto del bot
    aviso = t["cesar_aviso"].format(
        score=score, nombre=args.nombre or "-", empresa=args.empresa or "-",
        servicio=args.servicio or "-", fecha=args.fecha or "-",
        hora=args.hora or "-", telefono=args.telefono or "-")
    notify_cesar(aviso)
    send_telegram(CHAT_CESAR, aviso) if False else None
    return cid


def list_citas(args):
    c = con()
    rows = c.execute("SELECT * FROM citas ORDER BY fecha, hora").fetchall()
    for r in rows:
        print(f"#{r['id']} [{r['status']}] {r['score'].upper():4} "
              f"{r['fecha']} {r['hora']}  {r['nombre']} ({r['empresa']}) {r['idioma']}")


def recordar(args):
    """Cron: recordatorio EXACTAMENTE 6 horas antes de la cita + pedir confirmación."""
    c = con()
    ahora = datetime.now()
    rows = c.execute(
        "SELECT * FROM citas WHERE status IN ('pendiente','confirmada')").fetchall()
    enviados = 0
    for r in rows:
        try:
            inicio = datetime.strptime(f"{r['fecha']} {r['hora'] or '09:00'}", "%Y-%m-%d %H:%M")
        except Exception:
            continue
        t = PLANTILLAS.get(r["idioma"], PLANTILLAS["es"])

        # 6 horas antes de la reunión pactada (una sola vez)
        if not r["recordado_6h"] and ahora >= inicio - timedelta(hours=6):
            msg = t["recordatorio_6h"].format(
                nombre=r["nombre"] or "amigo",
                hora=inicio.strftime("%H:%M"),
                fecha=inicio.strftime("%d/%m/%Y"))
            if r["chat"]:
                send_telegram(r["chat"], msg)
                c.execute("UPDATE citas SET recordado_6h=1 WHERE id=?", (r["id"],))
                enviados += 1
    c.commit()
    print(f"[RECORDATORIOS 6H] {enviados} enviados ahora.")


def ingest_leads(args):
    """Lee JSONs que deja el agente (tool fs) en LEADS_DIR y los da de alta."""
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    creados = 0
    saltados = 0
    for f in sorted(LEADS_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text())
            nombre = (d.get("nombre") or "").strip().lower()
            telefono = (d.get("telefono") or "").strip()
            fecha = d.get("fecha")
            # DEDUPE: si ya existe cita con mismo nombre+telefono+fecha, NO reenviar
            if nombre or telefono:
                existe = con().execute(
                    "SELECT id FROM citas WHERE lower(nombre)=? AND telefono=? AND fecha=?",
                    (nombre, telefono, fecha)).fetchone()
                if existe:
                    print(f"[DUP LEAD] {f.name}: ya existe cita #{existe['id']}. skip")
                    f.rename(f.with_suffix(".dup.json"))
                    saltados += 1
                    continue
            ns = argparse.Namespace(
                nombre=d.get("nombre"), telefono=telefono,
                empresa=d.get("empresa"), servicio=d.get("servicio"),
                fecha=fecha, hora=d.get("hora"),
                idioma=d.get("idioma", "es"), chat=d.get("chat"))
            add(ns)
            f.rename(f.with_suffix(".done.json"))
            creados += 1
        except Exception as e:
            print(f"[LEAD FAIL] {f.name}: {e}")
    print(f"[INGEST] {creados} leads nuevos, {saltados} duplicados saltados.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")

    a = sub.add_parser("add")
    a.add_argument("--nombre"); a.add_argument("--telefono"); a.add_argument("--empresa")
    a.add_argument("--servicio"); a.add_argument("--fecha"); a.add_argument("--hora")
    a.add_argument("--idioma", default="es"); a.add_argument("--chat")

    sub.add_parser("list")
    sub.add_parser("recordar")
    sub.add_parser("ingest")

    args = ap.parse_args()
    if args.cmd == "add": add(args)
    elif args.cmd == "list": list_citas(args)
    elif args.cmd == "recordar": recordar(args)
    elif args.cmd == "ingest": ingest_leads(args)
    else: ap.print_help()


if __name__ == "__main__":
    main()
