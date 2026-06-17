"""
JARVIS Text-to-Speech Module
Multi-engine TTS with priority queue, async playback, and interruption support.
"""

import os
import asyncio
import logging
import subprocess
import threading
from queue import Queue
from typing import Optional, Callable

log = logging.getLogger("jarvis.voice.tts")

AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache", "voice")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ---------- TTS Functions ----------


def speak(text: str, lang: str = "es", voice: Optional[str] = None) -> Optional[str]:
    """
    Synthesize speech from text, return path to generated audio file.
    
    Uses engines in priority order:
    1. edge-tts (online, high quality)
    2. gTTS (online, lightweight)
    3. espeak (offline, basic)
    
    Args:
        text: Text to synthesize
        lang: Language code (es, en, etc.)
        voice: Specific voice name (optional)
    
    Returns:
        Path to generated audio file, or None if all engines fail
    """
    out = os.path.join(AUDIO_DIR, "output.wav")

    # Try edge-tts (online, high quality)
    result = _try_edge_tts(text, lang, voice, out)
    if result:
        return result

    # Try gTTS (lightweight online)
    result = _try_gtts(text, lang, out)
    if result:
        return result

    # Fallback: espeak via subprocess
    result = _try_espeak(text, lang, out)
    if result:
        return result

    log.error(f"All TTS engines failed for: {text[:50]}...")
    return None


def _try_edge_tts(text: str, lang: str, voice: Optional[str], out: str) -> Optional[str]:
    """Try edge-tts (Microsoft Edge TTS, online, high quality)."""
    try:
        import edge_tts

        voice_map = {
            "es": voice or "es-MX-DaliaNeural",
            "en": voice or "en-US-JennyNeural",
            "fr": voice or "fr-FR-DeniseNeural",
            "de": voice or "de-DE-KatjaNeural",
            "it": voice or "it-IT-ElsaNeural",
            "pt": voice or "pt-BR-FranciscaNeural",
        }

        selected_voice = voice_map.get(lang[:2], voice or "es-MX-DaliaNeural")

        async def _gen():
            communicate = edge_tts.Communicate(text, selected_voice)
            await communicate.save(out)

        asyncio.run(_gen())

        if os.path.exists(out) and os.path.getsize(out) > 100:
            log.info(f"edge-tts generated: {out} ({os.path.getsize(out)} bytes)")
            return out

    except ImportError:
        pass
    except Exception as e:
        log.warning(f"edge-tts failed: {e}")

    return None


def _try_gtts(text: str, lang: str, out: str) -> Optional[str]:
    """Try gTTS (Google Text-to-Speech, online, lightweight)."""
    try:
        from gtts import gTTS
        tts = gTTS(text, lang=lang[:2] if len(lang) >= 2 else "es", slow=False)
        tts.save(out)

        if os.path.exists(out) and os.path.getsize(out) > 100:
            log.info(f"gTTS generated: {out} ({os.path.getsize(out)} bytes)")
            return out

    except ImportError:
        pass
    except Exception as e:
        log.warning(f"gTTS failed: {e}")

    return None


def _try_espeak(text: str, lang: str, out: str) -> Optional[str]:
    """Try espeak (offline, basic quality)."""
    try:
        lang_code = lang[:2] if len(lang) >= 2 else "es"
        subprocess.run(
            ["espeak", "-v", lang_code, "-w", out, text],
            check=False,
            timeout=30,
            capture_output=True
        )

        if os.path.exists(out) and os.path.getsize(out) > 100:
            log.info(f"espeak generated: {out} ({os.path.getsize(out)} bytes)")
            return out

    except FileNotFoundError:
        log.warning("espeak not installed")
    except Exception as e:
        log.warning(f"espeak failed: {e}")

    return None


def play_audio(path: str, block: bool = False) -> bool:
    """
    Play audio file using available player.
    
    Args:
        path: Path to audio file
        block: If True, wait for playback to finish
    
    Returns:
        True if playback started successfully
    """
    if not path or not os.path.exists(path):
        return False

    try:
        # Try ffplay
        try:
            proc = subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if block:
                proc.wait()
            return True
        except FileNotFoundError:
            pass

        # Try aplay
        try:
            proc = subprocess.Popen(
                ["aplay", "-q", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if block:
                proc.wait()
            return True
        except FileNotFoundError:
            pass

        log.warning("No audio player found (ffplay/aplay)")
        return False

    except Exception as e:
        log.warning(f"Playback error: {e}")
        return False


# ---------- TTS Queue Engine ----------


class TTSEngine:
    """
    TTS engine with asynchronous queue and playback management.
    
    Features:
    - Queue-based speech synthesis
    - Priority queuing (urgent messages jump the queue)
    - Playback interruption
    - Callbacks for speech events
    """

    def __init__(self):
        self._queue: Queue = Queue()
        self._playing = False
        self._interrupted = False
        self._thread: Optional[threading.Thread] = None
        self._on_start: Optional[Callable] = None
        self._on_end: Optional[Callable] = None
        self._running = False

    def on_start(self, callback: Callable):
        """Register callback when speech starts."""
        self._on_start = callback

    def on_end(self, callback: Callable):
        """Register callback when speech ends."""
        self._on_end = callback

    def say(self, text: str, lang: str = "es", priority: bool = False):
        """
        Add text to speech queue.
        
        Args:
            text: Text to speak
            lang: Language code
            priority: If True, add to front of queue
        """
        item = {"text": text, "lang": lang}
        if priority:
            # Insert at front: create temp list, add to front, recreate queue
            items = []
            while not self._queue.empty():
                items.append(self._queue.get())
            items.insert(0, item)
            for it in items:
                self._queue.put(it)
        else:
            self._queue.put(item)

        log.info(f"TTS queued: '{text[:40]}...' (priority={priority})")

    def interrupt(self):
        """Interrupt current speech and clear queue."""
        self._interrupted = True
        # Clear queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except Exception:
                break
        log.info("TTS interrupted")

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    def start(self):
        """Start the TTS worker thread."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()
        log.info("TTS engine started")

    def stop(self):
        """Stop the TTS worker thread."""
        self._running = False
        self._interrupted = True
        if self._thread:
            self._thread.join(timeout=2)
        log.info("TTS engine stopped")

    def _worker(self):
        """Background worker processing TTS queue."""
        while self._running:
            try:
                item = self._queue.get(timeout=0.5)
            except Exception:
                continue

            if self._interrupted:
                self._interrupted = False
                continue

            text = item["text"]
            lang = item["lang"]

            try:
                if self._on_start:
                    self._on_start()

                self._playing = True
                audio_path = speak(text, lang=lang)

                if audio_path and not self._interrupted:
                    play_audio(audio_path, block=True)

                self._playing = False

                if self._on_end:
                    self._on_end()

            except Exception as e:
                log.warning(f"TTS worker error: {e}")
                self._playing = False

            self._queue.task_done()


# Singleton instance
_engine: Optional[TTSEngine] = None


def get_engine() -> TTSEngine:
    """Get or create the global TTS engine."""
    global _engine
    if _engine is None:
        _engine = TTSEngine()
    return _engine
