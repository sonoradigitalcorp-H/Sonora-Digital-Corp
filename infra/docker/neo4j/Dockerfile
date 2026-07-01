FROM neo4j:5.19-community

# Plugins para Graph RAG
ENV NEO4JLAB_PLUGINS='["apoc"]'

# Configuración de memoria (usando naming nuevo de Neo4j 5.x)
# Los valores en docker-compose.yml tienen prioridad
ENV NEO4J_server_memory_heap_max__size=256M
ENV NEO4J_server_memory_pagecache_size=128M

# Habilitar APOC procedures
ENV NEO4J_apoc_export_file_enabled=true
ENV NEO4J_apoc_import_file_enabled=true
ENV NEO4J_apoc_import_file_use__neo4j__config=true

# Copiar scripts de inicialización
COPY init.cypher /init.cypher
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Puertos
EXPOSE 7474 7687

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:7474 || exit 1

# Volumen para persistencia
VOLUME ["/data"]

ENTRYPOINT ["/docker-entrypoint.sh"]
