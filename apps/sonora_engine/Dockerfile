FROM python:3.12-slim

WORKDIR /app

COPY apps/sonora_engine/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/sonora_engine/ .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5100"]
