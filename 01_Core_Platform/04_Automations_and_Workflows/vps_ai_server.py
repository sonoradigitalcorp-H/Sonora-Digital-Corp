#!/usr/bin/env python3
"""vps_ai_server.py - Servidor API 24/7 sonoradigitalcorp.com (SDD-0012 v3 - Intent Router).

Pipeline 3 pasos:
  1. STT: faster-whisper tiny-int8 + Silero VAD (corta silencios, ahorra 70% CPU)
  2. Router Determinista: regex local para [calla, precio, cita, ubicacion] -> respuesta instantanea
  3. LLM Fallback: nemotron-3-ultra-free + clean_reply (max 320 chars)

Endpoints:
  POST /api/v1/chat/completions   OpenAI-compatible. person in {sdc,nathaly}.
  POST /api/v1/chat/voice         Audio -> STT -> Router -> LLM -> TTS (end-to-end voz)
  GET  /api/tts                   proxy -> tts_server :5293
  POST /api/stt                   proxy -> stt_server :5292
  GET  /health                    estado agregado llm+stt+tts
"""
import json
import os
import re
import tempfile
import time
import subprocess
from pathlib import Path

from aiohttp import web, ClientSession, ClientTimeout
from prometheus_client import Counter, Histogram, start_http_server

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['endpoint'])
LLM_LATENCY = Histogram('llm_request_duration_seconds', 'LLM request latency', ['model'])
LLM_TOKENS = Counter('llm_tokens_total', 'LLM tokens', ['model', 'type'])
LLM_FALLBACK = Counter('llm_fallback_total', 'LLM fallback count', ['model'])

# Start metrics server on port 9091
start_http_server(9091, addr='0.0.0.0')

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL_CHAIN = [
    "deepseek/deepseek-v4-flash-0731",          # principal: respuestas precisas y naturales
    "nvidia/nemotron-3-ultra-550b-a55b:free",   # fallback gratis
]
STT_URL = "http://127.0.0.1:5292/api/stt"
TTS_URL = "http://127.0.0.1:5293/api/tts"
COMPOSIO_API_KEY = os.environ.get("COMPOSIO_API_KEY", "")

# === Auth para endpoints sensibles de envio (fail-closed) ===
API_SERVER_KEY = os.environ.get("API_SERVER_KEY", "")

async def _authorized(request: web.Request) -> bool:
    """Valida Authorization: Bearer <API_SERVER_KEY>. Fail-closed: sin key o sin token -> False."""
    if not API_SERVER_KEY:
        return False
    auth = request.headers.get("Authorization", "")
    return auth.replace("Bearer ", "").strip() == API_SERVER_KEY

def require(key: str):
    """Decorator: exige auth en el handler marcado."""
    async def wrapper(request):
        if not await _authorized(request):
            return web.json_response({"error": "unauthorized"}, status=401)
        return await key(request)
    return wrapper

# === Memoria persistente (Supabase) ===
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor

SUPABASE_HOST = os.environ.get("SUPABASE_HOST", "localhost")
SUPABASE_PORT = os.environ.get("SUPABASE_PORT", "5434")
SUPABASE_DB   = os.environ.get("SUPABASE_DB", "postgres")
SUPABASE_USER = os.environ.get("SUPABASE_USER", "postgres")
SUPABASE_PASS = os.environ.get("SUPABASE_PASS", "")
if not SUPABASE_PASS:
    # Fail-closed: credenciales via env inyectadas por systemd, NUNCA leidas de archivo.
    print("[supabase] SUPABASE_PASS no seteado — fallo la conexion por env", flush=True)

def _pg_conn(tenant="tubandera"):
    conn = psycopg2.connect(
        host=SUPABASE_HOST, port=SUPABASE_PORT, dbname=SUPABASE_DB,
        user=SUPABASE_USER, password=SUPABASE_PASS
    )
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SET app.current_tenant = %s", (tenant,))
    return conn, cur

def get_memoria(chat_id, tenant, limit=5):
    try:
        conn, cur = _pg_conn(tenant)
        cur.execute(
            "SELECT mensaje, respuesta FROM public.conversaciones WHERE chat_id=%s AND tenant_id=%s ORDER BY creado_en DESC LIMIT %s",
            (str(chat_id), tenant, limit)
        )
        rows = cur.fetchall()
        cur.close(); conn.close()
        # orden cronologico (mas antiguo primero)
        return [(r["mensaje"], r["respuesta"]) for r in reversed(rows)]
    except Exception as e:
        print(f"[memoria] get error: {e}", flush=True)
        return []

