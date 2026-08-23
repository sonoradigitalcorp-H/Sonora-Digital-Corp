#!/usr/bin/env python3
"""fal_webhook_receiver.py — Receptor de Webhooks, Almacenador y Servidor para fal.ai

Funcionalidad:
1. Recibe peticiones HTTP POST (Webhooks o Log Drains) enviadas por fal.ai.
2. Extrae metadatos (request_id, prompt, modelo, semilla, URLs de imágenes/video/audio).
3. Descarga de forma automática los archivos multimedia a la carpeta local/VPS media/.
4. Mantiene el índice histórico en SQLite (fal_media.db).
5. Sirve una API REST (/api/gallery) y la Galería Web interactiva.

Uso:
  python3 fal_webhook_receiver.py --port 8645
"""

import os
import sys
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"
DB_PATH = BASE_DIR / "fal_media.db"
HTML_PATH = BASE_DIR / "fal_gallery.html"

MEDIA_DIR.mkdir(parents=True, exist_ok=True)


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


def save_creation(request_id, prompt, model, media_type, original_url, local_filename, seed=None, status="COMPLETED", metadata=None):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    meta_str = json.dumps(metadata or {}, ensure_ascii=False)
    
    try:
        cursor.execute("""
            INSERT INTO fal_creations (request_id, prompt, model, media_type, original_url, local_filename, seed, status, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(request_id) DO UPDATE SET
                prompt=COALESCE(EXCLUDED.prompt, fal_creations.prompt),
                original_url=COALESCE(EXCLUDED.original_url, fal_creations.original_url),
                local_filename=COALESCE(EXCLUDED.local_filename, fal_creations.local_filename),
                status=EXCLUDED.status,
                metadata_json=EXCLUDED.metadata_json
        """, (request_id, prompt, model, media_type, original_url, local_filename, seed, status, meta_str))
        conn.commit()
        print(f"  ✓ Guardado en DB: [{request_id}] {media_type} - {prompt[:40] if prompt else 'sin prompt'}")
    except Exception as e:
        print(f"  ✗ Error guardando en DB: {e}")
    finally:
        conn.close()


def download_media(url: str, request_id: str, index: int = 0) -> str:
    """Descarga el archivo desde el CDN de fal.ai y devuelve el nombre local."""
    if not url:
        return ""
    
    # Determinar extensión
    parsed_path = urllib.parse.urlparse(url).path
    ext = Path(parsed_path).suffix or ".png"
    if ext not in [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov", ".mp3", ".wav", ".ogg"]:
        ext = ".png"
        
    filename = f"{request_id}_{index}{ext}"
    dest_path = MEDIA_DIR / filename
    
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return filename
        
    try:
        print(f"  ⬇ Descargando medio: {url[:70]}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (SonoraDigitalCorp/1.0)"})
        with urllib.request.urlopen(req, timeout=60) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        print(f"  ✓ Descargado: {filename} ({dest_path.stat().st_size} bytes)")
        return filename
    except Exception as e:
        print(f"  ⚠ Error descargando medio: {e}")
        return ""


