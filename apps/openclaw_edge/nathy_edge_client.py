"""
Nathy Edge Client — Cliente Windows para Nathy Conta.

Hace 3 cosas:
1. Organiza el desorden: clasifica XMLs/PDFs por cliente, RFC, fecha
2. Procesa: envía al VPS para validación CFDI, OCR, extracción
3. Notifica: alertas Windows cuando algo necesita atención

Estructura:
  C:\NathyConta\Inbox\          ← arrastra tus archivos aquí
  C:\NathyConta\Clientes\       ← organizado automáticamente
  C:\NathyConta\Procesados\     ← ya enviados al VPS
  C:\NathyConta\Errores\        ← fallaron
  C:\NathyConta\Pendientes\     ← no se pudo clasificar
  C:\NathyConta\Duplicados\     ← archivos repetidos
  C:\NathyConta\Logs\           ← registros

Uso:
  python nathy_edge_client.py
"""

import hashlib
import json
import logging
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("nathy.edge")

PROCESSED_FILES: set[str] = set()

NS_CFDI = "http://www.sat.gob.mx/cfd/4"
NS_TFD = "http://www.sat.gob.mx/TimbreFiscalDigital"

SUB_DIRS = [
    "Inbox", "Clientes", "Procesados", "Errores",
    "Pendientes", "Duplicados", "Logs", "Config"
]

DEFAULT_CONFIG = {
    "vps": {
        "url": "https://vps.sonoradigitalcorp.com",
        "api_key": "",
        "enabled": False
    },
    "device": {
        "id": "nathy-laptop",
        "name": "Nathy Conta"
    },
    "paths": {
        "root": r"C:\NathyConta",
        "watch_delay": 1.0
    },
    "clientes": {
        "detectar_automatico": True,
        "crear_carpetas": True
    },
    "allowed_extensions": [".xml", ".pdf", ".XML", ".PDF"],
    "max_file_size_mb": 20,
    "logging": {
        "level": "INFO",
        "file": r"C:\NathyConta\Logs\nathy-edge.log"
    }
}


def load_config(path: str) -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
        _deep_merge(cfg, user_cfg)
    return cfg


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def setup_directories(root: str) -> dict[str, Path]:
    dirs = {}
    for sub in SUB_DIRS:
        p = Path(root) / sub
        p.mkdir(parents=True, exist_ok=True)
        dirs[sub] = p
    return dirs


