FROM python:3.14-slim
WORKDIR /app
COPY . /app/products/mystik
RUN mkdir -p /app/products && touch /app/products/__init__.py
RUN pip install --no-cache-dir fastapi uvicorn httpx pydantic-settings chromadb edge-tts redis slowapi
ENV PYTHONPATH=/app
CMD ["uvicorn", "products.mystik.main:app", "--host", "0.0.0.0", "--port", "5200"]
