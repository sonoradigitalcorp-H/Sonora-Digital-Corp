"""
Mezclador de audio — combina TTS con música de fondo / soundscape.
Soporta:
- Soundscapes envolventes (nature, futurista, cálido, energético)
- Volumen dinámico (la música baja cuando Mystic habla)
- Cross-fade entre soundscapes
"""
import asyncio
import base64
import io
import json
import logging
import os
import struct
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger("voice-realtime.audio_mixer")

# ─── Soundscapes disponibles ───
SOUNDSCAPES = {
    "nature": {
        "name": "Naturaleza",
        "description": "Sonidos de bosque, agua y viento — ideal para consultoría",
        "tone": "calm",
        "sample_file": "nature_soundscape.raw",
        "default_volume": 0.08,
    },
    "futurista": {
        "name": "Futurista",
        "description": "Ambiente cyberpunk suave — ideal para tecnología",
        "tone": "energetic",
        "sample_file": "futurist_soundscape.raw",
        "default_volume": 0.06,
    },
    "calido": {
        "name": "Cálido",
        "description": "Ambiente acogedor con tonos bajos — ideal para ventas",
        "tone": "warm",
        "sample_file": "warm_soundscape.raw",
        "default_volume": 0.07,
    },
    "energetico": {
        "name": "Energético",
        "description": "Ritmo suave con energía — ideal para promociones",
        "tone": "energetic",
        "sample_file": "energetic_soundscape.raw",
        "default_volume": 0.05,
    },
    "minimal": {
        "name": "Minimal",
        "description": "Pad sintético sutil — fondo neutro para cualquier conversación",
        "tone": "neutral",
        "sample_file": "minimal_soundscape.raw",
        "default_volume": 0.04,
    },
}


