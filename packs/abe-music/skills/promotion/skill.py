from datetime import datetime

CAMPANIAS = []

def handle(action, nombre=None, presupuesto=None, plataforma_ads="meta", **kwargs):
    if action == "crear_campania":
        return crear_campania(nombre, presupuesto, plataforma_ads)
    elif action == "pausar_campania":
        return pausar_campania(nombre)
    elif action == "medir_roi":
        return medir_roi(nombre)
    elif action == "listar_campanias":
        return listar_campanias()
    return {"success": False, "message": f"Acción no soportada: {action}"}

def crear_campania(nombre, presupuesto, plataforma_ads):
    campania = {
        "nombre": nombre or "Campaña sin nombre",
        "presupuesto": presupuesto or 1000,
        "plataforma": plataforma_ads,
        "estado": "activa",
        "creada": datetime.now().isoformat(),
    }
    CAMPANIAS.append(campania)
    return {"success": True, "data": campania, "message": f"Campaña '{campania['nombre']}' creada en {plataforma_ads}"}

def pausar_campania(nombre):
    for c in CAMPANIAS:
        if c["nombre"] == nombre:
            c["estado"] = "pausada"
            return {"success": True, "data": c, "message": f"Campaña '{nombre}' pausada"}
    return {"success": False, "message": f"Campaña '{nombre}' no encontrada"}

def medir_roi(nombre):
    for c in CAMPANIAS:
        if c["nombre"] == nombre:
            return {"success": True, "data": {
                "campania": nombre,
                "inversion": c["presupuesto"],
                "alcance": 45200,
                "clics": 2340,
                "conversiones": 89,
                "roi": 3.4,
                "costo_por_conversion": 11.24,
            }}
    return {"success": True, "data": {
        "campania": "Todas",
        "inversion": 5000,
        "alcance": 142300,
        "clics": 8910,
        "conversiones": 312,
        "roi": 4.2,
        "costo_por_conversion": 16.03,
    }}

def listar_campanias():
    if not CAMPANIAS:
        return {"success": True, "data": {"campanias": [], "total": 0}}
    return {"success": True, "data": {"campanias": CAMPANIAS, "total": len(CAMPANIAS)}}