def parse_and_process_payload(data: dict):
    """Procesa un payload de Webhook de fal.ai."""
    request_id = data.get("request_id") or data.get("id") or f"req_{int(datetime.now().timestamp())}"
    status = data.get("status", "COMPLETED")
    
    # Extraer payload principal
    payload = data.get("payload") or data.get("output") or data
    
    # Extraer prompt y modelo
    prompt = payload.get("prompt") or data.get("prompt") or data.get("input", {}).get("prompt") or "Sin prompt especificado"
    model = data.get("model") or data.get("endpoint") or payload.get("model") or "fal-ai/flux"
    seed = payload.get("seed") or data.get("input", {}).get("seed")
    
    # Rastrear URLs de medios
    media_items = []
    
    # 1. Lista de imágenes
    images = payload.get("images") or payload.get("image")
    if isinstance(images, list):
        for img in images:
            if isinstance(img, dict) and "url" in img:
                media_items.append(("image", img["url"]))
            elif isinstance(img, str):
                media_items.append(("image", img))
    elif isinstance(images, dict) and "url" in images:
        media_items.append(("image", images["url"]))
        
    # 2. Videos
    video = payload.get("video") or payload.get("videos")
    if isinstance(video, dict) and "url" in video:
        media_items.append(("video", video["url"]))
    elif isinstance(video, list):
        for v in video:
            if isinstance(v, dict) and "url" in v:
                media_items.append(("video", v["url"]))
            elif isinstance(v, str):
                media_items.append(("video", v))
                
    # 3. Audios
    audio = payload.get("audio") or payload.get("audios")
    if isinstance(audio, dict) and "url" in audio:
        media_items.append(("audio", audio["url"]))
        
    # 4. Fallback directo url
    if not media_items and "url" in payload:
        media_items.append(("image", payload["url"]))
        
    for idx, (m_type, url) in enumerate(media_items):
        item_req_id = f"{request_id}_{idx}" if idx > 0 else request_id
        local_file = download_media(url, item_req_id, idx)
        save_creation(
            request_id=item_req_id,
            prompt=prompt,
            model=model,
            media_type=m_type,
            original_url=url,
            local_filename=local_file,
            seed=seed,
            status=status,
            metadata=data
        )


class FalWebhookHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_file(self, file_path, content_type):
        if not file_path.exists():
            self.send_error(404, "File Not Found")
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(file_path.stat().st_size))
        self.end_headers()
        with open(file_path, "rb") as f:
            self.wfile.write(f.read())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html", "/gallery"]:
            self._send_file(HTML_PATH, "text/html; charset=utf-8")
            return

        if path.startswith("/media/"):
            filename = path.replace("/media/", "")
            file_path = MEDIA_DIR / filename
            ext = file_path.suffix.lower()
            ct = "image/png"
            if ext in [".jpg", ".jpeg"]: ct = "image/jpeg"
            elif ext == ".webp": ct = "image/webp"
            elif ext in [".mp4", ".mov"]: ct = "video/mp4"
            elif ext in [".mp3", ".wav", ".ogg"]: ct = "audio/mpeg"
            self._send_file(file_path, ct)
            return

        if path == "/api/gallery":
            params = urllib.parse.parse_qs(parsed.query)
            q = params.get("q", [""])[0].lower()
            m_type = params.get("type", [""])[0]

            init_db()
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM fal_creations WHERE 1=1"
            sql_params = []

            if q:
                query += " AND (LOWER(prompt) LIKE ? OR LOWER(model) LIKE ? OR LOWER(request_id) LIKE ?)"
                sql_params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])

            if m_type:
                query += " AND media_type = ?"
                sql_params.append(m_type)

            query += " ORDER BY created_at DESC"
            cursor.execute(query, sql_params)
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()

            self._send_json({"count": len(rows), "data": rows})
            return

        self.send_error(404, "Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        try:
            data = json.loads(body)
            print(f"📥 Webhook fal.ai recibido: {self.path}")
            parse_and_process_payload(data)
            self._send_json({"status": "ok", "message": "Payload procesado exitosamente"})
        except Exception as e:
            print(f"⚠ Error procesando POST webhook: {e}")
            self._send_json({"status": "error", "message": str(e)}, status=400)


def main():
    parser = argparse.ArgumentParser(description="Servidor Webhook y Galería fal.ai")
    parser.add_argument("--port", type=int, default=8645, help="Puerto HTTP (default: 8645)")
    parser.add_argument("--host", default="0.0.0.0", help="Host de escucha")
    args = parser.parse_args()

    init_db()
    server = HTTPServer((args.host, args.port), FalWebhookHandler)
    print(f"🚀 Servidor Galería & Webhook fal.ai activo en http://{args.host}:{args.port}")
    print(f"📁 Galería Web: http://localhost:{args.port}/")
    print(f"🔗 API Galería: http://localhost:{args.port}/api/gallery")
    print(f"📥 Endpoint Webhook: http://localhost:{args.port}/webhook")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    main()
