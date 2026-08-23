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

PG_PASSWORD = os.environ.get("METRICS_DB_PASSWORD", "changeme_secure_metrics_password")
PG_HOST = os.environ.get("METRICS_PG_HOST", "127.0.0.1")
PG_PORT = os.environ.get("METRICS_PG_PORT", "5432")
PG_USER = os.environ.get("METRICS_PG_USER", "metrics")
PG_DB = os.environ.get("METRICS_PG_DB", "metrics")

def psql(cmd: str) -> str:
    """Ejecuta SQL vía psql (docker exec postgres-metrics psql)."""
    full = (
        f"docker exec postgres-metrics psql -U {PG_USER} -d {PG_DB} "
        f"-h localhost -c \"{cmd}\""
    )
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=30)
    return r.stdout + r.stderr

def citas_personas():
    """Inserta citas de todas las DBs citas_{persona}.db en metrics_citas."""
    base_dir = Path("/opt/hermes/citas_db")
    if not base_dir.exists():
        return 0
    cnt = 0
    for db in base_dir.glob("citas_*.db"):
        persona = db.stem.replace("citas_", "")
        try:
            conn = sqlite3.connect(db)
            rows = conn.execute("SELECT id, persona, nombre, telefono, fecha, hora, estado FROM citas").fetchall()
            conn.close()
            for r in rows:
                cid, p, nombre, tel, fecha, hora, estado = r
                psql(
                    f"INSERT INTO metrics_citas (tenant, fecha, hora, confirmada) VALUES "
                    f"('{persona}', '{fecha}', '{hora}', true) "
                    f"ON CONFLICT DO NOTHING;"
                )
                psql(
                    f"INSERT INTO metrics_leads (tenant, canal, telefono, estado) VALUES "
                    f"('{persona}', 'telegram', '{tel}', '{estado}');"
                )
                cnt += 1
        except Exception as e:
            print(f"[sync] citas {persona}: {e}")
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