def guardar_conversacion(chat_id, tenant, mensaje, respuesta):
    try:
        conn, cur = _pg_conn(tenant)
        cur.execute(
            "INSERT INTO public.conversaciones (tenant_id, chat_id, mensaje, respuesta) VALUES (%s, %s, %s, %s)",
            (tenant, str(chat_id), mensaje, respuesta)
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"[memoria] save error: {e}", flush=True)

async def async_get_memoria(chat_id, tenant, limit=5):
    return await asyncio.to_thread(get_memoria, chat_id, tenant, limit)

async def async_guardar_conversacion(chat_id, tenant, mensaje, respuesta):
    return await asyncio.to_thread(guardar_conversacion, chat_id, tenant, mensaje, respuesta)

SOULS = {
    "sdc": (
        "Eres el asistente de Sonora Digital Corp en Hermosillo, Sonora. Ayudas a duenos "
        "de negocio a recuperar tiempo: tu empresa queda atendiendo sola las 24 horas "
        "(mensajes, citas, clientes) mientras el dueno crece y no pierde ventas.\n"
        "REGLAS DURAS:\n"
        "1. Nunca uses signos de exclamacion ni i ni ! y nunca des respuestas con asteriscos ni markdown.\n"
        "2. Nunca digas IA, bot, modelo, inteligencia artificial, automatizacion. Di 'asistente' o 'te ayudo'.\n"
        "3. Vende beneficios concretos y AHORROS en tiempo/dinero: 'recuperas hasta 16 horas al mes', "
        "'dejas de pagar un sueldo de recepcionista', 'ningun cliente sin atender aunque sea de madrugada'.\n"
        "4. Maximo 4 frases cortas. Tono tranquilo, seguro, cercano. Espanol mexicano neutro.\n"
        "5. Precios jamas inventar: el diagnostico inicial es gratis y los precios exactos los da Luis Daniel.\n"
        "6. MANEJO DE OBJECIONES (siempre desde beneficio):\n"
        "   - 'es caro' -> 'mas barato que una recepcionista, y atiende 24 horas sin sueldo ni prestaciones'.\n"
        "   - 'me da miedo la tecnologia' -> 'no tienes que saber nada tecnico, yo me encargo de todo'.\n"
        "   - 'no tengo tiempo' -> 'es justo lo que te devuelve, horas cada semana'.\n"
        "   - 'es para empresas grandes' -> 'es para negocios como el tuyo, este es tu tamano ideal'.\n"
        "7. SIEMPRE CIERRA CON CITA: propone agendar el diagnostico. Se concreto, sugiere 2 horarios de esta "
        "semana. La conversacion debe avanzar SIEMPRE hacia una fecha concreta.\n"
        "8. NUNCA repitas la misma pregunta ni el mismo escenario. Cada respuesta avanza.\n"
        "9. Si el usuario pide silencio (calla, silencio, basta, ya no hables): responde breve y detente.\n"
        "10. Si preguntan como funciona: 'es mi asistente personal trabajando para ti, sin que toques nada'."
    ),
    "nathaly": (
        "Eres la asistente de Nathaly Hermosillo, contadora en Hermosillo, Sonora "
        "(Hermosillo Contabilidad). Servicios: contabilidad mensual, administracion y nomina, "
        "manifestacion de importacion, consultas y citas ante el SAT, marketing.\n"
        "REGLAS DURAS:\n"
        "1. Nunca uses signos de exclamacion ni i ni ! y nunca des respuestas con asteriscos ni markdown.\n"
        "2. Nunca digas IA, bot, modelo, inteligencia artificial. Di 'asistente de Nathaly'.\n"
        "3. Jamas inventes precios: 'la cotizacion exacta te la da Nathaly por WhatsApp'. El diagnostico inicial es gratis.\n"
        "4. Vende AHORROS y orden: 'cero multas del SAT', '8 horas al mes de vuelta'.\n"
        "5. Maximo 4 frases cortas. Tono tranquilo, cercano, profesional. Zona horaria America/Hermosillo.\n"
        "6. MANEJO DE OBJECIONES (siempre desde beneficio):\n"
        "   - 'es caro' -> 'una multa del SAT sale mas cara que llevar todo en orden'.\n"
        "   - 'no llevo mucho movimiento' -> 'justo por eso conviene tenerlo en regla desde ahora'.\n"
        "   - 'ya tengo contador' -> 'puedo revisar tu situacion sin costo y te digo si te conviene cambiarte'.\n"
        "   - 'me da flojera' -> 'Nathaly se encarga de todo, tu solo firmas'.\n"
        "7. SIEMPRE CIERRA CON CITA: propone agendar la revision con Nathaly. Se concreta, sugiere "
        "2 horarios de esta semana.\n"
        "8. NUNCA repitas la misma pregunta. Cada respuesta avanza.\n"
        "9. Si el usuario pide silencio (calla, silencio, basta): responde breve y detente.\n"
        "10. WhatsApp de Nathaly: 662 349 8589."
    ),
    "tubandera": (
        "Eres el Asistente Oficial de Tu Bandera A.C., centro de rehabilitacion en Hermosillo, Sonora (presidido por Roberto Lara). Mision: recuperando vidas, restaurando familias. Ayudas a personas que buscan apoyo para ellas o un familiar, con acompanamiento humano las 24 horas.\n"
        "REGLAS DURAS:\n"
        "1. NUNCA des recetas ni prescripciones medicas. NUNCA emitas juicios de valor sobre el usuario o su familia. Jamas diagnostiques. Ante crisis o riesgo, deriva a un humano y a emergencias (911).\n"
        "2. Nunca uses signos de exclamacion ni markdown ni asteriscos. Nunca digas IA, bot, modelo, algoritmo. Di asistente o te acompano.\n"
        "3. Habla con calidez, cercania y esperanza. Espanol mexicano neutro. Respuesta humana en 2 a 4 frases cortas.\n"
        "4. Ofrecemos DIAGNOSTICO GRATUITO inicial. Haz 1 o 2 preguntas basicas respetuosas para orientar. Pide amablemente un telefono de contacto para asignar el diagnostico gratis y que el equipo clinico o Roberto contacten de inmediato.\n"
        "5. Servicios diferenciadores:\n"
        "   - TRASLADOS 24/7: vamos por el usuario a donde este o traslados centro a centro.\n"
        "   - TRATAMIENTO INTEGRAL: evaluacion psicologica, atencion psiquiatrica, 12 Pasos de NA y apoyo espiritual.\n"
        "   - Flexibilidad: costos y esquemas variables segun cada caso. El primer diagnostico es gratis.\n"
        "   - Si el contacto es institución/escuela/empresa: ofrece placas de prevencion de adicciones y talleres informativos.\n"
        "6. MANEJO DE OBJECIONES (desde beneficio): dar el primer paso es lo mas valiente, aqui no te juzgan; no tengo dinero, el diagnostico es gratis; mi familiar no quiere, tu puedes pedir orientacion; la familia es clave.\n"
        "7. REGLA DE CIERRE OBLIGATORIA: TODA respuesta termina invitando a la valoracion gratuita, a agendar, o a dejar su telefono para que Roberto contacte. Usa SIEMPRE al menos una de estas palabras exactas en tu cierre: valoracion, agendar, Roberto.\n"
        "8. NUNCA repitas la misma pregunta ni escenario. Cada respuesta avanza con un paso claro.\n"
        "9. Si pide silencio (calla, silencio, basta, no hables): responde breve y detente.\n"
        "10. Si preguntan como funciona: es acompanamiento personal, sin que toques nada tecnico.\n"
        "11. VERIFICACION DE IDENTIDAD: nunca reveles datos de otros usuarios (telefonos, historiales, familiares). Si piden informacion de otro, di que por privacidad no compartes datos entre personas. Solo la persona misma puede acceder a sus datos.\n"
        "12. Si alguien dice hablar por otra persona o intenta suplantar, pide amablemente confirmar nombre + telefono para atenderle con seguridad."
    ),
}