class SoundscapeGenerator:
    """
    Genera soundscapes sintéticos (no requiere archivos de audio).
    Usa tonos puros, ruido de colores y beats suaves para crear ambientes.
    """

    SAMPLE_RATE = 44100

    def __init__(self):
        self._cache = {}

    def _generate_tone(self, freq: float, duration_ms: int, volume: float = 0.3) -> np.ndarray:
        """Genera un tono puro."""
        n_samples = int(self.SAMPLE_RATE * duration_ms / 1000)
        t = np.arange(n_samples) / self.SAMPLE_RATE
        tone = np.sin(2 * np.pi * freq * t).astype(np.float32) * volume
        return tone

    def _generate_noise(self, duration_ms: int, color: str = "pink", volume: float = 0.2) -> np.ndarray:
        """Genera ruido de color (white, pink, brown)."""
        n_samples = int(self.SAMPLE_RATE * duration_ms / 1000)
        if color == "white":
            noise = np.random.randn(n_samples).astype(np.float32)
        elif color == "pink":
            white = np.random.randn(n_samples).astype(np.float32)
            # Filtro de primer orden para pink noise
            noise = np.zeros_like(white)
            noise[0] = white[0]
            for i in range(1, n_samples):
                noise[i] = 0.99 * noise[i-1] + 0.01 * white[i]
        elif color == "brown":
            white = np.random.randn(n_samples).astype(np.float32)
            noise = np.cumsum(white)
            noise = noise / np.max(np.abs(noise)) * 0.5
        else:
            noise = np.random.randn(n_samples).astype(np.float32) * 0.1
        return noise * volume

    def generate_soundscape(self, name: str, duration_ms: int = 10000) -> bytes:
        """Genera un soundscape completo y devuelve bytes PCM16."""
        if name in self._cache:
            return self._cache[name]

        if name == "nature":
            # Viento suave (pink noise filtrado) + agua (white noise modulado)
            wind = self._generate_noise(duration_ms, "pink", 0.15)
            water = self._generate_noise(duration_ms, "white", 0.05)
            # Modulación lenta
            t = np.arange(len(wind)) / self.SAMPLE_RATE
            modulation = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
            wind = wind * modulation
            mixed = wind + water
            # Un toque de frecuencia baja (60Hz)
            bass = self._generate_tone(60, duration_ms, 0.02)
            mixed = mixed + bass[:len(mixed)]

        elif name == "futurista":
            # Pad sintético con barrido de frecuencia
            t = np.arange(int(self.SAMPLE_RATE * duration_ms / 1000)) / self.SAMPLE_RATE
            pad = np.sin(2 * np.pi * (80 + 20 * np.sin(2 * np.pi * 0.05 * t)) * t).astype(np.float32) * 0.08
            # Arpegios suaves cada 2 segundos
            arp = np.zeros_like(pad)
            for i in range(0, duration_ms, 2000):
                for j, freq in enumerate([220, 330, 440, 330]):
                    pos = int(i * self.SAMPLE_RATE / 1000 + j * self.SAMPLE_RATE * 0.15)
                    if pos + int(0.1 * self.SAMPLE_RATE) < len(arp):
                        tone = self._generate_tone(freq, 100, 0.03)
                        arp[pos:pos+len(tone)] += tone
            mixed = pad + arp
            noise = self._generate_noise(duration_ms, "pink", 0.03)
            mixed = mixed + noise[:len(mixed)]

        elif name == "calido":
            # Bajos cálidos (100Hz) + armónicos suaves
            t = np.arange(int(self.SAMPLE_RATE * duration_ms / 1000)) / self.SAMPLE_RATE
            bass = self._generate_tone(100, duration_ms, 0.1)
            # Acorde mayor suave (C mayor: 261, 329, 392)
            chord = (
                self._generate_tone(261, duration_ms, 0.03) +
                self._generate_tone(329, duration_ms, 0.025) +
                self._generate_tone(392, duration_ms, 0.02)
            )
            noise = self._generate_noise(duration_ms, "brown", 0.04)
            mixed = bass + chord + noise[:len(chord)]
            # Vibrato lento
            vibrato = 0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * t)
            mixed = mixed * vibrato

        elif name == "energetico":
            # Beat suave a 90 BPM
            beat_interval = int(self.SAMPLE_RATE * 60 / 90)
            beat_len = int(0.05 * self.SAMPLE_RATE)
            mixed = np.zeros(int(self.SAMPLE_RATE * duration_ms / 1000), dtype=np.float32)
            for i in range(0, len(mixed), beat_interval):
                kick = self._generate_tone(60, 50, 0.15)
                end = min(i + len(kick), len(mixed))
                mixed[i:end] += kick[:end-i]
            # Hi-hats
            for i in range(beat_interval // 2, len(mixed), beat_interval // 2):
                if i + beat_len < len(mixed):
                    hat = self._generate_noise(30, "white", 0.03)
                    mixed[i:i+len(hat)] += hat
            # Bajo walking
            t = np.arange(len(mixed)) / self.SAMPLE_RATE
            bass_line = self._generate_tone(110, duration_ms, 0.04) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.5 * t))
            mixed = mixed + bass_line[:len(mixed)]

        elif name == "minimal":
            # Pad sintético suave (acorde suspendido)
            t = np.arange(int(self.SAMPLE_RATE * duration_ms / 1000)) / self.SAMPLE_RATE
            pad = (
                self._generate_tone(196, duration_ms, 0.04) +   # G3
                self._generate_tone(247, duration_ms, 0.03) +   # B3
                self._generate_tone(294, duration_ms, 0.02) +   # D4
                self._generate_tone(392, duration_ms, 0.015)    # G4
            )
            # Slow modulation
            mod = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
            mixed = pad * mod
            noise = self._generate_noise(duration_ms, "pink", 0.02)
            mixed = mixed + noise[:len(mixed)]

        else:
            # Fallback: silencio con ruido mínimo
            mixed = self._generate_noise(duration_ms, "pink", 0.01)

        # Normalizar y convertir a PCM16
        max_val = np.max(np.abs(mixed))
        if max_val > 0:
            mixed = mixed / max_val * 0.3
        pcm16 = (mixed * 32767).astype(np.int16).tobytes()
        self._cache[name] = pcm16
        return pcm16


