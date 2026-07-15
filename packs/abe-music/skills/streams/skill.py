import json
from datetime import datetime, timedelta

PLATAFORMAS = {
    "spotify": {"name": "Spotify", "icon": "🎵"},
    "apple_music": {"name": "Apple Music", "icon": "🍎"},
    "youtube": {"name": "YouTube", "icon": "▶️"},
    "tiktok": {"name": "TikTok", "icon": "📱"},
}

def handle(action, plataforma=None, periodo="30d", **kwargs):
    if action == "consultar":
        return consultar(plataforma, periodo)
    elif action == "analizar":
        return analizar(plataforma, periodo)
    elif action == "reportar":
        return reportar(plataforma, periodo)
    else:
        return {"success": False, "message": f"Acción no soportada: {action}"}

def consultar(plataforma, periodo):
    dias = int(periodo.replace("d", ""))
    data = {
        "total_streams": 145892,
        "plataformas": [],
        "crecimiento": 12.4,
        "top_cancion": "Nueva Ola",
    }
    if plataforma:
        pf = PLATAFORMAS.get(plataforma, {})
        data["plataformas"].append({
            "nombre": pf.get("name", plataforma),
            "streams": 45321,
            "oyentes_unicos": 12340,
        })
    else:
        for pid, pf in PLATAFORMAS.items():
            data["plataformas"].append({
                "nombre": pf["name"],
                "streams": 45321 if pid == "spotify" else 38920 if pid == "apple_music" else 28901 if pid == "youtube" else 32750,
                "oyentes_unicos": 12340 if pid == "spotify" else 8901 if pid == "apple_music" else 7820,
            })
    return {"success": True, "data": data}

def analizar(plataforma, periodo):
    return {"success": True, "data": {
        "pico_streams": "2026-06-15",
        "mejor_plataforma": "Spotify",
        "trend": "up",
        "insight": "Tus streams crecieron 12.4% este mes. Spotify domina con el 31% del total."
    }}

def reportar(plataforma, periodo):
    return {"success": True, "data": {
        "reporte_url": f"https://dashboard.abe-music.app/reports/streams-{periodo}.pdf",
        "formato": "PDF",
        "generado": datetime.now().isoformat(),
    }}