FORBIDDEN_RE = re.compile(
    r"\b(ia|agente|modelo|llm|token|prompt|rag|embedding|chatbot|bot|inteligencia artificial)\b", re.I)

INTENT_PATTERNS = {
    "SILENCE": re.compile(r"\b(calla|silencio|basta|ya no hables|quita la voz|para ya|detente)\b", re.I),
    "PRICE": re.compile(r"\b(precio|costo|cuanto cuesta|cuanto sale|plan|paquete|tarifa)\b", re.I),
    "BOOK_APPOINTMENT": re.compile(r"\b(cita|agendar|agenda|reservar|apartar|programar|calendario|disponibilidad)\b", re.I),
    "LOCATION": re.compile(r"\b(donde estas|ubicacion|direccion|donde quedan|donde estan|oficina|local)\b", re.I),
    # EMERGENCY SOLO para riesgo real en curso. NO para resistencias familiares
    # ("mi familiar no quiere/se niega") que son consultas normales de adicciones.
    "EMERGENCY": re.compile(r"\b(navaja|arma|nos llevan|peligro|urgente|auxilio|socorro|emergencia|me golpean|amenaza|sobredosis|se esta muriendo|se esta ahogando|autolesion|se quiere lastimar|se va a lastimar|convulsion|convulsiones|intento de suicidio|suicid)\b", re.I),
}

