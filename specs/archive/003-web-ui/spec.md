# Feature Specification: Web UI

**Feature**: 003-web-ui
**Status**: Active
**Input**: JARVIS necesita una interfaz web moderna con panel de tres columnas, streaming de respuestas en tiempo real, y exploración del workspace del proyecto.

---

## User Stories

### US6 — Chat con streaming en tiempo real
El usuario chatea con JARVIS y ve las respuestas token por token mientras se generan, con indicadores visuales de actividad.

**Prioridad**: P1
**Dependencias**: 001-memoria-persistente (sesiones)

**Independent Test**: Abrir la web UI en un navegador, enviar un mensaje de prueba, verificar que los tokens aparecen en tiempo real. Testeable contra el backend FastAPI funcionando.

**Acceptance Scenarios**:
1. **Given** un mensaje enviado por el usuario, **When** JARVIS genera la respuesta, **Then** los tokens aparecen en tiempo real en el chat.
2. **Given** que JARVIS está usando una herramienta, **When** se ejecuta, **Then** se muestra un indicador visual de qué tool está usando.
3. **Given** un streaming en curso, **When** el usuario envía un nuevo mensaje, **Then** el streaming anterior se cancela y empieza el nuevo.
4. **Given** la conexión se pierde durante un streaming, **When** se recupera, **Then** el chat se reconecta automáticamente.

### US7 — Explorar archivos del proyecto
El usuario navega el sistema de archivos del proyecto desde la web UI, ve el contenido de archivos y el estado git.

**Prioridad**: P2
**Dependencias**: Ninguna

**Independent Test**: Cargar la UI, abrir el panel workspace, navegar a un directorio y hacer clic en un archivo — debe mostrar el contenido con resaltado de sintaxis. Testeable sin backend de IA.

**Acceptance Scenarios**:
1. **Given** la UI cargada, **When** el usuario abre el panel workspace, **Then** ve la estructura de directorios del proyecto.
2. **Given** un archivo seleccionado, **When** el usuario hace clic, **Then** se muestra el contenido con resaltado de sintaxis.
3. **Given** cambios sin commit, **When** el usuario mira el workspace, **Then** ve el estado git (archivos modificados).

### US8 — Gestionar sesiones desde la UI
El usuario ve, busca, filtra y organiza sus sesiones de conversación directamente desde la interfaz.

**Prioridad**: P1
**Dependencias**: 001-memoria-persistente (US3)

**Independent Test**: Crear varias sesiones vía API, cargar la UI, verificar que aparecen listadas, filtrarlas, archivarlas y exportarlas. Testeable con API REST funcionando.

**Acceptance Scenarios**:
1. **Given** la UI, **When** el usuario carga la página, **Then** ve la lista de sesiones en el panel lateral.
2. **Given** la lista de sesiones, **When** el usuario escribe en el buscador, **Then** las sesiones se filtran por texto.
3. **Given** una sesión, **When** el usuario hace clic derecho, **Then** ve opciones: pin, archive, duplicate, export, delete.
4. **Given** la UI en móvil, **When** el usuario la abre, **Then** los paneles se apilan verticalmente.

---

### Edge Cases

- ¿Qué pasa si el backend SSE se cae durante un streaming? El frontend MUST mostrar error y botón de reconexión.
- ¿Qué pasa si el navegador no soporta SSE? MUST mostrar mensaje de compatibilidad.
- ¿Qué pasa si la pantalla es muy pequeña (< 480px)? Los paneles MUST apilarse sin romper el layout.
- ¿Qué pasa si se abre la UI sin backend disponible? MUST mostrar pantalla de error con mensaje claro.
- ¿Qué pasa si un archivo del workspace es muy grande (> 1MB)? MUST truncar la vista previa con advertencia.
- ¿Qué pasa si hay 100+ sesiones? El panel lateral MUST virtualizar o paginar la lista.

---

## Requirements

### Functional Requirements

**FR-020**: El sistema MUST servir una web UI con layout de tres paneles: sidebar (sesiones), chat (conversación), workspace (archivos).
**FR-021**: El sistema MUST transmitir respuestas del LLM vía SSE (Server-Sent Events) con eventos: `token`, `tool`, `search`, `done`, `error`.
**FR-022**: El frontend MUST reconectarse automáticamente al SSE si la conexión se pierde (máx 3s de espera).
**FR-023**: El frontend MUST renderizar markdown en los mensajes (código, tablas, listas).
**FR-024**: El sistema MUST exponer API REST para explorar archivos del proyecto (listar directorios, leer archivos, git status).
**FR-025**: El sistema MUST exponer API REST para comandos slash (`/help`, `/clear`, `/status`, `/skills`, `/voice`, `/theme`).
**FR-026**: La UI MUST ser responsive: en pantallas < 768px los paneles se apilan verticalmente.

### Key Entities

- **SSE Event**: Mensaje del servidor al cliente con tipo (`token`, `tool`, `done`, `error`) y datos JSON.
- **Slash Command**: Comando prefijado con `/` que ejecuta una acción predefinida.
- **Workspace**: Panel de exploración de archivos del proyecto.

---

## Success Criteria

- **SC-020**: SSE streaming muestra tokens en < 500ms desde que el servidor los genera.
- **SC-021**: Reconexión automática funciona en < 5s ante caída de conexión.
- **SC-022**: Markdown se renderiza correctamente (código con syntax highlighting, tablas, listas).
- **SC-023**: File browser muestra correctamente directorios y archivos del proyecto.
- **SC-024**: Git status muestra archivos modificados vs committed.

---

## Assumptions

- El frontend es JavaScript vanilla (sin framework), servido desde FastAPI.
- SSE es el mecanismo de streaming (no WebSocket, no Socket.IO).
- El tema visual es cyberpunk con CSS variables personalizables.
