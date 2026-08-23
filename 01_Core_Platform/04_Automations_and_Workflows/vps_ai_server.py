#!/usr/bin/env python3
"""vps_ai_server.py — Servidor API 24/7 sonoradigitalcorp.com (SDD-0012 v2).

Endpoints:
  POST /api/v1/chat/completions   OpenAI-compatible. person ∈ {sdc,nathaly}.
                                  Inyecta SOUL server-side; limpia exclamaciones.
  GET  /api/tts                   proxy → tts_server :5293 (kokoro/edge)
  POST /api/stt                   proxy → stt_server :5292 (faster-whisper)
  GET  /health                    estado agregado llm+stt+tts

Reglas SOUL (duras): cero exclamaciones en respuestas, sin palabras técnicas,
vender beneficios. La limpieza es determinista (regex), no depende del LLM.
"""
import json
import os
import re
import time

from aiohttp import web, ClientSession, ClientTimeout

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_CHAIN = [
    "nvidia/nemotron-3-ultra-550b-a55b:free",  # rápido, gratis, mejor copy de venta (eval 83%)
    "deepseek/deepseek-v4-flash-0731",          # fallback pago
]
STT_URL = "http://127.0.0.1:5292/api/stt"
TTS_URL = "http://127.0.0.1:5293/api/tts"

SOULS = {
    "sdc": (
        "Eres el asistente de Sonora Digital Corp en Hermosillo, Sonora. Ayudas a dueños "
        "de negocio a recuperar tiempo: tu empresa queda atendiendo sola las 24 horas "
        "(mensajes, citas, clientes) mientras el dueño crece y no pierde ventas.\n"
        "REGLAS DURAS:\n"
        "1. Nunca uses signos de exclamación ni ¡ ni ! y nunca des respuestas con asteriscos ni markdown.\n"
        "2. Nunca digas IA, bot, modelo, inteligencia artificial, automatización. Di 'asistente' o 'te ayudo'.\n"
        "3. Vende beneficios concretos y AHORROS en tiempo/dinero: 'recuperas hasta 16 horas al mes', "
        "'dejas de pagar un sueldo de recepcionista', 'ningún cliente sin atender aunque sea de madrugada'.\n"
        "4. Máximo 4 frases cortas. Tono tranquilo, seguro, cercano. Español mexicano neutro.\n"
        "5. Precios jamás inventar: el diagnóstico inicial es gratis y los precios exactos los da Luis Daniel.\n"
        "6. MANEJO DE OBJECIONES (siempre desde beneficio):\n"
        "   - 'es caro' -> 'más barato que una recepcionista, y atiende 24 horas sin sueldo ni prestaciones'.\n"
        "   - 'me da miedo la tecnología' -> 'no tienes que saber nada técnico, yo me encargo de todo'.\n"
        "   - 'no tengo tiempo' -> 'es justo lo que te devuelve, horas cada semana'.\n"
        "   - 'es para empresas grandes' -> 'es para negocios como el tuyo, este es tu tamaño ideal'.\n"
        "7. SIEMPRE CIERRA CON CITA: propone agendar el diagnóstico. Sé concreto, sugiere 2 horarios de esta "
        "semana (ej 'te puedo agendar el martes a las 10 o el jueves a las 4'). Nunca cierres solo con 'te escribo por "
        "WhatsApp' o 'cuéntame más'. La conversación debe avanzar SIEMPRE hacia una fecha concreta.\n"
        "8. NUNCA repitas la misma pregunta ni el mismo escenario que ya planteaste en la respuesta anterior. "
        "Cada respuesta avanza.\n"
        "9. Si el usuario pide silencio (calla, silencio, basta, ya no hables): responde breve y detente.\n"
        "10. Si preguntan cómo funciona: 'es mi asistente personal trabajando para ti, sin que toques nada'."
    ),
    "nathaly": (
        "Eres la asistente de Nathaly Hermosillo, contadora en Hermosillo, Sonora "
        "(Hermosillo Contabilidad). Servicios: contabilidad mensual, administración y nómina, "
        "manifestación de importación, consultas y citas ante el SAT, marketing.\n"
        "REGLAS DURAS:\n"
        "1. Nunca uses signos de exclamación ni ¡ ni ! y nunca des respuestas con asteriscos ni markdown.\n"
        "2. Nunca digas IA, bot, modelo, inteligencia artificial. Di 'asistente de Nathaly'.\n"
        "3. Jamás inventes precios: 'la cotización exacta te la da Nathaly por WhatsApp'. El diagnóstico inicial es gratis.\n"
        "4. Vende AHOOROS y orden: 'cero multas del SAT', '8 horas al mes de vuelta', 'tus declaraciones en regla sin vueltas'.\n"
        "5. Máximo 4 frases cortas. Tono tranquilo, cercano, profesional. Zona horaria America/Hermosillo.\n"
        "6. MANEJO DE OBJECIONES (siempre desde beneficio):\n"
        "   - 'es caro' -> 'una multa del SAT sale más cara que llevar todo en orden'.\n"
        "   - 'no llevo mucho movimiento' -> 'justo por eso conviene tenerlo en regla desde ahora'.\n"
        "   - 'ya tengo contador' -> 'puedo revisar tu situación sin costo y te digo si te conviene cambiarte'.\n"
        "   - 'me da flojera' -> 'Nathaly se encarga de todo, tú solo firmas'.\n"
        "7. SIEMPRE CIERRA CON CITA: propone agendar la revisión/diagnóstico con Nathaly. Sé concreta, sugiere "
        "2 horarios de esta semana. Nunca cierres solo con 'te escribo'. La conversación debe avanzar SIEMPRE hacia "
        "una fecha concreta.\n"
        "8. NUNCA repitas la misma pregunta ni el mismo escenario de la respuesta anterior. Cada respuesta avanza.\n"
        "9. Si el usuario pide silencio (calla, silencio, basta): responde breve y detente.\n"
        "10. WhatsApp de Nathaly: 662 349 8589."
    ),
}

