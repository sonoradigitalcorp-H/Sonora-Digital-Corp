"""Status API — HTTP endpoint /api/v1/status [FR8]"""
import json
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from . import drift_scanner, health_checker

REPO = Path(__file__).resolve().parent.parent.parent.parent
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
            elif self.path == "/api/v1/events/recent":
                self._handle_events_recent()
            elif self.path == "/api/v1/cost/summary":
                self._handle_cost_summary()
            elif self.path == "/api/v1/execution/stats":
                self._handle_exec_stats()
            elif self.path == "/api/v1/execution/tasks":
                self._handle_exec_tasks()
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

    def do_POST(self):
        try:
            if self.path == "/api/v1/execution/submit":
                self._handle_exec_submit()
            elif self.path.startswith("/api/v1/execution/cancel/"):
                self._handle_exec_cancel()
            elif self.path.startswith("/api/v1/execution/retry/"):
                self._handle_exec_retry()
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
            from apps.measure.scoreboard import compute_scoreboard
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

    def _handle_events_recent(self):
        try:
            import re
            events_file = REPO / "state" / "events" / "events.jsonl"
            events = []
            if events_file.exists():
                with open(events_file) as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            events.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
            limit = 20
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            if "limit" in qs:
                limit = int(qs["limit"][0])
            body = json.dumps({"events": events[:limit], "count": len(events[:limit])}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e), "events": []}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_cost_summary(self):
        try:
            eco_db = REPO / "state" / "economics.db"
            if eco_db.exists():
                import sqlite3
                conn = sqlite3.connect(str(eco_db))
                rows = conn.execute(
                    "SELECT agent, SUM(tokens_input + tokens_output), SUM(cost_usd), COUNT(*) "
                    "FROM operations GROUP BY agent ORDER BY SUM(cost_usd) DESC"
                ).fetchall()
                conn.close()
                totals = {}
                grand_cost = 0
                grand_tokens = 0
                for r in rows:
                    totals[r[0]] = {"tokens": r[1], "cost": round(r[2], 4), "ops": r[3]}
                    grand_cost += r[2]
                    grand_tokens += r[1]
                body = json.dumps({
                    "totals": totals,
                    "grand_total": {"tokens": grand_tokens, "cost": round(grand_cost, 4)}
                }).encode()
            else:
                body = json.dumps({"totals": {}, "grand_total": {"tokens": 0, "cost": 0}}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e), "totals": {}}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_exec_stats(self):
        try:
            sys.path.insert(0, str(REPO))
            from apps.decide.execution.queue import TaskQueue
            q = TaskQueue()
            body = json.dumps(q.stats()).encode()
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_exec_tasks(self):
        try:
            sys.path.insert(0, str(REPO))
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            status = qs.get("status", [None])[0]
            agent = qs.get("agent", [None])[0]
            limit = int(qs.get("limit", ["20"])[0])
            from apps.decide.execution.queue import TaskQueue
            q = TaskQueue()
            tasks = q.list_tasks(status=status, agent=agent, limit=limit)
            import json as j
            body = j.dumps({"tasks": tasks, "count": len(tasks)}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_exec_submit(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length) if content_length else b"{}"
            data = json.loads(post_data)
            sys.path.insert(0, str(REPO))
            from apps.decide.execution.queue import TaskQueue
            q = TaskQueue()
            result = q.submit(
                agent=data["agent"],
                operation=data["operation"],
                params=data.get("params", {}),
                priority=data.get("priority", 0),
                max_retries=data.get("max_retries", 3),
                spec_id=data.get("spec_id"),
            )
            body = json.dumps(result).encode()
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_exec_cancel(self):
        try:
            task_id = self.path.split("/")[-1]
            sys.path.insert(0, str(REPO))
            from apps.decide.execution.queue import TaskQueue
            q = TaskQueue()
            q.cancel(task_id)
            body = json.dumps({"status": "cancelled", "id": task_id}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def _handle_exec_retry(self):
        try:
            task_id = self.path.split("/")[-1]
            sys.path.insert(0, str(REPO))
            from apps.decide.execution.queue import TaskQueue
            q = TaskQueue()
            task = q.status(task_id)
            if not task:
                body = json.dumps({"error": "task not found"}).encode()
            elif task["status"] not in ("failed", "cancelled"):
                body = json.dumps({"error": f"task is {task['status']}, not retryable"}).encode()
            else:
                q.fail(task_id, "manual retry via API", retry=True)
                body = json.dumps({"status": "retry_submitted", "id": task_id}).encode()
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

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
