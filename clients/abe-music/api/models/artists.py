from pydantic import BaseModel
from typing import Optional, List

class ArtistCreate(BaseModel):
    name: str
    description: str = ""
    streams: int = 0
    label: str = "ABE Music Group"
    image: str = "🎤"

class ArtistUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    streams: Optional[int] = None
    label: Optional[str] = None
    image: Optional[str] = None

class ArtistOut(BaseModel):
    id: str
    name: str
    streams: int
    label: str
    image: str
    monthly_listeners: int = 0
    top_song: str = ""
    top_song_streams: int = 0
    instagram: str = ""
    spotify_url: str = ""
    apple_music_url: str = ""
