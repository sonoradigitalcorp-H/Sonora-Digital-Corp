FROM qdrant/qdrant:v1.7.4

# Instalar wget para health check
RUN apt-get update && apt-get install -y --no-install-recommends wget ca-certificates && rm -rf /var/lib/apt/lists/*

# Configuración optimizada
ENV QDRANT__SERVICE__GRPC_PORT=6334
ENV QDRANT__STORAGE__STORAGE_PATH=/qdrant/storage
ENV QDRANT__STORAGE__SNAPSHOTS_PATH=/qdrant/snapshots

# Puertos
EXPOSE 6333 6334

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD wget --no-verbose --tries=1 -O /dev/null http://localhost:6333/healthz || exit 1

# Volumen para persistencia
VOLUME ["/qdrant/storage", "/qdrant/snapshots"]
