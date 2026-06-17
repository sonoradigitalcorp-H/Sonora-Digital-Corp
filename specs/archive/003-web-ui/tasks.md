# Tasks: Web UI

---

## US6 — Chat con streaming (P1)

- [x] SSE endpoint en FastAPI: GET `/api/chat/{id}/stream`
- [x] EventSource consumer en frontend (`app.js`)
- [x] Streaming de tokens en tiempo real
- [x] Eventos: token, tool, search, done, error
- [x] Reconexión automática (3s)
- [x] Renderizado incremental de tokens (markdown)
- [x] Auto-scroll durante streaming
- [x] Cancelar request si usuario envía nuevo mensaje
- [x] Indicador visual de streaming
- [x] Integración con AgentOrchestrator
- [x] Headers SSE correctos (Cache-Control, Connection, X-Accel-Buffering)
- [x] Token counting en tiempo real con tiktoken

## US7 — Explorar archivos (P2)

- [x] API `/api/files` (listar directorios, leer archivos)
- [x] API `/api/files/git` (git status via subprocess)
- [x] File browser UI con breadcrumb navigation
- [x] Preview de contenido de archivos
- [x] Git status indicator visible en workspace panel
- [x] Syntax highlighting en preview de código

## US8 — Gestionar sesiones desde UI (P1)

- [x] Sidebar con lista de sesiones (CRUD desde UI)
- [x] Buscador de sesiones con debounce
- [x] Right-click context menu (pin, archive, duplicate, export, delete)
- [x] Filtros por tags/project
- [x] Header con estado del sistema (modelo, conexión, latencia)
- [x] Footer con token counter
- [x] Periodic system status polling (30s)
- [x] Responsive breakpoints (@768px stack vertical)
- [x] Drag & drop para reordenar sesiones

---

**Completado**: 28 tareas | **Pendiente**: 0 tareas
