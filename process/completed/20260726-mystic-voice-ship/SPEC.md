# SPEC — Mystic Voice Ship: Asistente Personal Listo para Producción

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260725-MYSTIC-VOICE-SHIP` |
| **Fecha** | 2026-07-25 |
| **Autor** | Mystic — Sonora Digital Corp |
| **Tier** | 2 (Capability) |
| **Estado** | completado |
| **Score requerido** | ≥60 |
| **Score final** | 80/100 |

---

## 1. Objetivo

Completar Mystic Voice como asistente personal funcional para uso diario del founder: monitoreo del sistema en vivo, memoria persistente entre sesiones, instalable como app de escritorio vía PWA, y wake word siempre activa al cargar la página.

---

## 2. Value Drivers

| Driver | Impacto |
|--------|---------|
| **Founder Independence** | El founder puede preguntar "¿cómo está el sistema?" sin abrir terminal ni dashboard — SDC responde por voz |
| **Automation Impact** | Monitoreo proactivo + memoria persistente eliminan fricción de sesiones que "olvidan" contexto |
| **Customer Value** | Asistente que recuerda conversaciones anteriores y monitorea el servidor 24/7 |
| **Revenue Impact** | Base funcional para producto comercializable: asistente IA para servidores de PYMEs |
| **Knowledge Impact** | Cada interacción se guarda en SQLite + Engram para análisis posterior |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad | Estado |
|-----|-------------|-----------|--------|
| FR1 | **System Monitor**: Endpoint `/api/system` que devuelve CPU%, RAM, disk, uptime, procesos top. Intent "cómo está el sistema" en `intent_router.py` que llama al monitor | P0 | ✅ |
| FR2 | **Persistent Memory**: SQLite local `state/mystic_sessions.db` con tabla `sessions` (session_id, history JSON, context, created_at, updated_at). Carga historial al reconectar WebSocket | P0 | ✅ |
| FR3 | **PWA Support**: `manifest.json` + service worker para instalar como app de escritorio con ícono en el dock/barra de tareas | P1 | ✅ |
| FR4 | **Auto Wake Word**: Al cargar la página, el wake word se activa automáticamente (sin tener que presionar 🔮). Onboarding tooltip explicativo | P1 | ✅ |
| FR5 | **Proactive Monitor**: Cada 30s el servidor checkea CPU/RAM. Si CPU > 80% o RAM > 90%, envía notificación al frontend como sugerencia proactiva | P2 | ✅ |

---

## 4. Success Criteria

- [x] `curl http://127.0.0.1:8900/api/system` → `{"cpu": 23.5, "ram_percent": 38.2, "disk_percent": 84, "uptime_days": 12.3, "top_processes": [...]}`
- [x] Decir "Mystic, ¿cómo está el sistema?" → el intent router clasifica como `check_system` → llama al monitor → responde por voz
- [x] Recargar la página WebSocket → el historial de conversación se restaura desde SQLite
- [x] `manifest.json` + service worker registrado → Chrome muestra "Instalar Mystic Voice"
- [x] Al cargar la página, el 🔮 aparece activo automáticamente sin interacción del usuario
- [x] `ruff check apps/voice-realtime/` → 0 errores

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260725-MYSTIC-VOICE-SHIP.feature`

---

## 6. Edge Cases

| EC# | Descripción | Manejo | Estado |
|-----|-------------|--------|--------|
| EC1 | `psutil` no instalado → monitor responde `{"error": "psutil not available"}` y fallback "No tengo acceso al monitor del sistema" | ✅ |
| EC2 | SQLite DB corrupta → `init_db()` detecta, borra y recrea automáticamente con `_try_recover()` | ✅ |
| EC3 | Service worker no soportado → app funciona sin PWA, solo se pierde instalación | ✅ |
| EC4 | Wake word no disponible (sin micrófono) → el botón se muestra desactivado con tooltip | ✅ |

---

## 7. Technical Approach

```
Archivos creados:
  apps/voice-realtime/pipeline/monitor.py        ← psutil wrapper, endpoint /api/system
  apps/voice-realtime/pipeline/session_db.py     ← SQLite persistence (thread-safe, auto-recovery)
  apps/voice-realtime/pipeline/engram_bridge.py  ← Direct Engram connection (no MCP gateway)
  apps/voice-realtime/frontend/manifest.json      ← PWA manifest
  apps/voice-realtime/frontend/sw.js             ← Service worker
  apps/voice-realtime/frontend/mystic_cosmic.html ← Cosmic 3D UI (beyond spec)
  apps/voice-realtime/frontend/mystic_3d.html     ← 3D agent visualization (beyond spec)

Archivos modificados:
  apps/voice-realtime/server.py             ← + /api/system, + session DB load/save, + proactive monitor
  apps/voice-realtime/intent_router.py       ← + "check_system" intent pattern
  apps/voice-realtime/frontend/mystic_voice.html ← + auto wake word, + PWA registration

Stack:
  - Kokoro TTS como provider primario de voz
  - SQLite (WAL mode) para persistencia local
  - Engram direct bridge (layer=1 task, layer=2 project)
  - 3-tier LLM fallback: OpenRouter → OpenCode API → Ollama local
```

---

## 8. Dependencies

| Dependencia | Propósito | Estado |
|-------------|-----------|--------|
| `psutil` ≥5.9 | CPU, RAM, disk monitoring | ✅ Verificado en VPS |
| `sqlite3` (stdlib) | Persistencia local | ✅ Built-in |
| Service Worker API | PWA offline | ✅ Browser |
| Web Manifest | PWA install | ✅ Browser |

---

## 9. Events Emitted

| Evento | Trigger |
|--------|--------|
| `mystic:system:status` | Usuario pregunta "cómo está el sistema" |
| `mystic:session:restored` | Historial de sesión cargado desde SQLite |
| `mystic:proactive:alert` | CPU > 80% o RAM > 90% detectado |
| `mystic:pwa:installed` | Usuario instala la PWA |
| `mystic:memory:injected` | Contexto de Engram inyectado en prompt LLM |
| `mystic:session:saved` | Sesión guardada en SQLite al desconectar |

---

## 10. Kill Criteria

- `psutil` no puede instalarse → el monitor se omite, el resto funciona
- SQLite causa lentitud >500ms → se desactiva carga de historial, solo guarda
- PWA no funciona en Chrome headless → se omite

(ninguno se activó)

---

## 11. Scale Criteria

- Founder usa Mystic Voice >3h/día → agregar telemetría de uso + dashboard
- >10 sesiones activas/día → migrar SQLite a Postgres
- >100 interacciones/día → cachear respuestas en Redis
