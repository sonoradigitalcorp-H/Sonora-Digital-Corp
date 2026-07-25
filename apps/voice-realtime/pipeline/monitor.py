import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("voice-realtime.monitor")

try:
    import psutil as _psutil

    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    _psutil = None
    logger.warning("psutil no disponible — todas las llamadas de monitoreo fallarán gracefulmente")


def _safe(call: str, fallback: Any = None) -> Any:
    """Ejecuta un atributo de psutil con captura de excepciones."""
    if not HAS_PSUTIL or _psutil is None:
        return fallback
    try:
        return call() if callable(call) else call
    except Exception as exc:
        logger.debug("psutil call failed: %s", exc, exc_info=True)
        return fallback


class SystemMonitor:
    """Monitoreo del sistema usando psutil para Mystic Voice.

    Todos los métodos son seguros ante ausencia de psutil
    y fallan gracefulmente devolviendo valores por defecto.
    """

    async def get_status(self) -> dict:
        """Devuelve un dict con el estado actual del sistema.

        Returns:
            dict con cpu_percent, ram_percent, ram_used_gb, ram_total_gb,
            disk_percent, disk_used_gb, disk_total_gb, uptime_days,
            top_processes (top 5 por cpu), boot_time
        """
        if not HAS_PSUTIL:
            return {"error": "psutil not available"}

        import asyncio

        loop = asyncio.get_running_loop()

        cpu = await loop.run_in_executor(None, _safe, lambda: _psutil.cpu_percent(interval=0.5), 0.0)
        ram = await loop.run_in_executor(None, _safe, lambda: _psutil.virtual_memory(), None)
        disk = await loop.run_in_executor(None, _safe, lambda: _psutil.disk_usage("/"), None)
        uptime = await loop.run_in_executor(None, _safe, lambda: _psutil.boot_time(), None)
        procs = await loop.run_in_executor(
            None,
            _safe,
            lambda: sorted(
                _psutil.process_iter(["name", "cpu_percent"]),
                key=lambda p: p.info.get("cpu_percent") or 0,
                reverse=True,
            )[:5],
            [],
        )
        boot_time_val = uptime

        ram_total = round((ram.total / (1024**3)) if ram else 0, 1)
        ram_used = round((ram.used / (1024**3)) if ram else 0, 1)
        ram_pct = round(ram.percent if ram else 0, 1)

        disk_total = round((disk.total / (1024**3)) if disk else 0, 1)
        disk_used = round((disk.used / (1024**3)) if disk else 0, 1)
        disk_pct = round(disk.percent if disk else 0, 1)

        uptime_days = 0.0
        if boot_time_val:
            try:
                uptime_delta = datetime.now() - datetime.fromtimestamp(boot_time_val)
                uptime_days = round(uptime_delta.total_seconds() / 86400, 1)
            except Exception:
                uptime_days = 0.0

        top_procs = []
        for p in procs:
            try:
                name = p.info.get("name", "?")
                cpu_pct = p.info.get("cpu_percent", 0) or 0
                top_procs.append({"name": name, "cpu_percent": round(cpu_pct, 1)})
            except Exception:
                continue

        return {
            "cpu_percent": round(cpu, 1),
            "ram_percent": ram_pct,
            "ram_used_gb": ram_used,
            "ram_total_gb": ram_total,
            "disk_percent": disk_pct,
            "disk_used_gb": disk_used,
            "disk_total_gb": disk_total,
            "uptime_days": uptime_days,
            "top_processes": top_procs,
            "boot_time": boot_time_val,
        }

    async def get_cpu_alert(self) -> dict | None:
        """Devuelve una alerta si CPU > 80 % o RAM > 90 %.

        Returns:
            dict con "level" y "message", o None si todo está normal.
        """
        if not HAS_PSUTIL:
            return None

        status = await self.get_status()
        if "error" in status:
            return None

        alerts = []
        if status["cpu_percent"] > 80:
            alerts.append(f"CPU al {status['cpu_percent']}%")
        if status["ram_percent"] > 90:
            alerts.append(f"RAM al {status['ram_percent']}%")

        if not alerts:
            return None

        level = "critical" if len(alerts) > 1 or status.get("cpu_percent", 0) > 90 or status.get("ram_percent", 0) > 95 else "warning"
        return {"level": level, "message": "Alerta del sistema: " + " y ".join(alerts) + "."}

    async def format_for_tts(self, status_dict: dict | None = None) -> str:
        """Genera un string en lenguaje natural para ser leído por TTS.

        Args:
            status_dict: resultado de get_status(). Si es None, se obtiene en vivo.

        Returns:
            Frase en español natural lista para voz.
        """
        if not HAS_PSUTIL:
            return "No tengo acceso al monitor del sistema en este momento."

        if status_dict is None:
            status_dict = await self.get_status()

        if "error" in status_dict:
            return "No tengo acceso al monitor del sistema en este momento."

        s = status_dict

        cpu = s["cpu_percent"]
        ram_pct = s["ram_percent"]
        ram_u = s["ram_used_gb"]
        ram_t = s["ram_total_gb"]
        disk_pct = s["disk_percent"]
        disk_u = s["disk_used_gb"]
        disk_t = s["disk_total_gb"]
        days = s["uptime_days"]
        procs = s.get("top_processes", [])

        lines = []

        if cpu < 50 and ram_pct < 70 and disk_pct < 80:
            lines.append("El sistema está estable.")
        elif cpu > 80 or ram_pct > 90:
            lines.append("El sistema está bajo carga.")
        else:
            lines.append("Estado del sistema:")

        parts = [f"CPU al {cpu}%"]
        parts.append(f"memoria RAM al {ram_pct}% ({ram_u} de {ram_t} GB)")
        parts.append(f"disco al {disk_pct}% ({disk_u} de {disk_t} GB)")

        lines.append(", ".join(parts) + ".")

        days_int = int(days)
        hours = round((days - days_int) * 24)
        if days_int > 0 and hours > 0:
            lines.append(f"Llevo {days_int} día{'s' if days_int != 1 else ''} y {hours} hora{'s' if hours != 1 else ''} encendido.")
        elif days_int > 0:
            lines.append(f"Llevo {days_int} día{'s' if days_int != 1 else ''} encendido.")
        else:
            lines.append("Acabo de iniciar.")

        if procs:
            top = procs[0]
            top_name = top["name"]
            top_cpu = top["cpu_percent"]
            if len(procs) > 1:
                second = procs[1]
                lines.append(
                    f"Los procesos más activos son: {top_name} con {top_cpu}% "
                    f"y {second['name']} con {second['cpu_percent']}%."
                )
            else:
                lines.append(f"El proceso que más recursos usa es {top_name} con el {top_cpu}% de CPU.")

        return " ".join(lines)
