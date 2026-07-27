FROM python:3.11-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy API
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ /app/api/
COPY frontend/ /app/frontend/

# Expose port
EXPOSE 8701

# Run
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8701"]