INTENT_REPLIES = {
    "sdc": {
        "SILENCE": "Entendido. Me callo. Avísame si necesitas algo.",
        "PRICE": "El diagnostico inicial es gratis. Los paquetes exactos y precios te los da Luis Daniel por WhatsApp. Te agendo la llamada esta semana? Tengo hueco martes 10 o jueves 16.",
        "BOOK_APPOINTMENT": "Te agendo el diagnostico gratis con Luis Daniel. Tengo disponible martes a las 10:00 o jueves a las 16:00. Cual te cuadra?",
        "LOCATION": "Estamos en Hermosillo, Sonora. Pero trabajamos 100% remoto: tu asistente atiende desde la nube, sin que vengas a oficina. Te cuento como funciona?",
    },
    "nathaly": {
        "SILENCE": "Entendido. Me callo. Avísame si necesitas algo mas.",
        "PRICE": "La revision inicial con Nathaly es gratis. La cotizacion exacta te la da ella por WhatsApp al 662 349 8589. Agendamos tu diagnostico esta semana? Tengo martes 10 u jueves 16.",
        "BOOK_APPOINTMENT": "Te agendo la revision contable gratis con Nathaly. Tengo martes a las 10:00 o jueves a las 16:00. Cual prefieres?",
        "LOCATION": "Nathaly atiende en Hermosillo, Sonora, y tambien 100% remoto. Todo por WhatsApp y videollamada. Te agendo la revision gratis?",
    },
    "tubandera": {
        "SILENCE": "Entendido. Me callo. Avisame si necesitas algo.",
        "PRICE": "La primera valoracion en Tu Bandera A.C. es gratuita. El plan y los costos exactos los define Roberto en una llamada sin compromiso. Dejame tus datos y te contacta.",
        "BOOK_APPOINTMENT": "Con gusto te apoyo. La primera valoracion en Tu Bandera A.C. es sin costo. Dejame tu nombre y telefono y Roberto te contacta para agendarte, o escríbenos por WhatsApp y Telegram.",
        "LOCATION": "Estamos en Cofre del Perote 9347, Hermosillo, Sonora. Tambien atendemos remoto. Dejame tus datos y te digo como llegar o coordinamos.",
        "EMERGENCY": "Entiendo que es una situación urgente. Por seguridad, si hay riesgo inmediato de daño, llama a emergencias al 911. Yo puedo ayudar a registrar el caso y poner en contacto a Roberto con la familia. ¿Hay peligro inminente? ¿Necesitas que te acompañe a un lugar seguro mientras contactamos al equipo?"
    },
}

