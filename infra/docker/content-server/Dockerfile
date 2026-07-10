FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl postgresql-client \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY products/content-studio/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY products/content-studio/server.py .
COPY products/content-studio/edge-tts-server.py .

EXPOSE 8765 8766

CMD ["sh", "-c", "\
    uvicorn edge-tts-server:app --host 0.0.0.0 --port 8766 & \
    uvicorn server:app --host 0.0.0.0 --port 8765 \
"]
