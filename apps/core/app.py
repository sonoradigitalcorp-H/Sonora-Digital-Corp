import asyncio
import hashlib
import json
import secrets
import subprocess
import time
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parent.parent
AUTH_FILE = ROOT / "state" / "auth_tokens.json"
AUTH_TOKENS: dict[str, dict] = {}

if AUTH_FILE.exists():
    try:
        AUTH_TOKENS.update(json.loads(AUTH_FILE.read_text()))
    except Exception:
        pass

app = FastAPI(title="Sonora Platform Kernel", version="1.0.0")
active_connections: list[WebSocket] = []


async def broadcast(data: dict):
    for ws in active_connections.copy():
        try:
            await ws.send_json(data)
        except Exception:
            active_connections.remove(ws)


@app.post("/auth/login")
async def auth_login(request: Request):
    body = await request.json()
    email = (body.get("email") or "").strip().lower()
    if not email or "@" not in email:
        return JSONResponse(content={"error": "Email inválido"}, status_code=400)

    token = secrets.token_urlsafe(32)
    AUTH_TOKENS[token] = {"email": email, "created": time.time()}

    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w") as f:
        json.dump(AUTH_TOKENS, f)

    sid = hashlib.sha256(token.encode()).hexdigest()[:12]
    return JSONResponse(content={"token": token, "email": email, "sid": sid})


@app.get("/auth/me")
async def auth_me(request: Request):
    token = request.headers.get("authorization", "").replace("Bearer ", "")
    session = AUTH_TOKENS.get(token)
    if not session:
        return JSONResponse(content={"error": "no session"}, status_code=401)
    return JSONResponse(content={"email": session["email"], "sid": hashlib.sha256(token.encode()).hexdigest()[:12]})


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok", "time": time.time()})


async def ask_ollama(prompt: str) -> str:
    try:
        result = subprocess.run(
            ["ollama", "run", "tinyllama:1.1b", prompt],
            capture_output=True, text=True, timeout=60,
        )
        return result.stdout.strip() or result.stderr.strip() or "Sin respuesta"
    except Exception as e:
        return f"Error: {e}"


@app.websocket("/kernel/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    active_connections.append(ws)

    await ws.send_json({"type": "connected"})

    try:
        while True:
            data = await ws.receive_text()
            raw = json.loads(data)
            input_text = raw.get("input", "")

            if not input_text:
                continue

            response = await ask_ollama(input_text)

            await ws.send_json({
                "type": "result",
                "text": response,
                "agent": "qwen2.5:1.5b",
                "status": "success",
                "duration_ms": 0,
            })
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "text": str(e)[:200]})
        except Exception:
            pass
    finally:
        if ws in active_connections:
            active_connections.remove(ws)


@app.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    body = await request.json()
    message_data = body.get("message", body)
    text = message_data.get("text", message_data.get("body", ""))
    sender = message_data.get("from", message_data.get("sender", ""))
    chat_id = message_data.get("chat", message_data.get("jid", sender))

    log_path = ROOT / "state" / "whatsapp" / "incoming.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps({"t": time.time(), "from": sender, "text": text}) + "\n")

    faq = {
        "hola": "¡Hola! Soy el asistente de Sonora Digital. Para atención completa, visita nuestra plataforma: https://sonoradigitalcorp.com/platform",
        "horarios": "Nuestros agentes IA están disponibles 24/7 en nuestra plataforma: https://sonoradigitalcorp.com/platform",
        "precios": "Conoce nuestros planes y precios en: https://sonoradigitalcorp.com/platform",
        "contacto": "Puedes contactarnos directamente en nuestra plataforma: https://sonoradigitalcorp.com/platform",
        "gracias": "¡De nada! Para cualquier consulta, estamos en: https://sonoradigitalcorp.com/platform",
    }

    text_lower = text.lower().strip()
    response = None
    for keyword, reply in faq.items():
        if keyword in text_lower:
            response = reply
            break

    if not response:
        response = (
            "Hola, gracias por contactarnos. 🙌\n\n"
            "Para brindarte la mejor atención, por favor continúa en nuestra plataforma:\n"
            "👉 https://sonoradigitalcorp.com/platform\n\n"
            "Ahí podrás chatear con nuestro asistente IA, consultar tu historial y más."
        )

    try:
        subprocess.run(
            ["wacli", "send", "text", "--to", chat_id, "--message", response],
            capture_output=True, text=True, timeout=30,
        )
    except Exception as e:
        print(f"[whatsapp] send error: {e}")

    return JSONResponse(content={"status": "ok", "response": response[:50]})