def clean_reply(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = text.replace("¡", "").replace("!", ".")
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[.,]{2,}", ".", text)
    if len(text) > 320:
        cut = text.rfind(". ", 0, 320)
        if cut != -1:
            text = text[:cut + 1]
        else:
            text = text[:300].rsplit(" ", 1)[0] + "."
    return text.strip()


def soft_replace_tech(text: str) -> str:
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



CTA_WORDS = ("valoracion", "agendar", "roberto")
def ensure_cta_tubandera(person: str, text: str) -> str:
    if person != "tubandera" or not text:
        return text
    low = text.lower()
    if any(w in low for w in CTA_WORDS):
        return text
    return text.rstrip() + " Cuando quieras damos el siguiente paso: te agendo la valoracion gratuita de Tu Bandera, o dejas tu telefono y Roberto te contacta."

def detect_intent(text: str):
    t = text.strip().lower()
    for intent, pattern in INTENT_PATTERNS.items():
        if pattern.search(t):
            return intent
    return None


def get_intent_reply(person: str, intent: str) -> str:
    return INTENT_REPLIES.get(person, INTENT_REPLIES["sdc"]).get(intent, "")


async def composio_execute(toolkit: str, action: str, params: dict) -> dict:
    if not COMPOSIO_API_KEY:
        return {"error": "no composio key"}
    try:
        timeout = ClientTimeout(total=15)
        async with ClientSession(timeout=timeout) as session:
            async with session.post(
                f"https://api.composio.dev/v1/toolkits/{toolkit}/actions/{action}/execute",
                headers={"Authorization": f"Bearer {COMPOSIO_API_KEY}", "Content-Type": "application/json"},
                json={"params": params},
            ) as resp:
                return await resp.json()
    except Exception as e:
        return {"error": str(e)}


async def handle_chat_completions(request: web.Request) -> web.Response:
    t0 = time.time()
    endpoint = "/api/v1/chat/completions"
    try:
        data = await request.json()
    except Exception:
        data = {}

    if not data.get("messages") and data.get("text"):
        data["messages"] = [{"role": "user", "content": str(data["text"])}]

    messages = list(data.get("messages", []))
    # Read person from JSON body, query params, or form data
    person = data.get("person")
    if not person:
        person = request.query.get("person", "")
    person = (person or "").strip().lower()
    chat_id = data.get("chat_id")

    # Fail-fast if person not in SOULS
    if person not in SOULS:
        return web.json_response({
            "error": f"persona desconocida: {person}. Validas: {list(SOULS.keys())}"
        }, status=400)

    last_user_text = next((str(m.get("content", "")) for m in reversed(messages)
                           if m.get("role") == "user"), "")

    # === PASO 2: ROUTER DETERMINISTA ===
    intent = detect_intent(last_user_text)
    if intent:
        reply = get_intent_reply(person, intent)
        print(f"[router] intent={intent} person={person} {round(time.time()-t0,3)}s", flush=True)
        return web.json_response({
            "choices": [{"message": {"role": "assistant", "content": reply}}],
            "model": f"router-deterministic-{intent.lower()}",
            "intent": intent,
        })

    # === PASO 3: LLM FALLBACK ===
    if not messages or messages[0].get("role") != "system":
        messages.insert(0, {"role": "system", "content": SOULS[person]})
    elif "REGLAS DURAS" not in messages[0].get("content", ""):
        messages[0]["content"] = SOULS[person]

    # === MEMORIA: inyectar historial del usuario ===
    if chat_id:
        try:
            historial = await async_get_memoria(chat_id, person)
            # Insertar despues del system prompt (indice 1)
            offset = 1
            for user_msg, bot_resp in historial:
                messages.insert(offset, {"role": "user", "content": user_msg})
                messages.insert(offset + 1, {"role": "assistant", "content": bot_resp})
                offset += 2
        except Exception as e:
            print(f"[memoria] inject error: {e}", flush=True)

    headers = {
        "Content-Type": "application/json",
        "HTTP-Referer": "https://sonoradigitalcorp.com",
        "X-Title": "Sonora Digital Corp",
    }
    if OPENROUTER_API_KEY:
        headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

    last_err = None
    for model in MODEL_CHAIN:
        payload = {"model": model, "messages": messages, "max_tokens": 800}
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
                    content = clean_reply(content)
                    content = ensure_cta_tubandera(person, content)
                    if FORBIDDEN_RE.search(content):
                        content = soft_replace_tech(content)
                    res_json["choices"][0]["message"]["content"] = content
                    res_json["model"] = model
                    # Record metrics
                    elapsed = time.time() - t0
                    REQUEST_LATENCY.labels(endpoint=endpoint).observe(elapsed)
                    LLM_LATENCY.labels(model=model).observe(elapsed)
                    REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
                    # Extract token usage if available
                    usage = res_json.get("usage", {})
                    if usage.get("prompt_tokens"):
                        LLM_TOKENS.labels(model=model, type="input").inc(usage["prompt_tokens"])
                    if usage.get("completion_tokens"):
                        LLM_TOKENS.labels(model=model, type="output").inc(usage["completion_tokens"])
                    print(f"[chat] {model} {round(elapsed,2)}s person={person}", flush=True)
                    # Guardar en memoria
                    if chat_id:
                        try:
                            await async_guardar_conversacion(chat_id, person, last_user_text, content)
                        except Exception as e:
                            print(f"[memoria] save error: {e}", flush=True)
                    return web.json_response(res_json)
        except Exception as e:
            last_err = f"{model}: {e}"
            continue

    reply = ("Te ayudo con gusto. Cuentame de tu negocio y que te esta quitando tiempo, "
             "y te digo exactamente como lo resolveriamos. El diagnostico inicial es gratis.")
    fallback_by_persona = {
        # cada tenant cae a SU texto, nunca a otro (la key puede morir y no confundir marcas)
        "nathaly": ("Con gusto te ayudo con tu contabilidad. Cuentame que necesitas: "
                    "declaraciones, citas SAT o llevar tus cuentas al dia, y agendamos tu "
                    "diagnostico gratis con Nathaly. Tambien puedes escribirle directo al 662 349 8589."),
        "tubandera": ("Te acompaño con gusto. En Tu Bandera A.C. ayudamos a personas que buscan "
                      "apoyo para ellas o un familiar con temas de adicciones. La primera valoracion "
                      "es gratuita y sin compromiso. Dejame tu telefono y Roberto te contacta, o "
                      "escribenos por WhatsApp. Si hay riesgo inmediato, llama al 911."),
    }
    reply = fallback_by_persona.get(person, reply)
    REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - t0)
    return web.json_response({
        "choices": [{"message": {"role": "assistant", "content": reply}}],
        "model": "fallback-offline",
    })


