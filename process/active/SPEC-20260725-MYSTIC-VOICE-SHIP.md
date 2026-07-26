# SPEC — Mystic Voice Ship: Asistente Personal Listo para Producción

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260725-MYSTIC-VOICE-SHIP` |
| **Fecha** | 2026-07-25 |
| **Autor** | Mystic — Sonora Digital Corp |
| **Tier** | 2 (Capability) |
| **Estado** | activo |
| **Score requerido** | ≥60 |

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

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | **System Monitor**: Endpoint `/api/system` que devuelve CPU%, RAM, disk, uptime, procesos top. Intent "cómo está el sistema" en `intent_router.py` que llama al monitor. | P0 |
| FR2 | **Persistent Memory**: SQLite local `state/mystic_sessions.db` con tabla `sessions` (session_id, history JSON, context, created_at, updated_at). Carga historial al reconectar WebSocket. | P0 |
| FR3 | **PWA Support**: `manifest.json` + service worker para instalar como app de escritorio con ícono en el dock/barra de tareas. | P1 |
| FR4 | **Auto Wake Word**: Al cargar la página, el wake word se activa automáticamente (sin tener que presionar 🔮). Onboarding tooltip explicativo. | P1 |
| FR5 | **Proactive Monitor**: Cada 30s el servidor checkea CPU/RAM. Si CPU > 80% o RAM > 90%, envía notificación al frontend como sugerencia proactiva. | P2 |

---

## 4. Success Criteria

- [ ] `curl http://127.0.0.1:8900/api/system` → `{"cpu": 23.5, "ram_percent": 38.2, "disk_percent": 84, "uptime_days": 12.3, "top_processes": [...]}`
- [ ] Decir "Mystic, ¿cómo está el sistema?" → el intent router clasifica como `check_system` → llama al monitor → responde por voz "CPU al 23%, RAM al 38%, disco al 84% — todo estable"
- [ ] Recargar la página WebSocket → el historial de conversación se restaura desde SQLite
- [ ] `manifest.json` + service worker registrado → Chrome muestra "Instalar Mystic Voice" en la barra de direcciones
- [ ] Al cargar la página, el 🔮 aparece activo automáticamente sin interacción del usuario
- [ ] `ruff check apps/voice-realtime/` → 0 errores
- [ ] `pytest tests/voice_realtime/ -q --tb=short` → 0 failures

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260725-MYSTIC-VOICE-SHIP.feature`

### Resumen

**Happy Path:**
1. Usuario pregunta "¿cómo está el sistema?" → Mystic lee CPU/RAM/disk por voz
2. Usuario dice "monitorea el servidor" → se activa proactive monitor cada 30s
3. Usuario recarga la página → el historial de conversación se restaura

**Edge Cases:**
1. Servidor sin `psutil` → fallback elegante, responde "no tengo acceso al monitor del sistema"
2. Memoria SQLite corrupta → recrea la base de datos desde cero, loggea warning
3. Service worker no soportado (Safari) → la app funciona sin PWA, solo sin instalación

---

## 6. Edge Cases

| EC# | Descripción | Manejo |
|-----|-------------|--------|
| EC1 | `psutil` no instalado → monitor responde `{"error": "psutil not available"}` y el intent router da fallback "No tengo acceso al monitor del sistema" |
| EC2 | SQLite DB corrupta → `open()` con `isolation_level=None`, si falla borra y recrea |
| EC3 | Service worker no soportado → app funciona sin PWA, solo se pierde instalación |
| EC4 | Wake word no disponible (sin micrófono) → el botón 🔮 se muestra desactivado con tooltip "Conecta un micrófono" |

---

## 7. Technical Approach

```
Archivos a crear:
  apps/voice-realtime/pipeline/monitor.py   ← psutil wrapper, endpoint /api/system
  apps/voice-realtime/pipeline/session_db.py ← SQLite persistence
  apps/voice-realtime/frontend/manifest.json ← PWA manifest
  apps/voice-realtime/frontend/sw.js        ← Service worker

Archivos a modificar:
  apps/voice-realtime/server.py             ← + /api/system, + session DB load/save, + proactive monitor
  apps/voice-realtime/intent_router.py      ← + "check_system" intent pattern
  apps/voice-realtime/frontend/mystic_voice.html ← + auto wake word, + PWA registration
```

### Pipeline expandido:

```
[Wake Word] → VAD → Whisper STT → Intent Router ─┬─ talk → LLM → TTS
                                                   ├─ navigate → Browser Actions → TTS
                                                   ├─ check_system → System Monitor → TTS
                                                   └─ search → Web Search → Browser → TTS

Memoria:
  SQLite (state/mystic_sessions.db) ←→ Session cache (dict) ←→ Engram API (MCP)
  Cada interacción: user input + response → SQLite + Engram
  Al conectar WebSocket: session_id → SQLite load → restore history
```

### SQLite Schema:

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,              -- session_id uuid
    history TEXT NOT NULL DEFAULT '[]', -- JSON array de mensajes
    context TEXT,                      -- JSON con metadata (tone, soundscape, etc.)
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,                -- 'user' | 'assistant' | 'system'
    content TEXT NOT NULL,
    intent_id TEXT,
    latency_ms INTEGER,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

---

## 8. Dependencies

| Dependencia | Propósito | Ya instalado |
|-------------|-----------|-------------|
| `psutil` ≥5.9 | CPU, RAM, disk monitoring | ❌ Verificar |
| `sqlite3` (stdlib) | Persistencia local | ✅ |
| Service Worker API | PWA offline | ✅ (browser) |
| Web Manifest | PWA install | ✅ (browser) |

---

## 9. Events to Emit

| Evento | Trigger |
|--------|--------|
| `mystic:system:status` | Usuario pregunta "cómo está el sistema" |
| `mystic:session:restored` | Historial de sesión cargado desde SQLite |
| `mystic:proactive:alert` | CPU > 80% o RAM > 90% detectado |
| `mystic:pwa:installed` | Usuario instala la PWA |

---

## 10. Kill Criteria

- `psutil` no puede instalarse o da errores en Python 3.13+ → el monitor se omite, el resto del asistente funciona sin él
- SQLite persistencia causa lentitud en conexión WebSocket (>500ms) → se desactiva la carga de historial, solo guarda
- PWA no funciona en Chrome headless → se omite, la app web sigue funcionando normalmente

---

## 11. Scale Criteria

- Founder usa Mystic Voice >3h/día → agregar telemetría de uso + dashboard de interacciones
- >10 sesiones activas/día → migrar SQLite a Postgres para consultas analíticas
- >100 interacciones/día → cachear respuestas frecuentes en Redis para reducir latencia TTS
