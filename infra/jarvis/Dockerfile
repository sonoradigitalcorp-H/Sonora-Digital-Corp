FROM python:3.12-slim AS base

# Allow PIP_ROOT_USER_ACTION for container builds
ENV PIP_ROOT_USER_ACTION=ignore

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY infra/docker/jarvis/requirements-docker.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/ /app/apps/
COPY scripts/ /app/scripts/
COPY process/ /app/process/
RUN mkdir -p /app/state/logs
COPY .env /app/.env
COPY .gitignore /app/
COPY opencode.json /app/
COPY pyproject.toml /app/pyproject.toml

ENV PYTHONPATH=/app:/app/apps/jarvis
ENV JARVIS_UI_PORT=5174

FROM base AS test
COPY tests/ /app/tests/
COPY pyproject.toml /app/
COPY AGENTS.md /app/
COPY README.md /app/
COPY CLAUDE.md /app/
COPY requirements.txt /app/
RUN pip install --no-cache-dir pytest pytest-asyncio pytest-cov ruff
RUN python3 -m pytest tests/unit/ -q --no-header 2>&1 | tail -5

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:5174/api/enterprise-score', timeout=5)" || exit 1

FROM base AS jarvis-core
CMD ["python3", "apps/jarvis/main.py"]

FROM base AS jarvis-webui
EXPOSE 5174
CMD ["python3", "-m", "uvicorn", "apps.webui.fastapp:app", "--host", "0.0.0.0", "--port", "5174"]
