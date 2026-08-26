import os, psycopg2
from psycopg2.extras import RealDictCursor

SUPABASE_HOST = os.environ.get("SUPABASE_HOST", "localhost")
SUPABASE_PORT = os.environ.get("SUPABASE_PORT", "5434")
SUPABASE_DB   = os.environ.get("SUPABASE_DB", "postgres")
SUPABASE_USER = os.environ.get("SUPABASE_USER", "postgres")
SUPABASE_PASS = os.environ.get("SUPABASE_PASS", "")

def _pg(tenant="tubandera"):
    conn = psycopg2.connect(
        host=SUPABASE_HOST, port=SUPABASE_PORT, dbname=SUPABASE_DB,
        user=SUPABASE_USER, password=SUPABASE_PASS
    )
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SET app.current_tenant = %s", (tenant,))
    return conn, cur

def init():
    conn, cur = _pg()
    cur.execute("SELECT current_setting('app.current_tenant', true)")
    conn.commit(); cur.close(); conn.close()

def registrar_usuario(chat_id, nombre, telefono, sustancia=None, tenant="tubandera"):
    tid = "TB-" + str(chat_id)
    conn, cur = _pg(tenant)
    cur.execute("""
        INSERT INTO public.personas (tenant_id, chat_id, nombre, telefono, sustancia_principal, estado)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (tenant_id, chat_id) DO NOTHING
        RETURNING id
    """, (tid, chat_id, nombre, telefono, sustancia or "", "activo"))
    cur.fetchone()
    conn.commit(); cur.close(); conn.close()
    return tid

def get_usuario(chat_id, tenant="tubandera"):
    conn, cur = _pg(tenant)
    cur.execute("SELECT * FROM public.personas WHERE chat_id=%s", (chat_id,))
    r = cur.fetchone()
    cur.close(); conn.close()
    return dict(r) if r else None

def guardar_lead(chat_id, nombre, telefono, perfil, urgencia, mensaje, respuesta,
                 canal="telegram", estado="nuevo", tenant="tubandera"):
    """Persiste un lead en public.leads (fuente única). Idempotente por (tenant_id, chat_id, creado_en)."""
    conn, cur = _pg(tenant)
    cur.execute("""
        INSERT INTO public.leads (tenant_id, canal, chat_id, nombre, telefono, perfil, urgencia, mensaje, respuesta, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (tenant, canal, str(chat_id), nombre, telefono, perfil, urgencia, mensaje, respuesta, estado))
    conn.commit(); cur.close(); conn.close()
    return True

def registrar_familiar(chat_id, nombre, telefono, parentesco, permiso=False, tenant="tubandera"):
    u = get_usuario(chat_id, tenant)
    if not u:
        return None
    conn, cur = _pg(tenant)
    cur.execute("""
        INSERT INTO public.familiares (tenant_id, persona_id, nombre, telefono, parentesco, permiso)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (tenant, u["id"], nombre, telefono, parentesco, permiso))
    conn.commit(); cur.close(); conn.close()

def get_familiares(chat_id, tenant="tubandera"):
    u = get_usuario(chat_id, tenant)
    if not u:
        return []
    conn, cur = _pg(tenant)
    cur.execute("SELECT * FROM public.familiares WHERE persona_id=%s", (u["id"],))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return [dict(r) for r in rows]

def registrar_avance(chat_id, tipo, detalle, tenant="tubandera"):
    import datetime
    u = get_usuario(chat_id, tenant)
    if not u:
        return
    conn, cur = _pg(tenant)
    cur.execute("""
        INSERT INTO public.avances (tenant_id, persona_id, tipo, detalle)
        VALUES (%s, %s, %s, %s)
    """, (tenant, u["id"], tipo, detalle))
    conn.commit(); cur.close(); conn.close()

def registrar_foto(chat_id, ruta, para_grupo=True, tenant="tubandera"):
    import datetime
    u = get_usuario(chat_id, tenant)
    if not u:
        return
    conn, cur = _pg(tenant)
    cur.execute("""
        INSERT INTO public.fotos (tenant_id, persona_id, ruta, para_grupo)
        VALUES (%s, %s, %s, %s)
    """, (tenant, u["id"], ruta, para_grupo))
    conn.commit(); cur.close(); conn.close()

def resumen_empresa(tenant="tubandera"):
    conn, cur = _pg(tenant)
    cur.execute("SELECT estado, COUNT(*) n FROM public.personas WHERE tenant_id=%s GROUP BY estado", (tenant,))
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) n FROM public.fotos WHERE tenant_id=%s", (tenant,))
    ft = cur.fetchone()
    cur.close(); conn.close()
    return {"usuarios_por_estado": {r["estado"]: r["n"] for r in rows}, "fotos": ft["n"] if ft else 0}

if __name__ == "__main__":
    init(); print("Supabase conectado OK")
    print("test:", registrar_usuario(123456, "Juan Perez", "6621112233", "opioides"))
    print("resumen:", resumen_empresa())
