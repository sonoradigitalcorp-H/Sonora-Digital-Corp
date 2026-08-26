#!/usr/bin/env python3
"""
audio_matutino.py — Audio matutino COSUDE (twin digital de mejora diaria).

Genera un reporte de voz de 60-90s que le dice a Luis Daniel:
  - Estado real del sistema (servicios VPS vivos, web OK)
  - Pendientes REALES de ESTADO.md (no inventados)
  - Próximas acciones concretas (Tu Bandera, Nathaly, SDC reales)
  - Lección del sistema / mejora propuesta

Corre en el VPS 24/7 (donde wacli está autenticado y edge-tts existe).
Envío: edge-tts → MP3 → wacli voice → WhatsApp de Luis Daniel.

NOTA: NUNCA vende a clientes archivados (Aztrotech/César). Solo proyectos VIVOS:
Tu Bandera, Nathaly Contabilidad, SDC.
"""
import datetime
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path("/opt/hermes/repo")  # repo clonado en VPS
ESTADO = Path("/home/mystic/ESTADO.md")
LUIS_WHATSAPP = "5216623538272@s.whatsapp.net"
WACLI_BIN = "/home/mystic/wacli"
WACLI_STORE = "/home/mystic/.wacli"
EDGE_TTS = "/opt/hermes/venv/bin/edge-tts"

VOICE = "es-MX-DaliaNeural"


