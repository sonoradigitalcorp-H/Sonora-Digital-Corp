"""Collectors for each DSP/platform.

Each module exposes:
  fetch_artist(identifier) -> dict | None
  fetch_artist_with_fallback(identifier) -> dict
"""
from . import apple_music, deezer, instagram, spotify, tiktok, youtube
