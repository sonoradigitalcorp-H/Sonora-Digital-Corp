# Feature Specification: Servidor MCP

**Feature**: 002-servidor-mcp
**Status**: Active
**Input**: JARVIS necesita un servidor MCP (Model Context Protocol) que exponga herramientas ejecutables por el LLM y el orquestador, con capacidad de expansión mediante skills.

---

## User Stories

### US4 — Ejecutar herramientas desde el LLM
El LLM puede invocar herramientas del sistema (leer archivos, ejecutar comandos, buscar código) durante una conversación para resolver tareas del usuario.

**Prioridad**: P1
**Dependencias**: Ninguna

**Independent Test**: Iniciar el servidor MCP, llamar a la tool `read_file` con una ruta existente, verificar que devuelve el contenido. Testeable sin LLM ni base de datos.

**Acceptance Scenarios**:
1. **Given** un usuario que pide "mostrame el contenido de main.py", **When** el LLM decide usar la herramienta `read_file`, **Then** el contenido del archivo se muestra en la conversación.
2. **Given** un usuario que pide "buscá dónde se define la función `route`", **When** el LLM usa `search_code`, **Then** devuelve los archivos y líneas donde aparece.
3. **Given** un usuario que pide "ejecutá `ls src/`", **When** el LLM usa `execute_command`, **Then** devuelve el listado (si el comando está en whitelist).
4. **Given** un comando no permitido (ej: `rm -rf /`), **When** se intenta ejecutar, **Then** el sistema lo rechaza.

### US5 — Skills expandibles vía MCP
El usuario puede listar skills disponibles, consultar su documentación y ejecutarlas por nombre.

**Prioridad**: P2
**Dependencias**: US4

**Independent Test**: Listar skills vía API, verificar que al menos 8 skills están registradas con nombre y descripción. Testeable con el servidor MCP funcionando.

**Acceptance Scenarios**:
1. **Given** el sistema en funcionamiento, **When** el usuario lista skills, **Then** ve al menos 8 skills con nombre, descripción y parámetros.
2. **Given** una skill `web_fetch`, **When** se ejecuta con una URL, **Then** devuelve el contenido de la página.
3. **Given** una skill que no existe, **When** se intenta ejecutar, **Then** el sistema devuelve un error claro.

---

### Edge Cases

- ¿Qué pasa si el servidor MCP se inicia sin Neo4j/Qdrant disponibles? Las tools que dependen de ellos MUST devolver error claro, no colgar.
- ¿Qué pasa si una tool MCP excede el timeout? El servidor MUST cancelar la operación y devolver timeout error.
- ¿Qué pasa si `execute_command` recibe un comando vacío? MUST rechazar con mensaje de error.
- ¿Qué pasa si `write_file` intenta escribir fuera del directorio del proyecto? MUST rechazar con mensaje de seguridad.
- ¿Qué pasa si `search_semantic` se llama sin embeddings disponibles? MUST fallback a búsqueda por palabras clave.
- ¿Qué pasa si se registran dos tools con el mismo nombre? MUST rechazar el registro duplicado.

---

## Requirements

### Functional Requirements

**FR-010**: El sistema MUST exponer un servidor MCP (FastMCP) con herramientas registrables.
**FR-011**: El sistema MUST implementar como mínimo estas tools MCP: `jarvis_search`, `jarvis_remember`, `jarvis_forget`, `jarvis_status`, `jarvis_execute`, `jarvis_search_semantic`, `jarvis_get_context`, `jarvis_list_skills`, `jarvis_analyze_code`, `jarvis_web_fetch`.
**FR-012**: Las tools MCP MUST usar embeddings reales (768d, Ollama) para búsqueda semántica.
**FR-013**: `jarvis_execute` MUST tener una whitelist de comandos permitidos.
**FR-014**: `jarvis_analyze_code` MUST analizar AST de Python y devolver métricas (funciones, clases, imports, complejidad ciclomática).
**FR-015**: El sistema MUST exponer 10 tools LLM-callables en `src/core/tools.py` con JSON Schema para function calling.
**FR-016**: Las tools LLM MUST incluir: `execute_command`, `read_file`, `write_file`, `list_files`, `run_tests`, `search_code`, `docker_build`, `docker_deploy`, `search_semantic`, `rag_store`.
**FR-017**: Las tools LLM MUST validar que las rutas de archivo estén dentro del directorio del proyecto.
**FR-018**: El SkillAgent (orquestador) MUST exponer catálogo de skills, ejecución por nombre y documentación.

### Key Entities

- **MCP Tool**: Función registrada en el servidor MCP con nombre, descripción y parámetros.
- **LLM Tool**: Función con JSON Schema expuesta al LLM para function calling.
- **Skill**: Tool MCP envuelta con metadata adicional (categoría, parámetros, documentación).
- **Whitelist**: Lista de comandos shell permitidos para `execute_command`/`jarvis_execute`.

---

## Success Criteria

- **SC-010**: Las 10 tools MCP responden sin errores cuando los servicios (Neo4j, Qdrant) están disponibles.
- **SC-011**: Las 10 tools LLM en `tools.py` tienen JSON Schema y executor function.
- **SC-012**: `execute_command` rechaza comandos fuera de whitelist con mensaje de error claro.
- **SC-013**: `write_file` rechaza escrituras fuera del directorio del proyecto.
- **SC-014**: `jarvis_analyze_code` devuelve métricas válidas para cualquier archivo Python.

---

## Assumptions

- FastMCP está disponible como dependencia Python.
- Neo4j y Qdrant pueden no estar disponibles; las tools degradan gracefulmente.
- El servidor MCP corre en Docker o localmente en puerto 8000.