FORBIDDEN_RE = re.compile(
    r"\b(ia|agente|modelo|llm|token|prompt|rag|embedding|chatbot|bot|inteligencia artificial)\b", re.I)


def clean_reply(text: str) -> str:
    """Limpieza determinista SOUL: exclamaciones fuera, markdown suave, longitud voz."""
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.replace("!", ".").replace("¡", "")
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[.,]{2,}", ".", text)
    # voz: cortar a ~300 chars en frase completa (evita TTS eterno)
    if len(text) > 320:
        cut = text.rfind(". ", 0, 320)
        if cut != -1:
            text = text[:cut + 1]
        else:
            text = text[:300].rsplit(" ", 1)[0] + "."
    return text.strip()


def soft_replace_tech(text: str) -> str:
    """Reemplaza palabras técnicas que se colaran del LLM (defensa en profundidad)."""
    reps = [
        (r"\binteligencia artificial\b", "mi asistente"),
        (r"\bIA\b", "mi asistente"),
        (r"\bchatbot\b", "asistente"),
        (r"\bbot\b", "asistente"),
        (r"\bagente\b", "asistente"),
        (r"\bmodelo\b", "asistente"),
        (r"\bLLM\b", "asistente"),
    ]
    for pat, rep in reps:
        text = re.sub(pat, rep, text, flags=re.I if pat.startswith(r"\binteligencia") else 0)
    text = re.sub(r"(mi )?asistente(?: mi asistente)+", "mi asistente", text)
    text = re.sub(r"asistente asistente", "asistente", text)
    return text


