from datetime import datetime

TRANSACCIONES = []

def handle(action, monto=None, concepto=None, categoria=None, periodo="2026-06", **kwargs):
    if action == "registrar_ingreso":
        return registrar_ingreso(monto, concepto, categoria)
    elif action == "registrar_gasto":
        return registrar_gasto(monto, concepto, categoria)
    elif action == "reporte_mensual":
        return reporte_mensual(periodo)
    elif action == "conciliar":
        return conciliar(periodo)
    elif action == "resumen":
        return resumen()
    return {"success": False, "message": f"Acción no soportada: {action}"}

def registrar_ingreso(monto, concepto, categoria="presentaciones"):
    txn = {
        "tipo": "ingreso",
        "monto": monto or 0,
        "concepto": concepto or "Sin concepto",
        "categoria": categoria,
        "fecha": datetime.now().isoformat(),
    }
    TRANSACCIONES.append(txn)
    return {"success": True, "data": txn, "message": f"Ingreso registrado: ${monto:,.2f} - {concepto}"}

def registrar_gasto(monto, concepto, categoria="produccion"):
    txn = {
        "tipo": "gasto",
        "monto": monto or 0,
        "concepto": concepto or "Sin concepto",
        "categoria": categoria,
        "fecha": datetime.now().isoformat(),
    }
    TRANSACCIONES.append(txn)
    return {"success": True, "data": txn, "message": f"Gasto registrado: ${monto:,.2f} - {concepto}"}

def reporte_mensual(periodo):
    return {"success": True, "data": {
        "periodo": periodo,
        "ingresos": 185000,
        "gastos": 62300,
        "utilidad": 122700,
        "utilidad_pct": 66.3,
        "top_ingresos": [
            {"concepto": "Presentación Foro Sol", "monto": 85000},
            {"concepto": "Regalías Spotify", "monto": 32000},
            {"concepto": "Booking fee", "monto": 18000},
        ],
        "top_gastos": [
            {"concepto": "Producción", "monto": 25000},
            {"concepto": "Marketing", "monto": 15000},
            {"concepto": "Transporte", "monto": 8900},
        ],
    }}

def conciliar(periodo):
    return {"success": True, "data": {
        "periodo": periodo,
        "transacciones_conciliadas": 42,
        "discrepancias": 2,
        "detalle": "Se detectaron 2 cargos duplicados en Contpaqi. Se requiere revisión manual.",
    }, "message": "Conciliación completada con 2 discrepancias. Revisar timbrado manual."}

def resumen():
    total_ingresos = sum(t["monto"] for t in TRANSACCIONES if t["tipo"] == "ingreso")
    total_gastos = sum(t["monto"] for t in TRANSACCIONES if t["tipo"] == "gasto")
    return {"success": True, "data": {
        "transacciones": len(TRANSACCIONES),
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance": total_ingresos - total_gastos,
    }}
