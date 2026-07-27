from datetime import datetime, date, timedelta

AGENDA = []

EVENTOS_EJEMPLO = [
    {"fecha": "2026-08-15", "lugar": "Foro Sol, CDMX", "estado": "disponible"},
    {"fecha": "2026-08-22", "lugar": "Auditorio Nacional, CDMX", "estado": "disponible"},
    {"fecha": "2026-09-05", "lugar": "Palacio de los Deportes, Guadalajara", "estado": "disponible"},
    {"fecha": "2026-09-12", "lugar": "Teatro Diana, Guadalajara", "estado": "reservado"},
    {"fecha": "2026-10-03", "lugar": "Escenario GNP, Monterrey", "estado": "disponible"},
]

def handle(action, fecha=None, lugar=None, fee=None, **kwargs):
    if action == "consultar_disponibilidad":
        return consultar_disponibilidad()
    elif action == "cotizar":
        return cotizar(fecha, lugar, fee)
    elif action == "confirmar":
        return confirmar(fecha, lugar)
    elif action == "cancelar":
        return cancelar(fecha, lugar)
    elif action == "listar_eventos":
        return listar_eventos()
    return {"success": False, "message": f"Acción no soportada: {action}"}

def consultar_disponibilidad():
    disponibles = [e for e in EVENTOS_EJEMPLO if e["estado"] == "disponible"]
    return {"success": True, "data": {"fechas_disponibles": disponibles, "total": len(disponibles)}}

def cotizar(fecha, lugar, fee):
    cotizacion = {
        "folio": f"COT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "fecha_evento": fecha or "Por definir",
        "lugar": lugar or "Por definir",
        "fee_propuesto": fee or 50000,
        "incluye": [
            "Presentación en vivo (60-90 min)",
            "Sonido e iluminación básicos",
            "Rider técnico",
            "Transporte para 5 personas",
        ],
        "no_incluye": [
            "Hospedaje (si aplica fuera de CDMX)",
            "Vuelos internacionales",
        ],
        "valida_hasta": (date.today() + timedelta(days=15)).isoformat(),
        "estado": "cotizada",
    }
    AGENDA.append(cotizacion)
    return {"success": True, "data": cotizacion, "message": f"Cotización {cotizacion['folio']} generada"}

def confirmar(fecha, lugar):
    return {"success": True, "data": {
        "evento": f"{lugar} - {fecha}",
        "estado": "confirmado",
        "contrato": f"https://drive.google.com/abe-music/contratos/{fecha}.pdf",
    }, "message": f"Evento confirmado: {lugar} el {fecha}"}

def cancelar(fecha, lugar):
    return {"success": True, "data": {"evento": f"{lugar} - {fecha}", "estado": "cancelado"},
            "message": f"Evento cancelado: {lugar} el {fecha}"}

def listar_eventos():
    return {"success": True, "data": {"eventos": EVENTOS_EJEMPLO, "total": len(EVENTOS_EJEMPLO)}}
