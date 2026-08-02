import asyncio
import json
import logging
import os
import io
import wave
import time
import uuid
import struct
import glob
import subprocess
import tempfile

from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.mediastreams import AudioFrame

import edge_tts
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pipeline.orchestrator import CallSession
from pipeline.context import detect_objection
from pipeline.gate_output import check_response, sanitize
from ai.llm import compose_prompt, generate_response
from campaigns.scraper import get_leads
from campaigns.orchestrator import get_campaign_summary
from analytics.scorer import get_ab_stats
from tenant.service import _load_tenants, get_lead_type, get_call_history

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT = os.path.join(os.path.dirname(__file__), "..")

# Preload whisper on first call instead of at startup
_whisper_loaded = False
def ensure_whisper():
    global _whisper_loaded
    if not _whisper_loaded:
        logger.info("Cargando whisper...")
        from ai.stt import get_whisper
        get_whisper()
        _whisper_loaded = True
        logger.info("✅ Whisper listo")

ROOT = os.path.join(os.path.dirname(__file__), "..")
WEB_DIR = os.path.join(ROOT, "frontend", "dist")
if not os.path.exists(WEB_DIR):
    WEB_DIR = os.path.join(ROOT, "web")
logger.info(f"Serving from: {WEB_DIR}")

pcs = set()
sessions = {}


class ResponseAudioTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()
        self._ended = False

    async def recv(self):
        if self._ended and self.queue.empty():
            raise Exception("Track ended")
        frame = await self.queue.get()
        return frame

    def stop(self):
        self._ended = True

    async def add_tts(self, text, voice="es-MX-DaliaNeural"):
        try:
            tts = edge_tts.Communicate(text, voice)
            audio_data = b""
            async for chunk in tts.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            if not audio_data:
                logger.warning("TTS generó audio vacío")
                return

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                tmp_mp3.write(audio_data)
                mp3_path = tmp_mp3.name

            wav_path = mp3_path.replace(".mp3", ".wav")
            subprocess.run(
                ["ffmpeg", "-y", "-i", mp3_path, "-acodec", "pcm_s16le",
                 "-ar", "48000", "-ac", "1", wav_path],
                capture_output=True, timeout=10
            )

            with wave.open(wav_path, "rb") as wf:
                sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())

            os.unlink(mp3_path)
            os.unlink(wav_path)

            chunk_size = 960  # 20ms at 48000Hz
            pts = 0
            for i in range(0, len(frames), chunk_size * 2):
                chunk = frames[i:i + chunk_size * 2]
                if len(chunk) < chunk_size * 2:
                    chunk = chunk.ljust(chunk_size * 2, b'\0')
                frame = AudioFrame(format="s16", layout="mono", samples=chunk_size)
                frame.planes[0].update(chunk)
                frame.sample_rate = sample_rate
                frame.pts = pts
                pts += chunk_size
                await self.queue.put(frame)
                await asyncio.sleep(0.002)  # small yield to prevent queue flood
        except Exception as e:
            logger.error(f"Error en TTS: {e}")


_pending_candidates = {}
_pending_pcs = {}