async def handle_chat_completions(request: web.Request) -> web.Response:
    t0 = time.time()
    try:
        data = await request.json()
    except Exception:
        data = {}

    # Formato nuevo {messages[], person} o legado {text, sid}
    if not data.get("messages") and data.get("text"):
        data["messages"] = [{"role": "user", "content": str(data["text"])}]

    messages = list(data.get("messages", []))
    person = data.get("person")
    if not person:
        sys0 = ""
        if messages and messages[0].get("role") == "system":
            sys0 = str(messages[0].get("content", ""))
        last_user = next((str(m.get("content", "")) for m in reversed(messages)
                          if m.get("role") == "user"), "")
        person = "nathaly" if ("Nathaly" in sys0 or "Nathaly" in last_user
                               or "contabilidad" in last_user.lower()
                               or " sat" in last_user.lower()) else "sdc"

    # Inyectar SOUL si no viene system
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SOULS[person]})
    elif "REGLAS DURAS" not in messages[0].get("content", ""):
        messages[0]["content"] = SOULS[person]

    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sonoradigitalcorp.com",
        "X-Title": "Sonora Digital Corp",
    }
    if OPENROUTER_API_KEY:
        headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

    last_err = None
    for model in MODEL_CHAIN:
        payload = {"model": model, "messages": messages, "max_tokens": 220}
        try:
            timeout = ClientTimeout(total=22)
            async with ClientSession(timeout=timeout) as session:
                async with session.post("https://openrouter.ai/api/v1/chat/completions",
                                        headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        last_err = f"{model}: HTTP {resp.status}"
                        continue
                    res_json = await resp.json()
                    content = res_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if not content or not content.strip():
                        last_err = f"{model}: empty"
                        continue
                    # Limpieza SOUL determinista
                    content = clean_reply(content)
                    if FORBIDDEN_RE.search(content):
                        content = soft_replace_tech(content)
                    res_json["choices"][0]["message"]["content"] = content
                    res_json["model"] = model
                    print(f"[chat] {model} {round(time.time()-t0,2)}s person={person}", flush=True)
                    return web.json_response(res_json)
        except Exception as e:
            last_err = f"{model}: {e}"
            continue

    # Fallback offline: beneficio primero, sin exclamaciones
    reply = ("Te ayudo con gusto. Cuéntame de tu negocio y qué te está quitando tiempo, "
             "y te digo exactamente cómo lo resolveríamos. El diagnóstico inicial es gratis.")
    if person == "nathaly":
        reply = ("Con gusto te ayudo con tu contabilidad. Cuéntame qué necesitas: "
                 "declaraciones, citas SAT o llevar tus cuentas al día, y agendamos tu "
                 "diagnóstico gratis con Nathaly. También puedes escribirle directo al 662 349 8589.")
    return web.json_response({
        "choices": [{"message": {"role": "assistant", "content": reply}}],
        "model": "fallback-offline",
    })


async def handle_stt(request: web.Request) -> web.Response:
    """Proxy multipart → stt_server :5292."""
    try:
        timeout = ClientTimeout(total=45)
        async with ClientSession(timeout=timeout) as session:
            data = await request.read()
            ctype = request.headers.get("Content-Type", "application/octet-stream")
            async with session.post(STT_URL, data=data,
                                    headers={"Content-Type": ctype}) as resp:
                body = await resp.read()
                return web.Response(body=body, status=resp.status,
                                    content_type="application/json")
    except Exception as e:
        return web.json_response({"error": f"stt upstream: {e}"}, status=502)


async def handle_tts(request: web.Request) -> web.Response:
    """Proxy GET/POST query/body → tts_server :5293."""
    try:
        timeout = ClientTimeout(total=30)
        async with ClientSession(timeout=timeout) as session:
            if request.method == "POST":
                data = await request.read()
                url = TTS_URL
                headers = {"Content-Type": request.headers.get("Content-Type", "application/json")}
                async with session.post(url, data=data, headers=headers) as resp:
                    body = await resp.read()
                    ct = resp.headers.get("Content-Type", "audio/mpeg")
                    return web.Response(body=body, status=resp.status, content_type=ct,
                                        headers={"X-TTS-Engine": resp.headers.get("X-TTS-Engine", "?"),
                                                 "Cache-Control": "public,max-age=3600"})
            else:
                params = dict(request.query)
                async with session.get(TTS_URL, params=params) as resp:
                    body = await resp.read()
                    ct = resp.headers.get("Content-Type", "audio/mpeg")
                    return web.Response(body=body, status=resp.status, content_type=ct,
                                        headers={"X-TTS-Engine": resp.headers.get("X-TTS-Engine", "?"),
                                                 "Cache-Control": "public,max-age=3600"})
    except Exception as e:
        return web.json_response({"error": f"tts upstream: {e}"}, status=502)


async def handle_citas(request: web.Request) -> web.Response:
    """POST /api/v1/citas — agenda y manda audio de confirmación al teléfono (wacli).
    Body: {persona, nombre, negocio, telefono, fecha, hora}
    """
    import subprocess
    import tempfile
    from pathlib import Path

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "json inválido"}, status=400)

    persona = data.get("persona", "sdc")
    nombre = (data.get("nombre") or "para ti").strip()
    negocio = (data.get("negocio") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    fecha = (data.get("fecha") or "").strip()
    hora = (data.get("hora") or "").strip()

    if not (telefono and fecha and hora):
        return web.json_response({"error": "faltan telefono/fecha/hora"}, status=400)
    # validar teléfono MX: 10 dígitos o 521+10
    digits = re.sub(r"\D", "", telefono)
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]

    # → guardar cita (SQLite determinista, misma DB de leads del tenant)
    db_dir = Path("/opt/hermes/citas_db")
    db_dir.mkdir(parents=True, exist_ok=True)
    db_path = db_dir / f"citas_{persona}.db"
    import sqlite3, uuid, datetime
    cita_id = str(uuid.uuid4())
    now = datetime.datetime.now().isoformat()
    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS citas (
                id TEXT PRIMARY KEY, persona TEXT, nombre TEXT, negocio TEXT,
                telefono TEXT, fecha TEXT, hora TEXT, estado TEXT DEFAULT 'confirmada',
                creado_en TEXT)""")
            conn.execute("INSERT INTO citas VALUES (?,?,?,?,?,?,?,?,?)",
                         (cita_id, persona, nombre, negocio, digits, fecha, hora, "confirmada", now))
            conn.commit()
    except Exception as e:
        print(f"[citas] db error: {e}", flush=True)

    # → TTS confirmación (voz de la persona)
    msg = (f"Hola {nombre}. Tu cita queda confirmada para el {fecha} a las {hora}. "
           f"{'Te espero.' if persona=='sdc' else 'Te espera Nathaly.'} "
           f"Si necesitas cambiar el día, no dudes en escribir.")
    try:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            async with session.post(TTS_URL, json={"text": msg, "person": persona}) as resp:
                audio = await resp.read()
    except Exception as e:
        print(f"[citas] tts error: {e}", flush=True)
        audio = b""

    # → wacli send voice al teléfono (binario Go + store autenticado personal)
    wacli_status = "skipped-no-audio"
    if audio:
        tmp = tempfile.mktemp(suffix=".ogg")
        Path(tmp).write_bytes(audio)
        wacli_bin = os.environ.get("WACLI_BIN", "/home/mystic/.local/bin/wacli")
        wacli_store = os.environ.get("WACLI_STORE", "/home/mystic/.wacli")
        try:
            to = f"{digits}@s.whatsapp.net"
            r = subprocess.run(
                [wacli_bin, "send", "voice", "--store", wacli_store,
                 "--to", to, "--file", tmp],
                capture_output=True, text=True, timeout=40,
            )
            wacli_status = "sent" if r.returncode == 0 else f"err:{r.stderr[:120]}"
        except Exception as e:
            wacli_status = f"err:{e}"
        finally:
            try: Path(tmp).unlink()
            except Exception: pass

    print(f"[citas] {persona} {nombre} {fecha} {hora} wacli={wacli_status}", flush=True)
    return web.json_response({"ok": True, "cita_id": cita_id, "estado": "confirmada",
                              "wacli": wacli_status, "telefono": digits})


async def handle_health(request: web.Request) -> web.Response:
    services = {}
    async with ClientSession(timeout=ClientTimeout(total=3)) as session:
        for name, url in (("stt", "http://127.0.0.1:5292/health"),
                          ("tts", "http://127.0.0.1:5293/health")):
            try:
                async with session.get(url) as resp:
                    services[name] = "ok" if resp.status == 200 else f"http{resp.status}"
            except Exception:
                services[name] = "down"
        services["llm"] = "ok" if OPENROUTER_API_KEY else "no-key(fallback-local)"
    all_ok = all(v == "ok" or v.startswith("no-key") for v in services.values())
    return web.json_response({"status": "ok" if all_ok else "degraded",
                              "service": "Sonora Digital Corp AI Server",
                              "services": services})


app = web.Application(client_max_size=16 * 1024 * 1024)
app.router.add_get("/health", handle_health)
app.router.add_post("/api/v1/chat/completions", handle_chat_completions)
app.router.add_get("/api/v1/chat/completions", handle_chat_completions)
app.router.add_post("/v1/chat/completions", handle_chat_completions)
app.router.add_post("/chat", handle_chat_completions)          # compat páginas viejas
app.router.add_post("/api/stt", handle_stt)
app.router.add_get("/api/stt", handle_stt)
app.router.add_post("/api/tts", handle_tts)
app.router.add_get("/api/tts", handle_tts)
app.router.add_post("/api/v1/citas", handle_citas)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8643"))
    print(f"[ai] escuchando :{port} (chain: {' -> '.join(MODEL_CHAIN)})", flush=True)
    web.run_app(app, host="127.0.0.1", port=port)
