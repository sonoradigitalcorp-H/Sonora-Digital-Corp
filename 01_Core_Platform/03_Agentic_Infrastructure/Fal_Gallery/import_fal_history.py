#!/usr/bin/env python3
"""import_fal_history.py — Importador Histórico de Contenido fal.ai

Rombra en logs de sesiones, historial de terminales, scripts y archivos del sistema
para encontrar cualquier URL de fal.media o registro previo de fal.ai, descargarlo
e indexarlo en la base de datos fal_media.db.
"""

import os
import re
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"
DB_PATH = BASE_DIR / "fal_media.db"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)

# Expresiones regulares para detectar URLs de fal.media y fal.run
FAL_MEDIA_RE = re.compile(r'https?://[a-zA-Z0-9\.\-]*fal\.media/files/[a-zA-Z0-9\.\-_/]+\.(png|jpg|jpeg|webp|mp4|mov|mp3|wav|ogg)')
FAL_MEDIA_ANY_RE = re.compile(r'https?://[a-zA-Z0-9\.\-]*fal\.media/files/[a-zA-Z0-9\.\-_/]+')


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fal_creations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT UNIQUE,
            prompt TEXT,
            model TEXT,
            media_type TEXT,
            original_url TEXT,
            local_filename TEXT,
            seed INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata_json TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_imported(request_id, prompt, model, media_type, original_url, local_filename, created_at=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        if created_at:
            cursor.execute("""
                INSERT INTO fal_creations (request_id, prompt, model, media_type, original_url, local_filename, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'COMPLETED', ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    prompt=COALESCE(EXCLUDED.prompt, fal_creations.prompt),
                    local_filename=COALESCE(EXCLUDED.local_filename, fal_creations.local_filename)
            """, (request_id, prompt, model, media_type, original_url, local_filename, created_at))
        else:
            cursor.execute("""
                INSERT INTO fal_creations (request_id, prompt, model, media_type, original_url, local_filename, status)
                VALUES (?, ?, ?, ?, ?, ?, 'COMPLETED')
                ON CONFLICT(request_id) DO UPDATE SET
                    prompt=COALESCE(EXCLUDED.prompt, fal_creations.prompt),
                    local_filename=COALESCE(EXCLUDED.local_filename, fal_creations.local_filename)
            """, (request_id, prompt, model, media_type, original_url, local_filename))
        conn.commit()
        print(f"  [Importado] {request_id} -> {local_filename}")
    except Exception as e:
        print(f"  ⚠ Error al importar en DB: {e}")
    finally:
        conn.close()


def download_media(url: str, request_id: str) -> str:
    parsed_path = urllib.parse.urlparse(url).path
    ext = Path(parsed_path).suffix or ".png"
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mp3", ".wav", ".ogg"]:
        ext = ".png"
        
    filename = f"{request_id}{ext}"
    dest_path = MEDIA_DIR / filename
    
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return filename
        
    try:
        print(f"  ⬇ Descargando histórico: {url[:70]}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SonoraDigitalCorp/1.0)"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        return filename
    except Exception as e:
        print(f"  ⚠ No disponible en CDN (expirado o inaccesible): {e}")
        return ""


def scan_file_for_fal_links(file_path: Path):
    try:
        content = file_path.read_text(errors="ignore")
    except Exception:
        return 0

    urls = FAL_MEDIA_ANY_RE.findall(content)
    if not urls:
        return 0

    count = 0
    for idx, url in enumerate(set(urls)):
        req_id = f"hist_{file_path.stem}_{idx}"
        
        # Intentar extraer el tipo
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        m_type = "image"
        if ext in [".mp4", ".mov"]: m_type = "video"
        elif ext in [".mp3", ".wav", ".ogg"]: m_type = "audio"
        
        local_file = download_media(url, req_id)
        
        # Intentar asociar con contexto/prompt cercano
        prompt = f"Generado en {file_path.name}"
        model = "fal-ai/flux"
        
        save_imported(
            request_id=req_id,
            prompt=prompt,
            model=model,
            media_type=m_type,
            original_url=url,
            local_filename=local_file or "expirado.png"
        )
        count += 1

    return count


def scan_workspace():
    print("🔍 Escaneando historial del sistema en busca de contenidos fal.ai...")
    
    paths_to_scan = [
        Path.home() / ".hermes" / "sessions",
        Path.home() / ".hermes" / "logs",
        Path.home() / ".hermes" / "agents",
        Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo/00_Administration/Session_Logs"),
        Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects"),
        Path("/home/mystic/Documentos/Sonora Digital Corp Nuevo/01_Core_Platform"),
    ]
    
    total_found = 0
    for base in paths_to_scan:
        if not base.exists():
            continue
        print(f" 📂 Escaneando {base}...")
        for p in base.rglob("*"):
            if p.is_file() and p.suffix in [".json", ".jsonl", ".log", ".txt", ".md", ".py", ".sh"]:
                found = scan_file_for_fal_links(p)
                total_found += found

    print(f"\n✅ Importación histórica completada. Total de ítems procesados: {total_found}")


if __name__ == "__main__":
    init_db()
    scan_workspace()
