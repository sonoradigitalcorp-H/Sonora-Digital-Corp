---
name: index-knowledge
description: >
  Indexa documentos del cliente en Qdrant (vectores) y Neo4j (grafos).
  Toma archivos de clients/<nombre>/knowledge/, los chunkea,
  genera embeddings, y los almacena para búsqueda RAG.
license: MIT
compatibility: opencode
metadata:
  domain: knowledge
  capabilities: rag, embeddings, search
---

## Qué hace

Procesa documentos de un cliente y los indexa para búsqueda semántica:
- Lee archivos de clients/<nombre>/knowledge/
- Soporta: PDF, Word, Excel, Markdown, TXT
- Chunking inteligente por tipo de documento
- Genera embeddings (OpenAI/text-embedding-3-small o local)
- Almacena en Qdrant (vectores) y Neo4j (metadatos + relaciones)

## Cuándo usarlo

- Cuando un cliente sube nuevos documentos
- Cuando se configura un cliente nuevo
- Cuando se actualiza la knowledge base

## Pasos

1. **Identificar documentos nuevos**
   - Escanea clients/<nombre>/knowledge/
   - Compara con últimos indexados (revisa Neo4j)

2. **Procesar cada documento**
   - Extraer texto (PDF, Word, etc.)
   - Chunkear en segmentos de ~500 tokens con overlap de 50
   - Generar embedding para cada chunk

3. **Indexar en Qdrant**
   - Crear colleción si no existe
   - Insertar puntos con: vector + metadata (doc_id, chunk_idx, source)

4. **Indexar en Neo4j**
   - Crear nodo Documento con metadatos
   - Crear relaciones entre documentos relacionados

5. **Verificar**
   - Hacer una búsqueda de prueba
   - Confirmar que los resultados son relevantes

## Referencias

- Qdrant MCP: mcp/qdrant (config en opencode.json)
- Neo4j MCP: mcp/neo4j (config en opencode.json)
- Documentos del cliente: clients/<nombre>/knowledge/