async def handle_voice_chat(request: web.Request) -> web.Response:
    t0 = time.time()
    try:
        reader = await request.multipart()
        audio_data = None
        person = "sdc"
        async for part in reader:
            if part.name == "audio":
                audio_data = await part.read()
            elif part.name == "person":
                person = (await part.text()).strip()

        if not audio_data:
            return web.json_response({"error": "no audio"}, status=400)

        try:
            timeout = ClientTimeout(total=45)
            async with ClientSession(timeout=timeout) as session:
                async with session.post(STT_URL, data=audio_data,
                                        headers={"Content-Type": "audio/wav"}) as resp:
                    if resp.status != 200:
                        return web.json_response({"error": "stt failed"}, status=502)
                    stt_res = await resp.json()
        except Exception as e:
            return web.json_response({"error": f"stt: {e}"}, status=502)

    except Exception as e:
        return web.json_response({"error": f"parse: {e}"}, status=400)

    transcript = (stt_res.get("text") or "").strip()
    if not transcript:
        return web.json_response({"error": "empty transcript"}, status=400)

    intent = detect_intent(transcript)
    if intent:
        reply = get_intent_reply(person, intent)
        model_used = f"router-deterministic-{intent.lower()}"
    else:
        messages = [
            {"role": "system", "content": SOULS[person]},
            {"role": "user", "content": transcript},
        ]
        headers = {
            "Content-Type": "application/json",
            "HTTP-Referer": "https://sonoradigitalcorp.com",
            "X-Title": "Sonora Digital Corp",
        }
        if OPENROUTER_API_KEY:
            headers["Authorization"] = f"Bearer {OPENROUTER_API_KEY}"

        reply = None
        model_used = "fallback-offline"
        for model in MODEL_CHAIN:
            payload = {"model": model, "messages": messages, "max_tokens": 800}
            try:
                timeout = ClientTimeout(total=22)
                async with ClientSession(timeout=timeout) as session:
                    async with session.post("https://openrouter.ai/api/v1/chat/completions",
                                            headers=headers, json=payload) as resp:
                        if resp.status != 200:
                            continue
                        res_json = await resp.json()
                        content = res_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                        if content and content.strip():
                            reply = clean_reply(content)
                            reply = ensure_cta_tubandera(person, reply)
                            if FORBIDDEN_RE.search(reply):
                                reply = soft_replace_tech(reply)
                            model_used = model
                            break
            except Exception:
                continue

        if not reply:
            reply = ("Te ayudo con gusto. Cuentame de tu negocio y que te esta quitando tiempo, "
                     "y te digo exactamente como lo resolveriamos. El diagnostico inicial es gratis.")
            if person == "nathaly":
                reply = ("Con gusto te ayudo con tu contabilidad. Cuentame que necesitas: "
                         "declaraciones, citas SAT o llevar tus cuentas al dia, y agendamos tu "
                         "diagnostico gratis con Nathaly.")

    audio_response = b""
    try:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            async with session.post(TTS_URL, json={"text": reply, "person": person}) as resp:
                if resp.status == 200:
                    audio_response = await resp.read()
    except Exception:
        pass

    print(f"[voice] person={person} intent={intent or model_used} {round(time.time()-t0,2)}s", flush=True)

    import base64
    return web.json_response({
        "text": reply,
        "audio_base64": base64.b64encode(audio_response).decode() if audio_response else "",
        "intent": intent,
        "model": model_used,
        "transcript": transcript,
    })


