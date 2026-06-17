# Feature Specification: Memoria Persistente

**Feature**: 001-memoria-persistente
**Status**: Active
**Input**: JARVIS necesita memoria a largo plazo que combine búsqueda por grafos (Neo4j), búsqueda semántica (Qdrant), y gestión de sesiones de conversación.

---

## User Stories

### US1 — Almacenar y recuperar recuerdos
El usuario interactúa con JARVIS y este recuerda información de sesiones anteriores, tanto por relaciones explícitas (grafos) como por similitud semántica (vectores).

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Guardar un recuerdo "color favorito es azul" y luego preguntar "¿cuál es mi color favorito?" — debe responder "azul". Testeable sin red ni servicios externos con fallback a memoria.

**Acceptance Scenarios**:
1. **Given** un usuario que dice "acordate que mi color favorito es azul", **When** luego pregunta "¿cuál es mi color favorito?", **Then** JARVIS responde "azul".
2. **Given** información almacenada en la base vectorial, **When** el usuario hace una pregunta semánticamente similar, **Then** JARVIS encuentra el contenido relevante aunque las palabras exactas no coincidan.
3. **Given** que Neo4j no está disponible, **When** el usuario guarda o recupera un recuerdo, **Then** el sistema usa almacenamiento en memoria como fallback y no falla.

### US2 — Vincular conceptos en un grafo de conocimiento
El usuario habla de temas y JARVIS construye un grafo que relaciona conceptos, permitiendo navegación por asociaciones.

**Prioridad**: P2
**Dependencias**: US1

**Independent Test**: Tras almacenar conceptos "Python" y "Django", consultar el grafo vía API y verificar que ambos nodos existen y están relacionados. Testeable con Neo4j disponible.

**Acceptance Scenarios**:
1. **Given** conversaciones sobre "Python" y "Django", **When** se consulta el grafo, **Then** ambos conceptos aparecen relacionados.
2. **Given** un concepto en el grafo, **When** el usuario pregunta por temas relacionados, **Then** JARVIS devuelve los nodos conectados.

### US3 — Gestionar sesiones de conversación
El usuario crea, busca, organiza y exporta sus sesiones de conversación.

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Crear una sesión vía API, enviar un mensaje, buscar la sesión por texto, exportarla a JSON y verificar que el contenido es correcto. Testeable con o sin Neo4j (fallback a memoria).

**Acceptance Scenarios**:
1. **Given** una sesión activa, **When** el usuario envía un mensaje, **Then** se guarda automáticamente en la sesión actual.
2. **Given** varias sesiones, **When** el usuario busca por texto, **Then** encuentra sesiones por contenido.
3. **Given** una sesión, **When** el usuario la archiva, **Then** desaparece de la vista principal pero sigue accesible.
4. **Given** una sesión, **When** el usuario la exporta, **Then** obtiene un archivo JSON o Markdown con todo el contenido.

---

### Edge Cases

- ¿Qué pasa si Neo4j no está disponible? El sistema MUST degradar a almacenamiento en memoria sin perder funcionalidad.
- ¿Qué pasa si Qdrant no está disponible? La búsqueda semántica MUST fallback a búsqueda exacta en Neo4j.
- ¿Qué pasa si Ollama no corre? Los embeddings MUST fallback a embeddings simples (TF-IDF o similares).
- ¿Qué pasa si la colección Qdrant no existe? El sistema MUST crearla automáticamente al iniciar.
- ¿Qué pasa si se guarda un recuerdo duplicado? El sistema MUST actualizar el existente en lugar de crear duplicados.
- ¿Qué pasa si el contenido es muy largo (> 10K caracteres)? El sistema MUST truncar o chunkear el texto antes de almacenar.

---

## Requirements

### Functional Requirements

**FR-001**: El sistema MUST almacenar mensajes de conversación en Neo4j como nodos `Session` y `Message` con timestamps.
**FR-002**: El sistema MUST generar embeddings vectoriales (768d) usando Ollama `nomic-embed-text` para búsqueda semántica.
**FR-003**: El sistema MUST almacenar embeddings en Qdrant con colecciones separadas por tipo (`conversations`, `documents`, `tasks`, `jarvis_knowledge`).
**FR-004**: El sistema MUST buscar tanto por grafo (Neo4j) como por vectores (Qdrant) y combinar resultados.
**FR-005**: El sistema MUST degradar gracefulmente si Neo4j o Qdrant no están disponibles, usando almacenamiento en memoria.
**FR-006**: El sistema MUST exponer APIs REST para CRUD de sesiones: listar, crear, obtener, actualizar, eliminar, pin/unpin, archive/unarchive, duplicar, exportar.
**FR-007**: El sistema MUST exponer búsqueda full-text sobre sesiones.
**FR-008**: El MemoryAgent (orquestador) MUST poder guardar, recordar, olvidar y listar recuerdos mediante Neo4j con fallback in-memory.

### Key Entities

- **Session**: Conversación con id, título, pinned, project, tags, archived, timestamps.
- **Message**: Mensaje individual con role (user/assistant), contenido, timestamp, metadata.
- **Memory**: Par clave-valor con timestamp (Neo4j label `Memory`).
- **Embedding**: Vector 768d almacenado en colecciones Qdrant con payload de texto y metadata.
- **Graph node**: Concepto o entidad en Neo4j con relaciones a otros nodos.

---

## Success Criteria

- **SC-001**: Almacenar y recuperar un recuerdo funciona con y sin Neo4j disponible.
- **SC-002**: Búsqueda semántica devuelve resultados relevantes (score > 0.5) para queries similares al contenido almacenado.
- **SC-003**: Sesiones CRUD + búsqueda responden en < 200ms.
- **SC-004**: Exportación JSON y Markdown contienen el contenido completo de la sesión.
- **SC-005**: 0 errores cuando Neo4j o Qdrant no están disponibles (fallback a memoria).

---

## Assumptions

- Neo4j corre localmente o en Docker accesible via bolt.
- Qdrant corre localmente o en Docker accesible via HTTP.
- Ollama con modelo `nomic-embed-text` está disponible para embeddings.
- Las colecciones Qdrant ya existen con dimensión 768 (creadas por `init_collections.py`).
