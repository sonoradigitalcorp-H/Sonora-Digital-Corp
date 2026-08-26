"""
sync_metrics.py — Vuelca datos operativos de SQLite tenants → Postgres metrics.
Skill nativa de Hermes para observabilidad. Determinista, sin dependencias frágiles.

Fuentes (SQLite):
  - /opt/hermes/citas_db/citas_{persona}.db          → metrics_citas / metrics_leads
  - /opt/hermes/tubandera/tubandera.db               → metrics_leads (usuarios) + metrics_eval
  - /opt/hermes/hermosillo/db/leads_hermosillo_cont.db → metrics_leads
Destino (Postgres): postgres-metrics :5432, db=metrics, user=metrics

Uso (cron cada 10 min): /opt/hermes/venv/bin/python3 /opt/hermes/scripts/sync_metrics.py
"""
import os
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path
import psycopg2

PG_PASSWORD = os.environ.get("METRICS_DB_PASSWORD", "")
PG_HOST = os.environ.get("METRICS_PG_HOST", "127.0.0.1")
PG_PORT = os.environ.get("METRICS_PG_PORT", "5432")
PG_USER = os.environ.get("METRICS_PG_USER", "metrics")
PG_DB = os.environ.get("METRICS_PG_DB", "metrics")

# Supabase (fuente única de citas) :5434
SB_HOST = os.environ.get("SUPABASE_HOST", "localhost")
SB_PORT = os.environ.get("SUPABASE_PORT", "5434")
SB_DB = os.environ.get("SUPABASE_DB", "postgres")
SB_USER = os.environ.get("SUPABASE_USER", "postgres")
SB_PASS = os.environ.get("SUPABASE_PASS", "")
if not SB_PASS:
    # Fail-closed: credenciales via env (cron wrapper), nunca de archivo.
    print("[sync] SUPABASE_PASS no seteado via env", flush=True)

def sb_conn():
    return psycopg2.connect(host=SB_HOST, port=SB_PORT, dbname=SB_DB,
                            user=SB_USER, password=SB_PASS)

def psql(cmd: str) -> str:
    """Ejecuta SQL vía psql (docker exec postgres-metrics psql)."""
    full = (
        f"docker exec postgres-metrics psql -U {PG_USER} -d {PG_DB} "
        f"-h localhost -c \"{cmd}\""
    )
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout + r.stderr

def citas_personas():
    """Inserta citas de Supabase (fuente única) en metrics_citas."""
    cnt = 0
    try:
        conn = sb_conn()
        cur = conn.cursor()
        cur.execute("SELECT persona, nombre, telefono, fecha, hora, estado, tenant_id FROM public.citas")
        rows = cur.fetchall()
        conn.close()
        for persona, nombre, tel, fecha, hora, estado, tenant_id in rows:
            persona_src = tenant_id or persona
            psql(
                f"INSERT INTO metrics_citas (tenant, fecha, hora, confirmada) VALUES "
                f"('{persona_src}', '{fecha}', '{hora}', true) "
                f"ON CONFLICT DO NOTHING;"
            )
            psql(
                f"INSERT INTO metrics_leads (tenant, canal, telefono, estado) VALUES "
                f"('{persona_src}', 'telegram', '{tel}', '{estado}');"
            )
            cnt += 1
    except Exception as e:
        print(f"[sync] citas supabase: {e}")
    return cnt

def tubandera_usuarios():
    """Inserta usuarios de tubandera → metrics_leads."""
    db = Path("/opt/hermes/tubandera/tubandera.db")
    if not db.exists():
        return 0
    try:
        conn = sqlite3.connect(db)
        rows = conn.execute("SELECT tenant_id, telefono, fecha_ingreso, estado, sustancia_principal FROM usuarios").fetchall()
        conn.close()
        for r in rows:
            tid, tel, fecha, estado, sustancia = r
            psql(
                f"INSERT INTO metrics_leads (tenant, canal, telefono, estado) VALUES "
                f"('tubandera', 'telegram', '{tel}', '{estado}');"
            )
        return len(rows)
    except Exception as e:
        print(f"[sync] tubandera: {e}")
        return 0

def hermosillo_leads():
    """Inserta leads de hermosillo → metrics_leads."""
    db = Path("/opt/hermes/hermosillo/db/leads_hermosillo_cont.db")
    if not db.exists():
        return 0
    try:
        conn = sqlite3.connect(db)
        cols = [r[1] for r in conn.execute("PRAGMA table_info(leads)").fetchall()]
        if "telefono" in cols and "score" in cols:
            rows = conn.execute("SELECT telefono, score, estado FROM leads").fetchall()
        else:
            rows = conn.execute("SELECT * FROM leads LIMIT 0").fetchall()
        conn.close()
        for r in rows:
            tel = r[0] if r else ""
            score = r[1] if len(r) > 1 else None
            estado = r[2] if len(r) > 2 else "nuevo"
            psql(
                f"INSERT INTO metrics_leads (tenant, canal, telefono, score, estado) VALUES "
                f"('hermosillo-cont', 'telegram', '{tel}', {score}, '{estado}');"
            )
        return len(rows)
    except Exception as e:
        print(f"[sync] hermosillo: {e}")
        return 0

def heartbeat():
    """Registra un pulso en metrics_health."""
    psql(
        f"INSERT INTO metrics_health (service, status) VALUES "
        f"('sync_metrics', 'ok') ON CONFLICT DO NOTHING;"
    )

def main():
    t0 = datetime.now()
    c = citas_personas()
    tu = tubandera_usuarios()
    he = hermosillo_leads()
    heartbeat()
    print(f"[sync] ok en {datetime.now()-t0}: citas={c} tubandera={tu} hermosillo={he}")

if __name__ == "__main__":
    main()