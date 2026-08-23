import sqlite3, os, json
DB="/opt/hermes/tubandera/tubandera.db"
def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
    c=conn(); c.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY, tenant_id TEXT UNIQUE, chat_id INTEGER,
        nombre TEXT, telefono TEXT, fecha_ingreso TEXT, estado TEXT DEFAULT activo,
        sustancia_principal TEXT, notas TEXT
    );
    CREATE TABLE IF NOT EXISTS familiares (
        id INTEGER PRIMARY KEY, usuario_id INTEGER, nombre TEXT, telefono TEXT,
        parentesco TEXT, permiso INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS avances (
        id INTEGER PRIMARY KEY, usuario_id INTEGER, fecha TEXT, tipo TEXT, detalle TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    );
    CREATE TABLE IF NOT EXISTS fotos (
        id INTEGER PRIMARY KEY, usuario_id INTEGER, fecha TEXT, ruta TEXT, para_grupo INTEGER DEFAULT 0,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    );
    """); c.commit(); c.close()
def registrar_usuario(chat_id, nombre, telefono, sustancia=None):
    c=conn(); tid="TB-"+str(chat_id)
    c.execute("INSERT OR IGNORE INTO usuarios(tenant_id,chat_id,nombre,telefono,sustancia_principal) VALUES(?,?,?,?,?)",
              (tid,chat_id,nombre,telefono,sustancia)); c.commit(); c.close(); return tid
def registrar_familiar(usuario_id, nombre, telefono, parentesco, permiso=0):
    c=conn(); c.execute("INSERT INTO familiares(usuario_id,nombre,telefono,parentesco,permiso) VALUES(?,?,?,?,?)",
                        (usuario_id,nombre,telefono,parentesco,permiso)); c.commit(); c.close()
def get_usuario(chat_id):
    c=conn(); r=c.execute("SELECT * FROM usuarios WHERE chat_id=?",(chat_id,)).fetchone(); c.close(); return dict(r) if r else None
def get_familiares(usuario_id):
    c=conn(); r=c.execute("SELECT * FROM familiares WHERE usuario_id=?",(usuario_id,)).fetchall(); c.close(); return [dict(x) for x in r]
def registrar_avance(usuario_id, tipo, detalle):
    import datetime; c=conn()
    c.execute("INSERT INTO avances(usuario_id,fecha,tipo,detalle) VALUES(?,?,?,?)",
              (usuario_id, datetime.datetime.now().isoformat(), tipo, detalle)); c.commit(); c.close()
def registrar_foto(usuario_id, ruta, para_grupo=1):
    import datetime; c=conn()
    c.execute("INSERT INTO fotos(usuario_id,fecha,ruta,para_grupo) VALUES(?,?,?,?)",
              (usuario_id, datetime.datetime.now().isoformat(), ruta, para_grupo)); c.commit(); c.close()
def resumen_empresa():
    c=conn(); r=c.execute("SELECT estado, COUNT(*) n FROM usuarios GROUP BY estado").fetchall()
    ft=c.execute("SELECT COUNT(*) n FROM fotos").fetchone(); c.close()
    return {"usuarios_por_estado":{x["estado"]:x["n"] for x in r},"fotos":ft["n"]}
if __name__=="__main__":
    init(); print("DB inicializada", DB)
    print("test:", registrar_usuario(123456,"Juan Perez","6621112233","opioides"))
    print("resumen:", resumen_empresa())