async def handle_stt(request: web.Request) -> web.Response:
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
    import uuid
    import datetime
    from urllib.parse import urlparse, parse_qs

    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "json invalido"}, status=400)

    persona = data.get("persona", "sdc")
    nombre = (data.get("nombre") or "para ti").strip()
    negocio = (data.get("negocio") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    fecha = (data.get("fecha") or "").strip()
    hora = (data.get("hora") or "").strip()

    if not (telefono and fecha and hora):
        return web.json_response({"error": "faltan telefono/fecha/hora"}, status=400)

    digits = re.sub(r"\D", "", telefono)
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]

    # --- Google Calendar validation via Composio (best-effort; NO bloquea la cita) ---
    # api.composio.dev NO resuelve desde este VPS -> timeout corto (3s) para no retrasar la cita.
    calendar_status = "not_checked"
    if COMPOSIO_API_KEY:
        try:
            timeout = ClientTimeout(total=3)
            async with ClientSession(timeout=timeout) as session:
                # Check if the date/time is available via calendar
                async with session.post(
                    f"https://api.composio.dev/v1/toolkits/google-calendar-mcp/actions/check_availability/execute",
                    headers={"Authorization": f"Bearer {COMPOSIO_API_KEY}", "Content-Type": "application/json"},
                    json={"params": {"date": fecha, "time": hora, "participants": [{"name": nombre, "phone": digits}]}}
                ) as resp:
                    if resp.status == 200:
                        calendar_data = await resp.json()
                        calendar_status = calendar_data.get("status", "checked")
        except Exception as e:
            calendar_status = f"error: {str(e)[:50]}"

    # === Migrar cita a Supabase (fuente única de verdad) — ya no sqlite ===
    cita_id = str(uuid.uuid4())
    now = datetime.datetime.now().isoformat()
    try:
        conn, cur = _pg_conn(persona)
        # negocio + calendar_verified se colapsan en `notas` (schema supabase no tiene columnas propias)
        notas = ""
        if negocio:
            notas += f"negocio: {negocio} | "
        if calendar_status:
            notas += f"calendar: {calendar_status}"
        cur.execute(
            "INSERT INTO public.citas (tenant_id, persona, nombre, telefono, fecha, hora, estado, notas, creado_en) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (persona, persona, nombre, digits, fecha, hora, "confirmada", notas, now)
        )
        conn.commit()
        cur.close(); conn.close()
    except Exception as e:
        print(f"[citas] db error: {e}", flush=True)

    cierre_persona = {
        "sdc": "Te espero.",
        "nathaly": "Te espera Nathaly.",
        "tubandera": "Te espera el equipo de Tu Bandera.",
    }.get(persona, "Te espero.")
    msg = (f"Hola {nombre}. Tu cita queda confirmada para el {fecha} a las {hora}. "
           f"{cierre_persona} Si necesitas cambiar el dia, no dudes en escribir.")
    try:
        async with ClientSession(timeout=ClientTimeout(total=30)) as session:
            async with session.post(TTS_URL, json={"text": msg, "person": persona}) as resp:
                audio = await resp.read()
    except Exception as e:
        print(f"[citas] tts error: {e}", flush=True)
        audio = b""

    wacli_status_client = "skipped-no-audio"
    wacli_status_owner = "skipped-no-audio"
    # Notificar al dueno SOLO del tenant correcto, no global.
    # tubandera -> Roberto Lara | nathaly -> Nathaly (empresa) | sdc -> Luis Daniel
    owner_by_persona = {
        "tubandera": "5216623645186",
        "nathaly": "5216623498589",
        "sdc": "5216623538272",
    }
    owner_phone = os.environ.get("OWNER_PHONE", owner_by_persona.get(persona, ""))
    digits_client = digits
    owner_digits = re.sub(r"\D", "", owner_phone) if owner_phone else ""

    if audio:
        tmp = tempfile.mktemp(suffix=".ogg")
        Path(tmp).write_bytes(audio)
        wacli_bin = os.environ.get("WACLI_BIN", "/home/mystic/.local/bin/wacli")
        wacli_store = os.environ.get("WACLI_STORE", "/home/mystic/.wacli")
        try:
            to_client = f"{digits_client}@s.whatsapp.net"
            r = subprocess.run(
                [wacli_bin, "send", "voice", "--store", wacli_store,
                 "--to", to_client, "--file", tmp],
                capture_output=True, text=True, timeout=40,
            )
            wacli_status_client = "sent" if r.returncode == 0 else f"err:{r.stderr[:120]}"
        except Exception as e:
            wacli_status_client = f"err:{e}"
        if owner_digits:
            try:
                to_owner = f"{owner_digits}@s.whatsapp.net"
                r2 = subprocess.run(
                    [wacli_bin, "send", "voice", "--store", wacli_store,
                     "--to", to_owner, "--file", tmp],
                    capture_output=True, text=True, timeout=40,
                )
                wacli_status_owner = "sent" if r2.returncode == 0 else f"err:{r2.stderr[:120]}"
            except Exception as e:
                wacli_status_owner = f"err:{e}"
        try:
            Path(tmp).unlink()
        except Exception:
            pass

    print(f"[citas] {persona} {nombre} {fecha} {hora} wacli_client={wacli_status_client} wacli_owner={wacli_status_owner} calendar={calendar_status}", flush=True)
    return web.json_response({"ok": True, "cita_id": cita_id, "estado": "confirmada",
                              "wacli_client": wacli_status_client, "wacli_owner": wacli_status_owner,
                              "calendar_verified": calendar_status, "telefono": digits})


