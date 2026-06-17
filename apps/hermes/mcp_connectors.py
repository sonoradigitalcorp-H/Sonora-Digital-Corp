#!/usr/bin/env python3
"""
Conectores MCP para Hugging Face y GitHub.
Se comunican a través del protocolo MCP (Model Context Protocol) para que
los agentes puedan interactuar con modelos y repositorios.
"""
import json, os, subprocess, logging

log = logging.getLogger("jarvis.mcp")

HF_API_KEY = os.getenv("HF_API_KEY", "")
GH_TOKEN = os.getenv("GH_TOKEN", "")

MCP_DIR = os.path.expanduser("~/.config/opencode/mcp")

# ---------- Hugging Face MCP ----------
def hf_infer(model="gpt2", prompt="Hello", max_tokens=100):
    """Consulta modelos de Hugging Face Inference API."""
    if not HF_API_KEY:
        return {"error": "HF_API_KEY no configurada"}
    import requests
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}
    resp = requests.post(f"https://api-inference.huggingface.co/models/{model}",
                          headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()
    return {"error": resp.text}

def hf_mcp_server(port=8081):
    """Inicia un servidor MCP local para Hugging Face (proceso hijo)."""
    script = '''#!/usr/bin/env python3
import sys, json, http.server, requests
from urllib.parse import urlparse, parse_qs

class HFHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = json.loads(self.rfile.read(length))
        model = body.get("model", "gpt2")
        prompt = body.get("prompt", "")
        headers = {"Authorization": f"Bearer {os.environ.get('HF_API_KEY','')}"}
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{model}",
            headers=headers, json={"inputs": prompt}
        )
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(resp.json()).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"hf_mcp_running"}')

    def log_message(self, *a): pass

if __name__ == "__main__":
    http.server.HTTPServer(("0.0.0.0", PORT), HFHandler).serve_forever()
'''.replace("PORT", str(port))
    subprocess.Popen(["python3", "-c", script],
                     env={**os.environ, "HF_API_KEY": HF_API_KEY},
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"http://localhost:{port}"

# ---------- GitHub MCP ----------
def gh_list_repos(username="", pages=1):
    """Lista repositorios públicos de un usuario/organización."""
    import requests
    headers = {}
    if GH_TOKEN:
        headers["Authorization"] = f"Bearer {GH_TOKEN}"
    url = f"https://api.github.com/users/{username or 'octocat'}/repos?per_page=30&page={pages}"
    resp = requests.get(url, headers=headers)
    return resp.json() if resp.status_code == 200 else {"error": resp.text}

def gh_mcp_server(port=8082):
    """Inicia un servidor MCP local para GitHub (proceso hijo)."""
    script = '''#!/usr/bin/env python3
import sys, json, http.server, requests, os, subprocess

GH_BIN = "/usr/bin/gh"

class GHHandler(http.server.BaseHTTPRequestHandler):
    def _gh(self, args):
        try:
            r = subprocess.run([GH_BIN] + args, capture_output=True, text=True, timeout=30)
            return {"stdout": r.stdout.strip(), "stderr": r.stderr.strip(), "returncode": r.returncode}
        except Exception as e:
            return {"error": str(e)}

    def _gh_json(self, args):
        r = self._gh(args + ["--json", "number,title,state,headRefName,baseRefName,createdAt,url"])
        if r.get("returncode") != 0:
            return {"error": r.get("stderr", "gh command failed")}
        return json.loads(r["stdout"]) if r["stdout"] else {}

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))
        action = body.get("action", "repos")
        token = os.environ.get("GH_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        repo = body.get("repo", "")
        result = {}

        if action == "repos":
            user = body.get("user", "octocat")
            url = f"https://api.github.com/users/{user}/repos?per_page=30"
            resp = requests.get(url, headers=headers)
            result = resp.json() if resp.status_code == 200 else {"error": resp.text}

        elif action == "issues":
            url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=20"
            resp = requests.get(url, headers=headers)
            result = resp.json() if resp.status_code == 200 else {"error": resp.text}

        elif action == "list_prs":
            result = self._gh_json(["pr", "list", "--repo", repo, "--limit", "20"])

        elif action == "view_pr":
            number = str(body.get("number", ""))
            raw = self._gh(["pr", "view", number, "--repo", repo, "--json",
                            "number,title,state,body,headRefName,baseRefName,author,additions,deletions,files,url"])
            if raw.get("returncode") == 0 and raw.get("stdout"):
                try:
                    result = json.loads(raw["stdout"])
                except json.JSONDecodeError:
                    result = {"error": "Failed to parse PR data"}
            else:
                result = {"error": raw.get("stderr", "Failed to view PR")}

        elif action == "create_pr":
            title = body.get("title", "")
            pr_body = body.get("body", "")
            head = body.get("head", "")
            base = body.get("base", "main")
            raw = self._gh(["pr", "create", "--repo", repo, "--title", title,
                            "--body", pr_body, "--base", base, "--head", head])
            if raw.get("returncode") == 0:
                url = raw.get("stdout", "").strip()
                pr_num = url.rstrip("/").split("/")[-1] if url else ""
                result = {"url": url, "number": pr_num, "title": title}
            else:
                result = {"error": raw.get("stderr", "Failed to create PR")}

        elif action == "merge_pr":
            number = str(body.get("number", ""))
            strategy = body.get("strategy", "merge")
            raw = self._gh(["pr", "merge", number, "--repo", repo, f"--{strategy}"])
            result = {"stdout": raw.get("stdout", ""), "stderr": raw.get("stderr", ""),
                      "success": raw.get("returncode") == 0}

        elif action == "checkout_pr":
            number = str(body.get("number", ""))
            raw = self._gh(["pr", "checkout", number, "--repo", repo])
            result = {"stdout": raw.get("stdout", ""), "success": raw.get("returncode") == 0}

        else:
            result = {"error": f"Unknown action: {action}"}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"gh_mcp_running"}')

    def log_message(self, *a): pass

if __name__ == "__main__":
    http.server.HTTPServer(("0.0.0.0", PORT), GHHandler).serve_forever()
'''.replace("PORT", str(port))
    subprocess.Popen(["python3", "-c", script],
                     env={**os.environ, "GH_TOKEN": GH_TOKEN},
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"http://localhost:{port}"

# ---------- Auto‑start MCP servers ----------
def start_all_mcp():
    """Arranca los servidores MCP HF y GH si hay credenciales."""
    for fn, port, key, name in [
        (hf_mcp_server, 8081, "HF_API_KEY", "HuggingFace"),
        (gh_mcp_server, 8082, "GH_TOKEN", "GitHub"),
    ]:
        if os.environ.get(key):
            url = fn(port=port)
            log.info(f"MCP {name} → {url}")
        else:
            log.warning(f"MCP {name} saltado ({key} no definida)")

if __name__ == "__main__":
    start_all_mcp()
