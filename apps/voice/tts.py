import os
from openai import OpenAI


_client = None


def speak(text: str, voice: str = "alloy") -> str:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = _client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
    )
    path = f"/tmp/tts-{abs(hash(text))}.mp3"
    response.stream_to_file(path)
    return path