async def handle_whatsapp(request: web.Request) -> web.Response:
    """Exponer skill wacli como tool de Hermes (texto/voice/doc). Auto: API_SERVER_KEY.
    POST /api/v1/whatsapp {action: text|voice|doc|auth, phone, ...}"""
    data = {}
    if request.method == "POST":
        try:
            data = await request.json()
        except Exception:
            return web.json_response({"error": "json invalido"}, status=400)
    action = (data.get("action") or "text").strip()
    phone = str(data.get("phone") or "").strip()
    digits = re.sub(r"\D", "", phone)
    if len(digits) == 10:
        digits = "52" + digits
    elif len(digits) == 11 and digits.startswith("1"):
        digits = "52" + digits[1:]
    jid = f"{digits}@s.whatsapp.net"
    wacli_bin = os.environ.get("WACLI_BIN", "/home/mystic/wacli")
    wacli_store = os.environ.get("WACLI_STORE", "/home/mystic/.wacli")

    def run_wacli(args):
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=60)
            return r.returncode == 0, (r.stdout + r.stderr).strip()
        except Exception as e:
            return False, str(e)

    if action == "auth":
        ok, out = run_wacli([wacli_bin, "doctor", "--store", wacli_store])
        return web.json_response({"authenticated": "AUTHENTICATED" in out and "true" in out,
                                  "output": out})
    if action == "text":
        text = str(data.get("text") or "").strip()
        if not text:
            return web.json_response({"error": "text vacio"}, status=400)
        ok, out = run_wacli([wacli_bin, "send", "text", "--store", wacli_store,
                             "--to", jid, "--message", text])
        return web.json_response({"ok": ok, "output": out, "to": jid,
                                  "status": "sent" if ok else "error"})
    if action == "voice":
        audio_path = str(data.get("audio_path") or "").strip()
        if not audio_path:
            return web.json_response({"error": "audio_path vacio"}, status=400)
        ok, out = run_wacli([wacli_bin, "send", "voice", "--store", wacli_store,
                             "--to", jid, "--file", audio_path])
        return web.json_response({"ok": ok, "output": out, "to": jid,
                                  "status": "sent" if ok else "error"})
    if action == "doc":
        file_path = str(data.get("file_path") or "").strip()
        if not file_path:
            return web.json_response({"error": "file_path vacio"}, status=400)
        ok, out = run_wacli([wacli_bin, "send", "file", "--store", wacli_store,
                             "--to", jid, "--file", file_path])
        return web.json_response({"ok": ok, "output": out, "to": jid,
                                  "status": "sent" if ok else "error"})
    return web.json_response({"error": f"accion desconocida: {action}"}, status=400)


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
app.router.add_get("/metrics", lambda r: web.Response(
    text=__import__("prometheus_client").generate_latest().decode(),
    content_type="text/plain"
))
app.router.add_post("/api/v1/chat/completions", handle_chat_completions)
app.router.add_get("/api/v1/chat/completions", handle_chat_completions)
app.router.add_post("/api/v1/chat/voice", handle_voice_chat)
app.router.add_post("/api/stt", handle_stt)
app.router.add_get("/api/stt", handle_stt)
app.router.add_post("/api/tts", handle_tts)
app.router.add_get("/api/tts", handle_tts)
app.router.add_post("/api/v1/citas", handle_citas)
app.router.add_post("/api/v1/whatsapp", require(handle_whatsapp))
app.router.add_get("/api/v1/whatsapp", require(handle_whatsapp))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8643"))
    print(f"[ai] escuchando :{port} (chain: {' -> '.join(MODEL_CHAIN)})", flush=True)
    web.run_app(app, host="127.0.0.1", port=port)

