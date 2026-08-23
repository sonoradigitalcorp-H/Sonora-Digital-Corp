#!/usr/bin/env python3
"""stt_server.py — Speech-to-Text en VPS OVH (SDD-0012).
faster-whisper small int8 CPU. Puerto :5292.
POST /api/stt  (multipart file=@audio.webm|ogg|mp3, person opcional)
GET  /health
Diseñado para systemd sdc-stt.service con Restart=always en 149.56.46.173.
"""
import io
import os
import re
import time

from aiohttp import web

MODEL_NAME = os.environ.get("STT_MODEL", "small")     # small int8 ~500MB RAM
COMPUTE = os.environ.get("STT_COMPUTE", "int8")
PORT = int(os.environ.get("STT_PORT", "5292"))
MAX_AUDIO_SECONDS = 60

_model = None


def get_model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        t0 = time.time()
        _model = WhisperModel(MODEL_NAME, device="cpu", compute_type=COMPUTE)
        print(f"[stt] modelo {MODEL_NAME}/{COMPUTE} cargado en {time.time()-t0:.1f}s", flush=True)
    return _model


async def handle_stt(request: web.Request) -> web.Response:
    t0 = time.time()
    reader = await request.multipart()
    audio_bytes = None
    lang = os.environ.get("STT_LANG", "es")
    async for part in reader:
        if part.name == "file":
            audio_bytes = await part.read(decode=False)
        elif part.name == "lang":
            lang = (await part.text()) or lang
        elif part.name == "text" and audio_bytes is None:
            pass
    if request.method == "POST" and audio_bytes is None:
        # fallback: body raw binario
        audio_bytes = await request.read()

    if not audio_bytes:
        return web.json_response({"error": "no audio"}, status=400)
    if len(audio_bytes) > 12 * 1024 * 1024:
        return web.json_response({"error": "audio demasiado grande"}, status=413)

    model = get_model()
    segments, info = model.transcribe(
        io.BytesIO(audio_bytes), language=lang,
        beam_size=3, vad_filter=True,
        condition_on_previous_text=False,
        initial_prompt="Conversación de negocio en español mexicano. "
                       "Nombres comunes: Sonora Digital Corp, Nathaly, Hermosillo, SAT.")
    text = " ".join(s.text for s in segments).strip()
    # Whisper es-MX suele añadir exclamaciones alucinadas: SOUL dice cero.
    text = re.sub(r"^[\s¡!]+", "", text)
    text = text.replace("!", "").replace("¡", "").replace("  ", " ").strip()

    out = {"text": text, "lang": info.language,
           "duration_s": round(info.duration, 2),
           "took_s": round(time.time() - t0, 2)}
    print(f"[stt] {out}", flush=True)
    return web.json_response(out)


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok", "service": "sdc-stt",
        "model": MODEL_NAME, "compute": COMPUTE, "loaded": _model is not None,
    })


def main():
    # Warm-up ANTES de abrir puerto: primer request ya es rápido.
    try:
        get_model()
    except Exception as e:
        print(f"[stt] warm-up falló (se reintenta en 1er request): {e}", flush=True)

    app = web.Application(client_max_size=16 * 1024 * 1024)
    app.router.add_post("/api/stt", handle_stt)
    app.router.add_get("/health", handle_health)
    print(f"[stt] escuchando :{PORT}", flush=True)
    web.run_app(app, host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
