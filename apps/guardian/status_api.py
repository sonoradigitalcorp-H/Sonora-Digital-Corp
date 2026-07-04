"""Status API — HTTP endpoint /api/v1/status [FR8]"""
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from . import drift_scanner, health_checker

STATIC_DIR = Path(__file__).resolve().parent / "static"


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path == "/api/v1/status":
                self._handle_status()
            elif self.path == "/api/v1/health":
                self._handle_health()
            elif self.path == "/api/v1/drift":
                self._handle_drift()
            elif self.path == "/api/v1/scoreboard":
                self._handle_scoreboard()
            elif self.path == "/scoreboard":
                self._serve_static("scoreboard.html")
            elif self.path == "/control":
                self._serve_static("control.html")
            else:
                static_file = STATIC_DIR / self.path.lstrip("/")
                if static_file.exists() and static_file.is_file():
                    self._serve_static(self.path.lstrip("/"))
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error":"not found"}')
        except Exception:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": traceback.format_exc()}).encode())

    def _handle_status(self):
        try:
            drifts = drift_scanner.scan()
        except Exception as e:
            drifts = [{"type": "error", "detail": str(e)}]
        try:
            health = health_checker.check_all()
        except Exception as e:
            health = [{"status": "error", "error": str(e)}]
        body = json.dumps({
            "service": "truth-guardian",
            "version": "1.0.0",
            "drifts": drifts,
            "drift_count": len(drifts),
            "health": health,
            "healthy_count": sum(1 for h in health if h["status"] == "healthy"),
            "total_services": len(health),
            "status": "healthy" if len(drifts) == 0 else "drift_detected",
        }).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_health(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"healthy"}')

    def _handle_drift(self):
        try:
            drifts = drift_scanner.scan()
        except Exception as e:
            drifts = [{"type": "error", "detail": str(e)}]
        body = json.dumps({"drifts": drifts, "count": len(drifts)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_scoreboard(self):
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
            from apps.agent_metrics.scoreboard import compute_scoreboard
            sb = compute_scoreboard()
            body = json.dumps({"scoreboard": sb, "count": len(sb)}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e), "scoreboard": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _serve_static(self, filename):
        try:
            filepath = STATIC_DIR / filename
            if not filepath.exists() or not filepath.is_file():
                self.send_response(404)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"not found")
                return
            ext = filename.split(".")[-1]
            mime = {"html": "text/html", "css": "text/css", "js": "application/javascript", "png": "image/png", "svg": "image/svg+xml"}
            content_type = mime.get(ext, "text/plain")
            body = filepath.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(f"error: {e}".encode())

    def log_message(self, format, *args):
        pass


def start(port=8088, host="127.0.0.1"):
    server = HTTPServer((host, port), StatusHandler)
    print(f"[guardian] Status API on http://{host}:{port}/api/v1/status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    start()
