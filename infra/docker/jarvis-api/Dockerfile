FROM python:3.11-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl gcc && rm -rf /var/lib/apt/lists/*

# Python deps
COPY apps/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY apps/jarvis/ /app/jarvis/
COPY apps/webui/ /app/webui/
COPY apps/hermes/ /app/hermes/
COPY data/ /app/data/

# Environment
ENV JARVIS_UI_PORT=5174
ENV NEO4J_URI=bolt://sdc-neo4j:7687
ENV NEO4J_USER=neo4j
ENV NEO4J_PASSWORD=sdc2026prod
ENV QDRANT_HOST=sdc-qdrant
ENV QDRANT_PORT=6333
ENV REDIS_HOST=sdc-redis
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD=sdc2026prod
ENV POSTGRES_HOST=sdc-postgres
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=sdc
ENV POSTGRES_PASSWORD=sdc2026prod
ENV POSTGRES_DB=sdc
ENV PYTHONPATH=/app:/app/jarvis

EXPOSE 5174

CMD ["python", "-m", "uvicorn", "webui.fastapp:app", "--host", "0.0.0.0", "--port", "5174"]
