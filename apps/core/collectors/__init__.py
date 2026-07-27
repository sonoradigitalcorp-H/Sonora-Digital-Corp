"""Collectors for each DSP/platform.

Each module exposes:
  fetch_artist(identifier) -> dict | None
  fetch_artist_with_fallback(identifier) -> dict
"""
from . import apple_music as apple_music
from . import deezer as deezer
from . import instagram as instagram
from . import spotify as spotify
from . import tiktok as tiktok
from . import wikipedia as wikipedia
from . import youtube as youtube
