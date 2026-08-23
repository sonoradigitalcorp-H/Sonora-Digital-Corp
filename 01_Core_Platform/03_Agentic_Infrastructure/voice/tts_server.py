#!/usr/bin/env python3
"""tts_server.py — Text-to-Speech en VPS OVH (SDD-0012).
Primary: kokoro-onnx es-MX ($0, local). Fallback: edge-tts (red, $0).
Puerto :5292+1 = :5293.
GET  /api/tts?text=&person=&voice=   → audio/mpeg stream
POST /api/tts {text, person, voice}  → audio/mpeg
GET  /health
systemd sdc-tts.service, Restart=always.
Reglas SOUL: limpia exclamaciones y símbolos antes de sintetizar.
"""
import asyncio
import io
import os
import re
import time

from aiohttp import web

PORT = int(os.environ.get("TTS_PORT", "5293"))
KOKORO_ONNX_DIR = os.environ.get("KOKORO_DIR", "/opt/hermes/kokoro")
VOICES = {
    "sdc": os.environ.get("TTS_VOICE_SDC", "es-MX-JorgeNeural"),
    "nathaly": os.environ.get("TTS_VOICE_NATHALY", "es-MX-DaliaNeural"),
}
MAX_TEXT_CHARS = 900

_kokoro = None
_kokoro_voice_id = None


def clean_for_tts(text: str) -> str:
    """SOUL: sin exclamaciones, emojis ni markdown. Preguntas suaves se quedan."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]", "", text)
    text = text.replace("!", ".").replace("¡", "")
    text = re.sub(r"[*_`#>]{1,}", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"[.,]{2,}", ".", text)
    return text.strip()


def try_kokoro():
    """Carga kokoro-onnx si existe el modelo en disco. Silencioso si no."""
    global _kokoro, _kokoro_voice_id
    try:
        from kokoro_onnx import Kokoro
        model_path = os.path.join(KOKORO_ONNX_DIR, "kokoro-v0_19.onnx")
        voices_path = os.path.join(KOKORO_ONNX_DIR, "voices-v1.0.bin")
        if not (os.path.exists(model_path) and os.path.exists(voices_path)):
            print("[tts] kokoro no instalado en disco — uso edge-tts", flush=True)
            return None
        _kokoro = Kokoro(model_path, voices_path)
        _kokoro_voice_id = os.environ.get("KOKORO_VOICE", "ef_dora")  # voz es femenina
        print("[tts] kokoro listo", flush=True)
    except Exception as e:
        print(f"[tts] kokoro no disponible ({e}) — uso edge-tts", flush=True)
        _kokoro = None
    return _kokoro


async def synth_edge(text: str, voice: str) -> bytes:
    import edge_tts
    communicate = edge_tts.Communicate(text[:MAX_TEXT_CHARS], voice)
    buf = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.extend(chunk["data"])
    return bytes(buf)


async def handle_tts(request: web.Request) -> web.Response:
    t0 = time.time()
    if request.method == "POST":
        try:
            data = await request.json()
        except Exception:
            data = {}
        text = data.get("text", "")
        person = data.get("person", "sdc")
        voice = data.get("voice") or VOICES.get(person, VOICES["sdc"])
    else:
        q = request.query
        text = q.get("text", "")
        person = q.get("person", "sdc")
        voice = q.get("voice") or VOICES.get(person, VOICES["sdc"])

    if not text:
        return web.json_response({"error": "no text"}, status=400)

    text = clean_for_tts(text)
    if not text:
        return web.json_response({"error": "texto vacío tras limpieza"}, status=400)

    engine = "edge-tts"
    try:
        if _kokoro is not None and person == "nathaly":
            # kokoro solo para la voz femenina por ahora; sample rate 24000
            async def _gen():
                audio, sr = await asyncio.to_thread(
                    _kokoro.create, text[:MAX_TEXT_CHARS], voice=_kokoro_voice_id,
                    speed=1.0, lang="es")
                return audio, sr
            audio, sr = await asyncio.wait_for(_gen(), timeout=25)
            buf = io.BytesIO()
            import wave
            with wave.open(buf, "wb") as w:  # wav contenedor; nginx/browser lo acepta
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(sr)
                w.writeframes((audio * 32767).astype("<i2").tobytes())
            body, ctype, engine = buf.getvalue(), "audio/wav", "kokoro"
        else:
            body = await synth_edge(text, voice)
            ctype = "audio/mpeg"
    except Exception as e:
        print(f"[tts] primary falló ({e}) → edge-tts fallback", flush=True)
        try:
            body = await synth_edge(text, VOICES[person])
            ctype = "audio/mpeg"
        except Exception as e2:
            return web.json_response({"error": str(e2)}, status=502)

    took = round(time.time() - t0, 2)
    print(f"[tts] {engine} {len(body)}B {took}s voice={voice}", flush=True)
    return web.Response(body=body, content_type=ctype,
                        headers={"Cache-Control": "public,max-age=3600",
                                 "X-TTS-Engine": engine, "X-TTS-Took": str(took)})


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "service": "sdc-tts",
                              "kokoro": _kokoro is not None})


def main():
    try:
        try_kokoro()
    except Exception:
        pass
    app = web.Application(client_max_size=1 * 1024 * 1024)
    app.router.add_get("/api/tts", handle_tts)
    app.router.add_post("/api/tts", handle_tts)
    app.router.add_get("/health", handle_health)
    print(f"[tts] escuchando :{PORT}", flush=True)
    web.run_app(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
