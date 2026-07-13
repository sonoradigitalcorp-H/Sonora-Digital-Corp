FROM python:3.12-slim

WORKDIR /app

COPY apps/sonora_bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/sonora_bot/ .
COPY apps/sonora_engine/ /app/sonora_engine/

CMD ["python", "-m", "main"]
