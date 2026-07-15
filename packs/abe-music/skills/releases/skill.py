from datetime import datetime

RELEASES = []

def handle(action, titulo=None, fecha_lanzamiento=None, tipo="single", **kwargs):
    if action == "programar":
        return programar(titulo, fecha_lanzamiento, tipo)
    elif action == "notificar":
        return notificar(titulo)
    elif action == "distribuir":
        return distribuir(titulo)
    elif action == "listar":
        return listar()
    return {"success": False, "message": f"Acción no soportada: {action}"}

def programar(titulo, fecha_lanzamiento, tipo):
    release = {
        "titulo": titulo or "Sin título",
        "fecha": fecha_lanzamiento or "2026-08-01",
        "tipo": tipo,
        "estado": "programada",
        "creada": datetime.now().isoformat(),
    }
    RELEASES.append(release)
    return {"success": True, "data": release, "message": f"Release '{release['titulo']}' programada para {release['fecha']}"}

def notificar(titulo):
    return {"success": True, "data": {
        "canales": ["whatsapp", "telegram"],
        "mensaje": f"🎵 ¡Nuevo {titulo} disponible! Escúchalo ya.",
        "status": "enviado"
    }}

def distribuir(titulo):
    return {"success": True, "data": {
        "plataformas": ["Spotify", "Apple Music", "YouTube Music", "TikTok"],
        "estado": "distribuyendo",
        "distribuidor": "DistroKid",
    }}

def listar():
    if not RELEASES:
        return {"success": True, "data": {"releases": [], "total": 0}}
    return {"success": True, "data": {"releases": RELEASES, "total": len(RELEASES)}}