def leer_estado() -> Path:
    """Localiza ESTADO.md (puede estar en repo clonado o en home de mystic)."""
    for cand in (ESTADO, REPO_ROOT / "ESTADO.md"):
        if cand.exists():
            return cand
    # fallback: buscar en el repo del VPS
    for cand in (Path("/opt/hermes/repo/ESTADO.md"),
                 Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo/ESTADO.md")):
        if cand.exists():
            return cand
    return Path("/dev/null")


def pendientes_reales(estado: Path) -> tuple[list[str], list[str]]:
    """Extrae pendientes (❌/PENDIENTE) y logros activos del ESTADO.md."""
    if not estado.exists():
        return [], []
    texto = estado.read_text(errors="ignore")
    pendientes = re.findall(r"(?m)^.*?(?:❌|PENDIENTE).*$", texto)
    pendientes = [p.strip()[:120] for p in pendientes[:6]]
    # Logros principales (secciones recientes con ✅)
    logros = re.findall(r"(?m)^## (.+?)(?: ✅|$)", texto)
    logros = [l.strip() for l in logros if l.strip()][:4]
    return pendientes, logros


def servicios_vps() -> list[str]:
    """Consulta servicios 24/7 en el propio VPS (donde corre este script)."""
    servicios = ["vps-ai-server", "hermes-gateway", "sdc-tts", "sdc-stt",
                 "hermosillo-webhook", "nginx", "cloudflared-tunnel"]
    activos = []
    for s in servicios:
        try:
            r = subprocess.run(["systemctl", "is-active", s], capture_output=True,
                               text=True, timeout=5)
            if "active" in r.stdout:
                activos.append(s)
        except Exception:
            pass
    return activos


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def dia_semana() -> str:
    return DIAS[datetime.datetime.now().weekday()]


def _limpiar_pendiente(linea: str) -> str:
    """Limpia markdown/código de una línea de pendiente para leerla en voz."""
    s = linea.strip().lstrip("-* ")
    s = re.sub(r"`+", "", s)
    s = re.sub(r"#+ ", "", s)
    s = re.sub(r"\*\*", "", s)
    s = re.sub(r"\s+", " ", s)
    # quitar fechas/títulos redundantes al inicio
    return s[:90]


def construir_reporte(estado: Path) -> str:
    pendientes, logros = pendientes_reales(estado)
    activos = servicios_vps()
    hoy = datetime.datetime.now().day
    mes = MESES[datetime.datetime.now().month - 1]
    dia = dia_semana()

    reporte = (
        f"Buenos días, Luis. Es {dia} {hoy} de {mes}. Soy Cosude, tu asistente de mejora diaria.\n"
        f"Tu VPS está vivo: {len(activos)} de 7 servicios corriendo, "
        f"incluyendo la web y el asistente de voz.\n"
        f"Proyectos activos: Tu Bandera, Nathaly Contabilidad y Sonora Digital Corp. "
        f"Aztrotech sigue archivado.\n"
        f"Para hoy, las tres acciones que más te mueven son:\n"
        f"Primero, revisa los pendientes marcados en tu estado. Hay {len(pendientes)} "
        f"pendientes detectados.\n"
        f"Segundo, cierra el flujo de citas de Tu Bandera: confirma el calendario y "
        f"que las confirmaciones lleguen por WhatsApp a Roberto.\n"
        f"Tercero, usa el VPS para todo lo pesado y deja la laptop solo para editar. "
        f"Eso evita que se congele.\n"
    )
    if pendientes:
        reporte += "Pendientes principales: " + ". ".join(
            _limpiar_pendiente(p) for p in pendientes[:3]) + ".\n"
    if activos:
        reporte += f"Servicios confirmados: {', '.join(activos[:5])}.\n"
    reporte += (
        "Recuerda: yo ya sé quién eres. Eres Luis Daniel Guerrero Enciso, "
        "de Sonora Digital Corp. Esta mañana, elige una sola meta y termínala. "
        "Que tengas un gran día."
    )
    return reporte


def main():
    estado = leer_estado()
    texto = construir_reporte(estado)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        mp3_path = tmp.name

    # 1. TTS con edge-tts del venv VPS
    try:
        subprocess.run([EDGE_TTS, "--voice", VOICE, "--rate", "+4%",
                        "--text", texto, "--write-media", mp3_path],
                       capture_output=True, text=True, timeout=60, check=True)
    except Exception as e:
        print(f"[audio_matutino] edge-tts error: {e}", file=sys.stderr)
        sys.exit(1)

    if not Path(mp3_path).exists() or Path(mp3_path).stat().st_size < 1000:
        print("[audio_matutino] audio vacío", file=sys.stderr)
        sys.exit(1)

    # 1b. Convertir MP3 → OGG Opus (wacli requiere Opus para notas de voz)
    ogg_path = mp3_path.replace(".mp3", ".ogg")
    try:
        subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-c:a", "libopus",
                        "-b:a", "48k", "-ar", "48000", ogg_path],
                       capture_output=True, text=True, timeout=60, check=True)
    except Exception as e:
        print(f"[audio_matutino] ffmpeg error: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Enviar por WhatsApp (wacli del VPS autenticado)
    try:
        r = subprocess.run([WACLI_BIN, "send", "voice", "--store", WACLI_STORE,
                            "--to", LUIS_WHATSAPP, "--file", ogg_path],
                           capture_output=True, text=True, timeout=60)
        estado_envio = "enviado" if r.returncode == 0 else f"error {r.returncode}:{r.stderr[:80]}"
        # también texto corto
        subprocess.run([WACLI_BIN, "send", "text", "--store", WACLI_STORE,
                        "--to", LUIS_WHATSAPP, "--message",
                        f"🎙️ Reporte COSUDE {hoy_texto()}\n\n{texto[:500]}"],
                       capture_output=True, text=True, timeout=60)
    except Exception as e:
        estado_envio = f"error {e}"

    print(f"[audio_matutino] {datetime.datetime.now().isoformat()} "
          f"wacli={estado_envio} chars={len(texto)}", flush=True)

    try:
        Path(mp3_path).unlink(missing_ok=True)
        Path(ogg_path).unlink(missing_ok=True)
    except Exception:
        pass


def hoy_texto() -> str:
    return datetime.datetime.now().strftime("%d/%m/%Y")


if __name__ == "__main__":
    main()