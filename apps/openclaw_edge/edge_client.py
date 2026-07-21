"""
OpenClaw Edge Client — Windows (Nathaly / Fourgea México)

Observa C:\\OpenClaw\\Inbox, envía archivos al VPS vía HTTPS,
recibe resultados y muestra notificaciones Windows.

NUNCA toca nada fuera de C:\\OpenClaw\\.

Uso:
    python edge_client.py --config config.yaml
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger("openclaw.edge")

PROCESSED_FILES: set[str] = set()

SUB_DIRS = ["Inbox", "Procesados", "Pendientes", "Errores", "Exportaciones", "Logs"]

DEFAULT_CONFIG = {
    "vps": {"url": "https://vps.sonoradigitalcorp.com", "api_key": ""},
    "device": {"id": "nathaly-laptop", "name": "Laptop Nathaly — Fourgea"},
    "paths": {"root": "C:\\OpenClaw", "watch_delay": 2.0},
    "allowed_extensions": [".xml", ".pdf", ".XML", ".PDF"],
    "max_file_size_mb": 20,
    "logging": {"level": "INFO", "file": "C:\\OpenClaw\\Logs\\edge.log"},
}


def load_config(path: str) -> dict:
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            user_cfg = yaml.safe_load(fh) or {}
        _deep_merge(cfg, user_cfg)
    return cfg


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v


def setup_directories(root: str) -> dict[str, Path]:
    dirs: dict[str, Path] = {}
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
        from win10toast import ToastNotifier  # type: ignore
        toaster = ToastNotifier()
        toaster.show_toast(title, message, duration=5, threaded=True)
    except Exception:
        logger.info(f"[NOTIF] {title}: {message}")


class InboxHandler(FileSystemEventHandler):
    def __init__(self, cfg: dict, dirs: dict[str, Path]):
        self.cfg = cfg
        self.dirs = dirs
        self.client = httpx.Client(
            base_url=cfg["vps"]["url"].rstrip("/"),
            headers={
                "Authorization": f"Bearer {cfg['vps']['api_key']}",
                "X-Device-ID": cfg["device"]["id"],
            },
            timeout=60.0,
            verify=True,
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

        logger.info(f"Nuevo archivo detectado: {filepath.name}")
        time.sleep(1.0)

        try:
            fsize_mb = filepath.stat().st_size / (1024 * 1024)
            if fsize_mb > self.cfg["max_file_size_mb"]:
                self._move_error(filepath, f"Excede tamaño máximo ({fsize_mb:.1f}MB > {self.cfg['max_file_size_mb']}MB)")
                return

            result = self._upload(filepath)
            self._handle_result(filepath, result)

        except Exception as exc:
            logger.exception(f"Error procesando {filepath.name}")
            self._move_error(filepath, str(exc))
            notify("OpenClaw Edge — Error", f"{filepath.name}: {exc}")

    def _upload(self, filepath: Path) -> dict:
        with open(filepath, "rb") as fh:
            files = {"file": (filepath.name, fh, "application/octet-stream")}
            resp = self.client.post("/edge/inbox", files=files)
            resp.raise_for_status()
            return resp.json()

    def _handle_result(self, filepath: Path, result: dict):
        if result.get("success"):
            r = result.get("result", {})
            msg = (
                f"{r.get('tipo', 'OK').upper()} | "
                f"RFC: {r.get('rfc_emisor', '?')} | "
                f"Total: ${r.get('total', 0):,.2f}"
            )
            notify("OpenClaw Edge — Procesado", f"{filepath.name}\n{msg}")
            self._move_to(filepath, self.dirs["Procesados"])
        else:
            err = result.get("error", "Error desconocido")
            notify("OpenClaw Edge — Error", f"{filepath.name}\n{err}")
            self._move_error(filepath, err)

    def _move_error(self, filepath: Path, reason: str):
        dest = self.dirs["Errores"] / filepath.name
        _safe_rename(filepath, dest)
        _write_error_log(self.dirs["Errores"], filepath.name, reason)

    def _move_to(self, filepath: Path, dest_dir: Path):
        dest = dest_dir / filepath.name
        _safe_rename(filepath, dest)
        logger.info(f"Movido → {dest}")


def _safe_rename(src: Path, dest: Path):
    if dest.exists():
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        dest = dest.with_stem(f"{dest.stem}_{ts}")
    os.rename(str(src), str(dest))


def _write_error_log(errors_dir: Path, filename: str, reason: str):
    log_entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "file": filename,
        "error": reason,
    }
    log_path = errors_dir / "error_log.jsonl"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def run_forever(cfg: dict, dirs: dict[str, Path]):
    handler = InboxHandler(cfg, dirs)
    observer = Observer()
    observer.schedule(handler, str(dirs["Inbox"]), recursive=False)
    observer.start()
    logger.info(f"Observando: {dirs['Inbox']}")
    logger.info("OpenClaw Edge activo. Ctrl+C para detener.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="OpenClaw Edge Client")
    parser.add_argument("--config", default="config.yaml", help="Ruta a config.yaml")
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

    if not cfg["vps"]["api_key"]:
        logger.error("API key no configurada. Edita config.yaml")
        sys.exit(1)

    dirs = setup_directories(cfg["paths"]["root"])
    notify("OpenClaw Edge", "Cliente iniciado — observando Inbox")
    run_forever(cfg, dirs)


if __name__ == "__main__":
    main()
