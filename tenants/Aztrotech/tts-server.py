"""
TTS Server local — API compatible con Qwen3-TTS
Usa edge-tts como backend, misma API que el VPS.
Endpoint: POST /tts  {"text": "...", "voice": "cesar", "output": "/tmp/out.wav"}
"""
import os
import json
import subprocess
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler


def _ffmpeg():
    """Devuelve binario ffmpeg funcional: prioriza el estático de imageio
    (el ffmpeg del sistema está roto por conflicto de libva en este equipo)."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if os.path.exists(exe):
            return exe
    except Exception:
        pass
    return "ffmpeg"

TTS_PORT = int(os.getenv("TTS_PORT", "8765"))
VOICES = {
    "cesar": "es-MX-DaliaNeural",        # Voz confirmada por César (100% local)
    "cesar_profesional": "es-MX-DaliaNeural",
    "cesar_calido": "es-MX-DaliaNeural",
    "default": "es-MX-DaliaNeural",
}


class TTSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            data = json.loads(body)
        except:
            self._respond(400, {"error": "JSON invalido"})
            return

        text = data.get("text", "")
        voice = data.get("voice", "default")
        output = data.get("output", "")

        if not text:
            self._respond(400, {"error": "text requerido"})
            return

        edge_voice = VOICES.get(voice, VOICES["default"])

        if output:
            out_path = output
        else:
            tag = str(hash(text + voice))[-8:]
            out_path = f"/tmp/tts-{tag}.wav"

        mp3_path = out_path.replace(".wav", ".mp3")
        result = subprocess.run(
            ["edge-tts", "--voice", edge_voice, "--text", text[:1000], "--write-media", mp3_path],
            capture_output=True, timeout=60,
        )

        if result.returncode != 0:
            self._respond(500, {"error": "TTS fallo", "detail": result.stderr.decode()[:200]})
            return

        subprocess.run(
            [_ffmpeg(), "-y", "-i", mp3_path, "-acodec", "pcm_s16le", "-ar", "24000", "-ac", "1", out_path],
            capture_output=True,
        )
        if os.path.exists(mp3_path):
            os.unlink(mp3_path)

        if os.path.exists(out_path):
            self._respond(200, {"text": text, "voice": voice, "output": out_path, "size": os.path.getsize(out_path)})
        else:
            self._respond(500, {"error": "No se generó el audio"})

    def do_GET(self):
        if self.path == "/health":
            self._respond(200, {"status": "ok", "engine": "edge-tts"})
        elif self.path == "/voices":
            self._respond(200, {"voices": list(VOICES.keys()), "available": "es-MX-DaliaNeural (confirmada)"})
        else:
            self._respond(404, {"error": "not found"})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", TTS_PORT), TTSHandler)
    print(f"TTS Server corriendo en :{TTS_PORT}")
    print(f"Voz César: es-MX-DaliaNeural (confirmada por César)")
    print(f"API: POST /tts  {{'text':'...','voice':'cesar','output':'...'}}")
    server.serve_forever()