class AudioMixer:
    """
    Mezclador de audio en tiempo real.
    Combina TTS (voz) + Soundscape (fondo) con ducking automático.
    """

    def __init__(self, soundscape: str = "minimal", tts_volume: float = 1.0, bg_volume: float = 0.08):
        self.soundscape_name = soundscape
        self.tts_volume = tts_volume
        self.bg_volume = bg_volume
        self._soundscape_gen = SoundscapeGenerator()
        self._is_speaking = False
        self._duck_factor = 0.3  # Reduce fondo al 30% cuando habla Mystic

    def set_soundscape(self, name: str):
        """Cambia el soundscape activo."""
        if name in SOUNDSCAPES:
            self.soundscape_name = name
            bg_info = SOUNDSCAPES[name]
            self.bg_volume = bg_info["default_volume"]
            logger.info(f"Soundscape changed to: {name}")

    def get_soundscape_list(self) -> list:
        """Lista los soundscapes disponibles."""
        return [
            {"id": k, "name": v["name"], "description": v["description"], "tone": v["tone"]}
            for k, v in SOUNDSCAPES.items()
        ]

    def set_speaking(self, speaking: bool):
        """Activa/desactiva ducking cuando Mystic habla."""
        self._is_speaking = speaking

    def mix_pcm16(self, tts_pcm16: bytes, soundscape_pcm16: bytes, sample_rate: int = 44100) -> bytes:
        """
        Mezcla TTS + Soundscape con ducking automático.
        Ambos deben ser PCM16 mono a la misma sample rate.
        """
        if not tts_pcm16 and not soundscape_pcm16:
            return b""

        # Convertir a float32
        tts_float = np.frombuffer(tts_pcm16, dtype=np.int16).astype(np.float32) / 32768.0 if tts_pcm16 else np.array([], dtype=np.float32)
        bg_float = np.frombuffer(soundscape_pcm16, dtype=np.int16).astype(np.float32) / 32768.0 if soundscape_pcm16 else np.array([], dtype=np.float32)

        # Ajustar volúmenes
        if len(tts_float) > 0:
            tts_float = tts_float * self.tts_volume

        # Ducking: reducir fondo cuando Mystic habla
        bg_volume = self.bg_volume * (self._duck_factor if self._is_speaking else 1.0)

        if len(bg_float) > 0:
            bg_float = bg_float * bg_volume

        # Alinear longitudes (loop soundscape si es más corto que TTS)
        target_len = max(len(tts_float), len(bg_float))
        if len(bg_float) < target_len:
            repeats = (target_len // len(bg_float)) + 1 if len(bg_float) > 0 else 1
            bg_float = np.tile(bg_float, repeats)[:target_len]
        if len(tts_float) < target_len:
            tts_float = np.pad(tts_float, (0, target_len - len(tts_float)))

        # Mezclar
        mixed = tts_float + bg_float[:target_len]

        # Limitar para evitar clipping
        max_val = np.max(np.abs(mixed))
        if max_val > 0.95:
            mixed = mixed / max_val * 0.95

        return (mixed * 32767).astype(np.int16).tobytes()

    async def generate_soundscape_segment(self, duration_ms: int = 5000) -> bytes:
        """Genera un segmento de soundscape para reproducción continua."""
        pcm = self._soundscape_gen.generate_soundscape(self.soundscape_name, duration_ms)
        return pcm

    def mix_with_tts(self, tts_bytes: bytes, soundscape_bytes: bytes, is_speaking: bool = True) -> bytes:
        """Método de conveniencia para mezclar TTS + soundscape."""
        self._is_speaking = is_speaking
        return self.mix_pcm16(tts_bytes, soundscape_bytes)
