# Dockerfile para Mystic Voice Realtime
FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para audio
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

EXPOSE 8900

CMD ["uvicorn", "apps.voice_realtime.server:app", "--host", "127.0.0.1", "--port", "8900"]
