import os
import tempfile
import asyncio
import subprocess
from pathlib import Path
from typing import Optional

BASE = Path(__file__).parent
VENV_PYTHON = BASE / ".venv" / "bin" / "python3"

CESAR_REF_AUDIO = str(BASE / "cesar" / "processed" / "cesar-ref-short.wav")
CESAR_REF_TEXT_FILE = str(BASE / "cesar" / "ref_text_short.txt")


class TTS:
    def __init__(self, engine: str = "edge"):
        self.engine = engine
        self._model = None

    async def synthesize(self, text: str, *, voice: Optional[str] = None) -> Optional[bytes]:
        if self.engine == "edge":
            return await self._edge_tts(text, voice or "es-MX-DaliaNeural")
        elif self.engine == "qwen":
            return await self._qwen_tts(text)
        return None

    async def _edge_tts(self, text: str, voice: str) -> Optional[bytes]:
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                out = f.name
            proc = await asyncio.create_subprocess_exec(
                "edge-tts", "--voice", voice, "--text", text, "--write-media", out,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=30)
            with open(out, "rb") as f:
                data = f.read()
            os.unlink(out)
            return data
        except Exception:
            return None

    def _load_model(self):
        if self._model is not None:
            return
        import torch
        from qwen_tts import Qwen3TTSModel
        self._model = Qwen3TTSModel.from_pretrained(
            "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
            device_map="cpu",
            dtype=torch.float32,
        )

    async def _qwen_tts(self, text: str) -> Optional[bytes]:
        import soundfile as sf
        self._load_model()

        model = self._model
        with open(CESAR_REF_TEXT_FILE) as f:
            ref_text = f.read().strip()

        loop = asyncio.get_event_loop()
        wavs, sr = await loop.run_in_executor(
            None,
            lambda: model.generate_voice_clone(
                text=text,
                language="Spanish",
                ref_audio=CESAR_REF_AUDIO,
                ref_text=ref_text,
            ),
        )
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            out = f.name
        sf.write(out, wavs[0], sr)
        with open(out, "rb") as f:
            data = f.read()
        os.unlink(out)
        return data