async def handle_offer(client_id, ws, sdp, candidate=None):
    if candidate:
        pc = _pending_pcs.get(client_id) or next(
            (pc for pc in pcs if getattr(pc, "client_id", None) == client_id), None
        )
        if pc and pc.remoteDescription:
            try:
                from aiortc.sdp import candidate_from_sdp
                ic = candidate_from_sdp(candidate["candidate"])
                ic.sdpMid = candidate.get("sdpMid", "0")
                ic.sdpMLineIndex = candidate.get("sdpMLineIndex", 0)
                await pc.addIceCandidate(ic)
            except Exception as e:
                logger.warning(f"ICE candidate error: {e}")
        elif pc:
            _pending_candidates.setdefault(client_id, []).append(candidate)
        return

    pc = RTCPeerConnection()
    pc.client_id = client_id
    pcs.add(pc)
    _pending_pcs[client_id] = pc

    session = CallSession(client_id, ws)
    sessions[client_id] = session
    response_track = ResponseAudioTrack()
    pc.addTrack(response_track)

    try:
        await pc.setRemoteDescription(RTCSessionDescription(sdp=sdp, type="offer"))
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)
        await ws.send_str(json.dumps({"type": "answer", "sdp": pc.localDescription.sdp}))
        logger.info("✅ WebRTC connected — playing welcome")

        # Play welcome AFTER connection is established
        asyncio.ensure_future(
            response_track.add_tts(
                "Hola, soy Mystica de Sonora Digital Corp. "
                "¿Cómo te llamas?"
            )
        )

        # Flush pending candidates
        for c in _pending_candidates.pop(client_id, []):
            try:
                from aiortc.sdp import candidate_from_sdp
                ic = candidate_from_sdp(c["candidate"])
                ic.sdpMid = c.get("sdpMid", "0")
                ic.sdpMLineIndex = c.get("sdpMLineIndex", 0)
                await pc.addIceCandidate(ic)
            except Exception as e:
                logger.warning(f"Pending candidate error: {e}")
    except Exception as e:
        logger.error(f"Offer error: {e}")
        await ws.send_str(json.dumps({"type": "error", "text": str(e)}))
        pcs.discard(pc)
        _pending_pcs.pop(client_id, None)
        return

    @pc.on("track")
    async def on_track(track):
        logger.info(f"Track: {track.kind}")
        if track.kind != "audio":
            return

        # Ensure whisper is loaded before processing audio
        ensure_whisper()
        buf = bytearray()
        n = 0
        while True:
            try:
                frame = await asyncio.wait_for(track.recv(), timeout=3.0)
                buf.extend(frame.data)
                n += 1
            except asyncio.TimeoutError:
                if n >= 20:  # ~0.4s of audio
                    raw = bytes(buf)
                    buf = bytearray()
                    n = 0
                    try:
                        logger.info(f"Procesando audio ({len(raw)} bytes)...")
                        resp = await session.process_audio(raw, 48000)
                        logger.info(f"Respuesta: {resp[:100] if resp else 'None'}")
                        if resp and resp != "escalated":
                            await response_track.add_tts(resp)
                    except Exception as e:
                        logger.error(f"process_audio: {e}")
                        import traceback
                        traceback.print_exc()
                continue
            except Exception:
                break
        await session.end_call()

    @pc.on("connectionstatechange")
    async def on_state_change():
        if pc.connectionState in ("failed", "closed", "disconnected"):
            try:
                await ws.send_str(json.dumps({"type": "close"}))
            except Exception:
                pass
            if client_id in sessions:
                await sessions[client_id].end_call()
                del sessions[client_id]
            pcs.discard(pc)
            _pending_pcs.pop(client_id, None)


async def ws_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    client_id = str(uuid.uuid4())
    logger.info(f"WS cliente {client_id} conectado")

    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT:
                data = json.loads(msg.data)
                msg_type = data.get("type")
                if msg_type == "offer":
                    await handle_offer(client_id, ws, data["sdp"])
                elif msg_type == "candidate":
                    await handle_offer(client_id, ws, None, data.get("candidate"))
                elif msg_type == "text":
                    text = data.get("text", "")
                    session = sessions.get(client_id)
                    if not session:
                        session = CallSession(client_id, ws)
                        sessions[client_id] = session
                    # Try to identify if not yet registered
                    if not session.tenant:
                        result = await session._auto_register(text)
                        if result == "identified":
                            continue
                        await session._send("transcript", {"text": text})
                        continue
                    await session._send("transcript", {"text": text})
                    session.transcript_buffer.append(text)
                    lead_type = get_lead_type(session.tenant)
                    history = get_call_history(session.tenant["id"])
                    obj_cat, obj_text = detect_objection(text)
                    if obj_text:
                        session.detected_objection = obj_text
                    campaign = session.tenant.get("campaign", {})
                    msgs = compose_prompt(session.tenant, lead_type, text, obj_text, history,
                                         variant=session.ab_variant,
                                         conversation_history=session.conversation_history,
                                         campaign=campaign,
                                         turn_number=len(session.conversation_history) + 1)
                    temp = {"cold": 0.7, "warm": 0.5, "hot": 0.3}.get(lead_type, 0.5)
                    resp = await generate_response(msgs, temperature=temp)
                    gate = check_response(resp, text)
                    resp = gate["sanitized"]
                    session.conversation_history.append({"user": text, "assistant": resp})
                    await session._send("response", {"text": resp})
            elif msg.type == web.WSMsgType.ERROR:
                logger.error(f"WS error: {ws.exception()}")
    except Exception as e:
        logger.error(f"Error en WS: {e}")
    finally:
        pc_to_remove = [pc for pc in pcs if getattr(pc, "client_id", None) == client_id]
        for pc in pc_to_remove:
            await pc.close()
            pcs.discard(pc)
        if client_id in sessions:
            await sessions[client_id].end_call()
            del sessions[client_id]
        logger.info(f"Cliente {client_id} desconectado")

    return ws