def file_hash(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def notify(title: str, message: str) -> None:
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
    except Exception:
        logger.info(f"[NOTIF] {title}: {message}")


def _parse_cfdi_xml(content: bytes) -> dict | None:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return None
    ns = {"cfdi": NS_CFDI, "tfd": NS_TFD}
    comp = root if root.tag == f"{{{NS_CFDI}}}Comprobante" else root.find(".//cfdi:Comprobante", ns)
    if comp is None:
        return None
    emisor = comp.find("cfdi:Emisor", ns)
    receptor = comp.find("cfdi:Receptor", ns)
    tfd = comp.find(".//tfd:TimbreFiscalDigital", ns)
    return {
        "rfc_emisor": emisor.get("Rfc", "") if emisor is not None else "",
        "rfc_receptor": receptor.get("Rfc", "") if receptor is not None else "",
        "total": float(comp.get("Total", 0)),
        "subtotal": float(comp.get("SubTotal", 0)),
        "fecha": comp.get("Fecha", ""),
        "uuid": tfd.get("UUID", "") if tfd is not None else "",
        "tipo_comprobante": comp.get("TipoDeComprobante", "I"),
        "moneda": comp.get("Moneda", "MXN"),
    }


def _identify_client(metadata: dict) -> str:
    """Identify client by RFC receptor. Returns a normalized name."""
    rfc = metadata.get("rfc_receptor", "")
    if rfc:
        return rfc
    return "desconocido"


def _generate_filename(metadata: dict, ext: str) -> str:
    tipo_map = {"I": "INGRESO", "E": "EGRESO", "P": "PAGO", "N": "NOMINA", "T": "TRASLADO"}
    rfc = metadata.get("rfc_emisor", "XXXX")
    fecha = metadata.get("fecha", "")[:10] if metadata.get("fecha") else ""
    fecha_clean = fecha.replace("-", "")
    tipo = tipo_map.get(metadata.get("tipo_comprobante", "I"), "CFDI")
    uuid_short = metadata.get("uuid", "")[:8] if metadata.get("uuid") else ""
    return f"{rfc}_{fecha_clean}_{tipo}_{uuid_short}{ext}"


def organize_file(filepath: Path, dirs: dict[str, Path]) -> dict:
    """Clasifica y organiza un archivo, devuelve resultado."""
    ext = filepath.suffix.lower()
    if ext not in (".xml", ".pdf"):
        return {"status": "ignored", "reason": "extensión no soportada"}

    metadata = None
    if ext == ".xml":
        try:
            content = filepath.read_bytes()
            metadata = _parse_cfdi_xml(content)
        except Exception as e:
            logger.warning(f"Error parseando XML {filepath.name}: {e}")

    if not metadata:
        return {"status": "pendiente", "reason": "no se pudo extraer metadatos"}

    client = _identify_client(metadata)
    new_name = _generate_filename(metadata, ext)
    hash_hex = file_hash(filepath)

    # Check duplicates
    for dup_check in dirs["Clientes"].rglob("*.xml"):
        if dup_check.name == new_name:
            _safe_move(filepath, dirs["Duplicados"] / new_name)
            return {"status": "duplicado", "reason": f"ya existe: {dup_check}"}

    # Create client folder structure: Clientes/{RFC}/{Año}/{Mes}/
    fecha = metadata.get("fecha", "")
    año = fecha[:4] if len(fecha) >= 4 else "sin-fecha"
    mes = fecha[5:7] if len(fecha) >= 7 else "00"
    tipo_map = {"I": "facturas", "E": "facturas", "P": "pagos",
                 "N": "nominas", "T": "traslados"}
    tipo_carpeta = tipo_map.get(metadata.get("tipo_comprobante", "I"), "otros")

    dest_dir = dirs["Clientes"] / client / año / mes / tipo_carpeta
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / new_name

    _safe_move(filepath, dest_path)

    return {
        "status": "organizado",
        "client": client,
        "rfc_emisor": metadata.get("rfc_emisor", ""),
        "uuid": metadata.get("uuid", ""),
        "total": metadata.get("total", 0),
        "archivo": new_name,
        "ruta": str(dest_path),
    }


def _safe_move(src: Path, dest: Path) -> None:
    if dest.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest = dest.with_stem(f"{dest.stem}_{ts}")
    os.rename(str(src), str(dest))


def _write_log(logs_dir: Path, entry: dict) -> None:
    log_path = logs_dir / "operations.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class NathyInboxHandler(FileSystemEventHandler):
    def __init__(self, cfg: dict, dirs: dict[str, Path]):
        self.cfg = cfg
        self.dirs = dirs
        self.client = None
        if cfg["vps"]["enabled"] and cfg["vps"]["api_key"]:
            self.client = httpx.Client(
                base_url=cfg["vps"]["url"].rstrip("/"),
                headers={
                    "Authorization": f"Bearer {cfg['vps']['api_key']}",
                    "X-Device-ID": cfg["device"]["id"],
                },
                timeout=60.0,
            )

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = Path(event.src_path)
        if filepath.suffix not in self.cfg["allowed_extensions"]:
            return
        self._process_file(filepath)

    def _process_file(self, filepath: Path):
        if str(filepath) in PROCESSED_FILES:
            return
        PROCESSED_FILES.add(str(filepath))

        logger.info(f"Archivo detectado: {filepath.name}")
        time.sleep(1.0)

        # Step 1: Organize locally
        result = organize_file(filepath, self.dirs)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "archivo_original": filepath.name if filepath.exists() else "(moved)",
            "resultado": result,
        }

        if result["status"] == "organizado":
            msg = f"✓ {result['client']} | ${result['total']:,.2f}"
            notify("Nathy — Organizado", msg)
            _write_log(self.dirs["Logs"], {**log_entry, "evento": "organizado"})

            # Step 2: Send to VPS if configured
            if self.client and result.get("ruta"):
                self._send_to_vps(Path(result["ruta"]), result)

        elif result["status"] == "duplicado":
            notify("Nathy — Duplicado", f"{filepath.name} ya existía")
            _write_log(self.dirs["Logs"], {**log_entry, "evento": "duplicado"})

        else:
            _safe_move(filepath, self.dirs["Pendientes"] / filepath.name)
            notify("Nathy — Pendiente", f"{filepath.name} no se pudo clasificar")
            _write_log(self.dirs["Logs"], {**log_entry, "evento": "pendiente"})

    def _send_to_vps(self, filepath: Path, result: dict):
        try:
            with open(filepath, "rb") as f:
                files = {"file": (filepath.name, f, "application/octet-stream")}
                resp = self.client.post("/edge/inbox", files=files)
                if resp.status_code == 200:
                    notify("Nathy — VPS", f"{filepath.name} enviado al servidor")
                else:
                    logger.warning(f"VPS error: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Error enviando a VPS: {e}")


def run_forever(cfg: dict, dirs: dict[str, Path]):
    handler = NathyInboxHandler(cfg, dirs)
    observer = Observer()
    observer.schedule(handler, str(dirs["Inbox"]), recursive=False)
    observer.start()
    logger.info(f"👀 Observando: {dirs['Inbox']}")
    logger.info("Nathy Edge Client activo")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Nathy Edge Client — Windows")
    parser.add_argument("--config", default=os.path.join(
        os.environ.get("NATHY_ROOT", r"C:\NathyConta"),
        "Config", "config.yaml"
    ), help="Ruta a config.yaml")
    parser.add_argument("--scan", help="Escanea y organiza una carpeta (one-shot)")
    args = parser.parse_args()

    cfg = load_config(args.config)

    log_cfg = cfg["logging"]
    logging.basicConfig(
        level=getattr(logging, log_cfg["level"].upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_cfg["file"], encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    dirs = setup_directories(cfg["paths"]["root"])

    if args.scan:
        scan_dir = Path(args.scan)
        logger.info(f"Escaneando: {scan_dir}")
        count = {"organizado": 0, "duplicado": 0, "pendiente": 0}
        for f in scan_dir.iterdir():
            if f.is_file():
                result = organize_file(f, dirs)
                count[result["status"]] = count.get(result["status"], 0) + 1
        logger.info(f"Resultado: {count}")
        return

    notify("Nathy Edge", "Cliente iniciado")
    run_forever(cfg, dirs)


if __name__ == "__main__":
    main()