async def index(request):
    return web.FileResponse(os.path.join(WEB_DIR, "index.html"))

async def legacy_call(request):
    return web.FileResponse(os.path.join(WEB_DIR, "call.html"))


async def creator_page(request):
    path = os.path.join(ROOT, "web", "creator.html")
    if os.path.exists(path):
        return web.FileResponse(path)
    return web.Response(text="Creator panel: use /dashboard for now", content_type="text/html")


async def dashboard_page(request):
    return web.FileResponse(os.path.join(WEB_DIR, "dashboard.html"))


async def api_dashboard(request):
    data_dir = os.path.join(ROOT, "data")
    calls_dir = os.path.join(data_dir, "calls")
    scores_dir = os.path.join(data_dir, "scores")

    calls = []
    if os.path.exists(calls_dir):
        for f in sorted(glob.glob(os.path.join(calls_dir, "*.json")), reverse=True)[:10]:
            with open(f) as fh:
                calls.append(json.load(fh))

    tenants_data = _load_tenants()
    tenants = tenants_data.get("tenants", [])
    total_calls = sum(t.get("total_calls", 0) for t in tenants)

    total_duration = 0
    for f in glob.glob(os.path.join(calls_dir, "*.json")):
        with open(f) as fh:
            c = json.load(fh)
            total_duration += c.get("duration_sec", 0)

    total_leads = len(get_leads())
    ab_stats = get_ab_stats()
    campaigns = get_campaign_summary()

    def serialize(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        return str(obj)

    def safe_sort_key(t):
        v = t.get("first_contact", "")
        return str(v) if not hasattr(v, 'isoformat') else v.isoformat()

    sorted_tenants = sorted(tenants, key=safe_sort_key, reverse=True)[:10]
    for t in sorted_tenants:
        if hasattr(t.get("first_contact"), 'isoformat'):
            t["first_contact"] = t["first_contact"].isoformat()

    return web.json_response({
        "total_tenants": len(tenants),
        "total_calls": total_calls,
        "total_duration": round(total_duration / 60),
        "total_leads": total_leads,
        "recent_calls": calls,
        "recent_tenants": sorted_tenants,
        "ab_stats": ab_stats,
        "campaigns": campaigns,
    })


async def api_tenants(request):
    tenants_data = _load_tenants()
    return web.json_response(tenants_data.get("tenants", []))


async def spa_fallback(request):
    return web.FileResponse(os.path.join(WEB_DIR, "index.html"))


async def widget_js(request):
    path = os.path.join(ROOT, "web", "widget.js")
    return web.FileResponse(path) if os.path.exists(path) else web.Response(text="// widget not found", content_type="application/javascript")


async def demo_sdc(request):
    path = os.path.join(ROOT, "web", "demo-sdc.html")
    return web.FileResponse(path) if os.path.exists(path) else web.Response(text="demo not found", content_type="text/html")


async def on_shutdown(app):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()


def create_app():
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/call", spa_fallback)
    app.router.add_get("/creator", creator_page)
    app.router.add_get("/dashboard", dashboard_page)
    app.router.add_get("/demo-sdc", demo_sdc)
    app.router.add_get("/widget.js", widget_js)
    app.router.add_get("/api/dashboard", api_dashboard)
    app.router.add_get("/api/tenants", api_tenants)
    app.router.add_get("/ws", ws_handler)
    app.router.add_static("/", WEB_DIR)
    return app


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    app = create_app()
    logger.info(f"✦ Mystica corriendo en http://localhost:{port}")
    logger.info(f"  → Landing:  http://localhost:{port}")
    logger.info(f"  → Llamada:  http://localhost:{port}/call")
    logger.info(f"  → Widget:   http://localhost:{port}/widget.js")
    logger.info(f"  → Demo SDC: http://localhost:{port}/demo-sdc")
    web.run_app(app, host="127.0.0.1", port=port)
