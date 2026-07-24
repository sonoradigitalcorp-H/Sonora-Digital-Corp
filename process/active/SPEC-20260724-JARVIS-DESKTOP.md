# SPEC — Jarvis Desktop: Asistente Personal de Escritorio para SDC

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260724-JARVIS-DESKTOP` |
| **Fecha** | 2026-07-24 |
| **Autor** | Mystic — Sonora Digital Corp |
| **Tier** | 3 (Capability/Platform) |
| **Estado** | borrador |
| **Score requerido** | ≥75 |

---

## 1. Objetivo

Construir un agente de escritorio nativo (Python) always-on con voz en tiempo real, control de escritorio, monitoreo del sistema y proactividad contextual, conectado al ecosistema SDC vía Hermes Gateway para eliminar la dependencia del VPS como único punto de interacción.

---

## 2. Value Driver

| Driver | Impacto |
|--------|---------|
| **Founder Independence** | El founder interactúa con SDC desde su escritorio sin depender del VPS o Telegram como único canal — SDC llega a donde el founder está |
| **Automation Impact** | Proactividad contextual: el sistema actúa antes de que el usuario pida (monitoreo, recordatorios, sugerencias) basado en estado del escritorio |
| **Revenue Impact** | Nuevo producto comercializable: Jarvis Desktop como SKU para clientes enterprise que quieran un asistente local always-on conectado a su VPS |
| **Scalability** | Multi-laptop: misma codebase corre en N máquinas, cada una con su propia identidad y conexión al mismo ecosistema SDC |
| **Knowledge Impact** | La sesión de escritorio del founder se vuelve fuente de datos: qué apps usa, cuándo trabaja, qué patrones sigue — todo alimenta Engram |
| **Reliability** | El VPS puede caer y el asistente local sigue funcionando (offline mode) con memoria local SQLite |
| **Reusability** | Los módulos de acción (screen capture, voz, monitoreo, notificaciones) son skills reutilizables que cualquier otro agente SDC puede invocar vía MCP |
| **Customer Value** | El usuario final tiene un asistente que no requiere abrir un navegador — está siempre ahí, escucha, observa y actúa |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| FR1 | **Always-on voice loop**: STT (micrófono local) → procesar (local o vía Hermes API) → TTS (altavoz local) con wake word "Jarvis" y push-to-talk opcional | P0 |
| FR2 | **Screen capture & OCR**: Captura de pantalla periódica + OCR (Tesseract) + detección de ventana activa para inferir contexto del usuario | P0 |
| FR3 | **Control de escritorio**: Mouse (click, mover, arrastrar), teclado (escribir, atajos), ventanas (abrir, cerrar, enfocar, mover/redimensionar) vía `pyautogui` + `wmctrl`/`xdotool` | P0 |
| FR4 | **Monitoreo del sistema**: CPU (%) , RAM (used/total), GPU (nvidia-smi o fallback), temperatura, procesos top, batería, disk usage — cada 30s con alertas configurables por umbral | P0 |
| FR5 | **Proactividad contextual**: Background monitor detecta estados (CPU alta, batería baja, hora de reunión, inactividad prolongada) y ejecuta acciones sin comando explícito | P1 |
| FR6 | **Conexión Hermes Gateway**: Cliente WebSocket+HTTP hacia VPS (`hermes.sonoracorp.com`) para ejecutar agentes/skills SDC remotos y sincronizar memoria con Engram API | P0 |
| FR7 | **Recordatorios nativos del OS**: Crear, listar, completar, eliminar recordatorios vía `notify-send` (Linux) + cola persistente en SQLite local con expiración y repetición | P0 |
| FR8 | **HUD visual**: PyQt6 overlay transparente (o textual TUI como alternativa ligera) con modo compacto (solo indicador de estado) y modo expandido (chat, monitoreo, acciones recientes) | P1 |
| FR9 | **Memoria local offline**: SQLite local como caché de eventos, recordatorios, historial de voz, con sincronización batch a Engram API cuando haya conectividad | P1 |
| FR10 | **Modo offline con cola**: Cuando VPS no está disponible, todas las capacidades locales siguen funcionando; comandos que requieren SDC remoto se encolan con reintento automático | P1 |
| FR11 | **Plugin system**: Acciones modulares en `actions/*.py` con registro automático por herencia de clase base `BaseAction` — cada acción tiene trigger, requisitos, permisos | P2 |
| FR12 | **Autenticación local**: PIN o fingerprint (si disponible) para desbloquear comandos destructivos (apagar PC, borrar archivos, enviar mensajes como el usuario) | P2 |

---

## 4. Success Criteria

- [ ] `python3 -m apps.jarvis_desktop.main --test-voice` → graba 2s y reproduce "Hola, soy Jarvis" en <3s
- [ ] `python3 -m apps.jarvis_desktop.main --test-screen` → captura pantalla, ejecuta OCR, devuelve texto detectado + ventana activa
- [ ] `python3 -m apps.jarvis_desktop.main --test-mouse` → mueve cursor a (100,100) y hace click
- [ ] `python3 -m apps.jarvis_desktop.main --test-monitor` → imprime CPU, RAM, GPU, temperatura cada 5s por 30s
- [ ] Wake word "Jarvis" detectada con Porcupine/local en <1s con >90% precisión en ambiente silencioso
- [ ] Hermes API client conecta y autentica contra VPS en <2s, ejecuta `ping` tool y recibe respuesta
- [ ] `notify-send "Jarvis" "Recordatorio: reunión en 5 min"` aparece como notificación nativa de Ubuntu
- [ ] HUD se inicia, muestra indicador de estado (conectado/offline/ocupado) en bandeja del sistema
- [ ] Simular corte de VPS: comandos remotos se encolan, al reconectarse se ejecutan en orden
- [ ] `ruff check apps/jarvis_desktop/` → 0 errores
- [ ] `pytest tests/jarvis_desktop/ -q --tb=short` → 0 failures
- [ ] SCORE.md ≥ 75

---

## 5. Gherkin Scenarios

Ver `process/active/gherkin/SPEC-20260724-JARVIS-DESKTOP.feature`

### Resumen de Escenarios

**Happy Path:**
1. Usuario dice "Jarvis, ¿cómo está el sistema?" → Jarvis lee monitoreo y responde por voz
2. Usuario dice "Jarvis, recuérdame llamar a las 3pm" → recordatorio creado, notificación a las 15:00
3. Usuario dice "Jarvis, abre Firefox y busca SDC en Google" → Firefox se abre, navega a google.com, escribe "Sonora Digital Corp"
4. Usuario dice "Jarvis, ejecuta el agente de ventas en SDC" → Hermes API llama al Sales Agent remoto, resultado se muestra en HUD
5. Inicio automático: Jarvis Desktop se inicia con el sistema operativo y establece conexión Hermes

**Edge Cases:**
1. Voz: ambiente ruidoso → wake word no se activa, push-to-talk funciona como fallback
2. Desconexión: VPS offline → Jarvis responde "Modo offline: los comandos remotos se encolarán"
3. Permisos: comando destructive sin PIN → Jarvis pide "Confirma con tu PIN de seguridad"
4. HUD minimizado: usuario en pantalla completa → overlay no interfiere, solo vibración suave
5. Múltiples monitores: screen capture captura el monitor activo donde el usuario trabaja
6. GPU no disponible: monitoreo omite GPU silenciosamente sin error

---

## 6. Edge Cases

| EC# | Descripción | Manejo |
|-----|-------------|--------|
| EC1 | **Microfono no detectado** → fallback a solo texto en HUD, reconexión periódica cada 30s | El sistema arranca en modo texto y reintenta el micrófono |
| EC2 | **Wake word falso positivo** → ventana de confirmación de 2s para cancelar antes de ejecutar | HUD muestra "¿Escuché bien?" con botón cancelar; si no hay respuesta, ejecuta |
| EC3 | **Pantalla bloqueada/SSH** → screen capture devuelve negro, OCR falla | Detecta locked session, pausa screen capture, solo mantiene monitoreo del sistema |
| EC4 | **Comando ambiguo** → "Jarvis, haz eso" sin referencia previa | Jarvis responde "No tengo contexto de 'eso'. ¿Puedes ser más específico?" |
| EC5 | **Dos instancias** → segundo Jarvis detecta que el puerto 18765 (socket local) está ocupado | La segunda instancia se cierra con mensaje "Jarvis ya está corriendo" |
| EC6 | **Batería crítica** (<5%) → monitoreo se reduce a cada 60s, voz se desactiva, solo HUD mínimo | Prioriza supervivencia: guarda estado, notifica "Batería crítica — Jarvis en modo ahorro" |
| EC7 | **Comando destructivo accidental** → "Jarvis, borra todo" sin PIN | Jarvis ignora o responde "Comando bloqueado. Ingresa tu PIN de seguridad." |
| EC8 | **Laptop suspend/hibernate** → Jarvis pausa todos los loops, al reanudar reconecta automáticamente | Detecta señales de suspensión vía systemd-logind D-Bus |

---

## 7. Technical Approach

```
Arquitectura Jarvis Desktop v1.0
══════════════════════════════════

┌─────────────────────────────────────────────────────────────────────┐
│                        JARVIS DESKTOP                               │
│  apps/jarvis_desktop/                                               │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  LAYER 0 — Core Loop (asyncio)                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │   │
│  │  │  Voice Loop   │  │  Screen Loop │  │  Monitor Loop│      │   │
│  │  │  (250ms)     │  │  (2s)       │  │  (30s)      │      │   │
│  │  │  STT → LLM   │  │  Capture →   │  │  CPU/RAM/GPU │      │   │
│  │  │  → TTS       │  │  OCR →       │  │  → Alertas   │      │   │
│  │  │              │  │  Ventana Act. │  │              │      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │  Proactive Engine (cada 10s)                         │   │   │
│  │  │  Evalúa: estado sistema + contexto ventana + hora    │   │   │
│  │  │  + calendario + última interacción                   │   │   │
│  │  │  → ¿Algo que sugerir/hacer sin que pidan?            │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 1 — Acciones (plugin system)                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  actions/                                                    │   │
│  │  ├── __init__.py          ← BaseAction registry             │   │
│  │  ├── voice.py             ← STT (speech_recognition /       │   │
│  │  │                          whisper.cpp local) + TTS (pyttsx3│   │
│  │  │                          / edge-tts)                     │   │
│  │  ├── screen.py            ← mss (capture) + pytesseract     │   │
│  │  │                          (OCR) + pygetwindow (ventanas)  │   │
│  │  ├── desktop.py           ← pyautogui + pynput +            │   │
│  │  │                          wmctrl/xdotool                   │   │
│  │  ├── monitor.py           ← psutil + nvidia-ml-py (GPU)     │   │
│  │  │                          + sensors (temperatura)          │   │
│  │  ├── reminders.py         ← SQLite + notify-send +          │   │
│  │  │                          schedule cron-like               │   │
│  │  ├── notifications.py     ← notify-send / plyer /           │   │
│  │  │                          dbus-python                      │   │
│  │  ├── hermes_client.py     ← websockets + httpx → VPS        │   │
│  │  └── auth.py              ← keyring + PIN hash (bcrypt)     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 2 — HUD                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  hud/                                                       │   │
│  │  ├── tray.py              ← System tray icon (PyQt6)        │   │
│  │  ├── overlay.py           ← Overlay transparente            │   │
│  │  ├── chat_panel.py        ← Chat expandido                  │   │
│  │  ├── monitor_widget.py    ← CPU/RAM/GPU widgets             │   │
│  │  └── tui.py               ← Alternativa TUI (textual)       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 3 — Memoria                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  memory/                                                    │   │
│  │  ├── local_db.py          ← SQLite (eventos, caché,         │   │
│  │  │                          recordatorios, historial)        │   │
│  │  ├── sync.py              ← Sincronización batch a Engram   │   │
│  │  └── offline_queue.py     ← Cola FIFO con reintento         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  LAYER 4 — Startup & Lifecycle                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  main.py                 ← Entry point (asyncio.run)        │   │
│  │  config.yaml             ← Wake word, umbrales, PIN,        │   │
│  │                            VPS endpoint, acciones disabled   │   │
│  │  systemd/                                                     │   │
│  │  └── jarvis-desktop.service  ← Autostart con el sistema     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                            │
                            │ Hermes WebSocket (wss://hermes.sonoracorp.com/ws)
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ECOSISTEMA SDC (VPS)                        │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │  Hermes       │  │  Engram API  │  │  MCP Gateway │             │
│  │  Gateway      │  │  (memoria)   │  │  (skills)    │             │
│  │  :18989       │  │  :18990     │  │  :18991     │             │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘             │
│         │                  │                  │                      │
│         ▼                  ▼                  ▼                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  24 Agentes SDC  │  50+ Skills  │  7 Capas de Memoria      │   │
│  │  (Sales, Dev,    │  (Browser,   │  (Working → Strategic)    │   │
│  │   Support, etc.) │  Social, etc)│                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

### Flujo de Voz (FR1)

```
[Microphone]
    │ stream (16kHz, mono)
    ▼
Porcupine (local) ── wake word detectada ──→ [Ring Buffer 5s]
    │                                              │
    ▼                                              ▼
(silencio)                             Whisper.cpp local o
                                        Hermes STT API
                                              │
                                              ▼
                                    LLM Router (local MiniLM
                                    o Hermes API /api/chat)
                                              │
                                              ▼
                                    TTS (edge-tts local
                                    o ElevenLabs API)
                                              │
                                              ▼
                                    [Altavoz]
```

### Flujo de Proactividad (FR5)

```
[Moni] [Screen] [Hora] [Calendario] [Última interacción]
    │       │       │        │              │
    └───────┴───────┴────────┴──────────────┘
                        │
                        ▼
          Proactive Engine (cada 10s)
                        │
                        ├── CPU > 80% → "Noto el sistema pesado. ¿Cierro Chrome?"
                        ├── Batería < 20% → "Batería al 18%. ¿Activo modo ahorro?"
                        ├── Ventana = "Zoom/Meet" + hora = reunión → silencio total
                        ├── Inactividad > 30min → "¿Descanso? Han pasado 30 minutos"
                        └── Recordatorio próximo → notificación nativa
```

### Wake Word Engine

| Opción | Descripción | Latencia | Precisión | Licencia |
|--------|-------------|----------|-----------|----------|
| Porcupine (Picovoice) | `porcupine` pypi, modelo "Jarvis" personalizado | <200ms | >95% | Apache 2.0 (free 1 wake word) |
| openWakeWord | `openwakeword` pypi, modelo genérico | <300ms | >90% | MIT |
| Silero VAD + `vosk` | VAD detecta habla → ASR → match "jarvis" | <500ms | >85% | Apache 2.0 |

**Default**: Porcupine con fallback a openWakeWord.

### Hermes Client Protocol (FR6)

```
Conexión: wss://hermes.sonoracorp.com/ws/jarvis-desktop/{device_id}
Auth:     JWT en query string + refresh cada 15 min
Formato:  JSON-RPC 2.0
Métodos:
  ├── ping                          → pong
  ├── execute_agent(name, input)    → {result, tokens, cost}
  ├── execute_skill(name, params)   → {result, tokens, cost}
  ├── engram_store(layer, data)     → {memory_id}
  ├── engram_query(query, limit)    → [{memory_id, text, layer}]
  └── get_enterprise_score()        → {score, metrics}
```

### SQLite Schema (FR9)

```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event TEXT NOT NULL,         -- ej: "voice:command", "screen:capture", "alert:cpu"
  payload TEXT,                -- JSON
  created_at TEXT DEFAULT (datetime('now')),
  synced INTEGER DEFAULT 0    -- 0 = pendiente, 1 = sincronizado
);

CREATE TABLE reminders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  text TEXT NOT NULL,
  due_at TEXT NOT NULL,        -- ISO 8601
  repeat TEXT,                  -- NULL, "daily", "weekly", "hourly"
  done INTEGER DEFAULT 0,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE offline_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  method TEXT NOT NULL,         -- "execute_agent", "execute_skill", "engram_store"
  params TEXT NOT NULL,         -- JSON
  retries INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 5,
  status TEXT DEFAULT 'pending', -- pending, executing, failed, done
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE context_snapshot (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  active_window TEXT,
  cpu REAL,
  ram_used REAL,
  ram_total REAL,
  gpu_util REAL,
  battery REAL,
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## 8. Dependencies

| Dependencia | Versión | Propósito | Alternativa si no disponible |
|-------------|---------|-----------|------------------------------|
| Python | ≥3.10 | Runtime | — |
| `asyncio` | stdlib | Core loop | — |
| `porcupine` | ≥3.0 | Wake word detection | `openwakeword` |
| `whisper.cpp` (python bindings) | ≥1.7 | STT local | Hermes STT API |
| `edge-tts` | ≥6.0 | TTS local (Microsoft Edge) | `pyttsx3` (offline) |
| `PyQt6` | ≥6.7 | HUD visual | `textual` (TUI alternativa) |
| `pyautogui` | ≥0.9 | Mouse + keyboard control | — |
| `pynput` | ≥1.7 | Keyboard/mouse listeners | — |
| `mss` | ≥9.0 | Screen capture (rápido) | `PIL.ImageGrab` |
| `pytesseract` | ≥0.3 | OCR | — |
| `psutil` | ≥5.9 | CPU, RAM, disk, procesos | — |
| `nvidia-ml-py` | ≥12.0 | GPU (NVIDIA) | omitir si no hay GPU |
| `websockets` | ≥12.0 | Hermes WebSocket client | — |
| `httpx` | ≥0.27 | Hermes HTTP API client | — |
| `sqlite3` | stdlib | Memoria local offline | — |
| `keyring` | ≥25.0 | Almacén seguro de PIN/tokens | `bcrypt` hash en archivo |
| `bcrypt` | ≥4.0 | PIN hashing | — |
| `textual` | ≥1.0 | TUI alternativa | — |
| `wmctrl` | system binary | Window management | — |
| `xdotool` | system binary | X11 automation | — |
| `notify-send` (libnotify) | system binary | Native notifications | — |
| `tesseract-ocr` | system package | OCR engine | — |

---

## 9. Events to Emit

| Evento | Trigger | Payload |
|--------|---------|---------|
| `jarvis:started` | Aplicación inicia | `{device_id, version, hostname, os}` |
| `jarvis:stopped` | Aplicación termina | `{device_id, uptime_seconds}` |
| `jarvis:voice:wake` | Wake word detectada | `{device_id, engine, confidence}` |
| `jarvis:voice:command` | Comando de voz procesado | `{device_id, text, intent, latency_ms}` |
| `jarvis:voice:tts` | TTS reproducido | `{device_id, text_length, engine}` |
| `jarvis:screen:captured` | Screen capture + OCR completado | `{device_id, active_window, ocr_length, apps_detected}` |
| `jarvis:monitor:alert` | Umbral de monitoreo superado | `{device_id, metric, value, threshold}` |
| `jarvis:reminder:created` | Nuevo recordatorio | `{device_id, reminder_id, text, due_at}` |
| `jarvis:reminder:fired` | Recordatorio se dispara | `{device_id, reminder_id, text}` |
| `jarvis:proactive:suggested` | Motor proactivo sugiere acción | `{device_id, suggestion_type, context_snapshot}` |
| `jarvis:hermes:connected` | Conexión Hermes establecida | `{device_id, endpoint, latency_ms}` |
| `jarvis:hermes:disconnected` | Conexión Hermes perdida | `{device_id, endpoint, last_ok}` |
| `jarvis:hermes:queued` | Comando remoto encolado (offline) | `{device_id, method, params_summary}` |
| `jarvis:error` | Error no recuperable | `{device_id, component, error, traceback_short}` |
| `jarvis:auth:pin_required` | Comando destructivo requiere PIN | `{device_id, action}` |

---

## 10. Kill Criteria

- **Wake word no funciona en laptop del founder** después de 1 semana con 3 alternativas de engine probadas (Porcupine, openWakeWord, VAD+vosk) → abortar o reducir a push-to-talk-only
- **Latencia de voz >5s** (STT + LLM + TTS) en laptop del founder con whisper.cpp local, incluso tras optimización a modelo tiny — la experiencia always-on no es viable con latencia perceptible
- **Screen capture causa lag visible** (>500ms de bloqueo de UI) en la laptop del founder con `mss` — el costo de contexto visual supera el beneficio
- **pyautogui/wmctrl no funciona confiablemente** en Ubuntu 26.04 de la laptop del founder (Wayland issues, permisos X11) — control de escritorio inviable sin un entorno X11 funcional
- **Uso de RAM supera 1GB** en reposo (solo tray + loops mínimos) — el asistente no debe ser un ciudadano de primera clase en recursos del sistema
- **Score < 75** en la evaluación enterprise score — no pasa el gate de Tier 3
- **No hay adopción del founder** después de 2 semanas de uso activo — si el propio creador no lo usa, el producto no tiene mercado

---

## 11. Scale Criteria

- **Founder usa Jarvis Desktop >5h/día** → escalar a beta cerrada para 5 usuarios internos
- **Beta cerrada supera 90% de satisfacción** (encuesta NPS) → abrir Early Access para clientes enterprise SDC
- **>20 usuarios activos** → agregar telemetría opcional + dashboard de uso en VPS
- **>100 usuarios activos** → implementar actualizaciones automáticas vía Hermes (OTA push)
- **>500 usuarios activos** → separar módulo de voz como servicio independiente (Hermes Voice Service) para balancear carga
- **Multi-OS demanda** (Windows/Mac solicitudes) → port de los actions a API multiplataforma con `pyautogui` + alternativas nativas por OS

---

## 12. Architecture Decisions (ADR Required)

Las siguientes decisiones de arquitectura requieren ADR individual:

| Decisión | Tema | ADR ID Propuesto |
|----------|------|------------------|
| Choice of Porcupine as primary wake word engine | Voice | ADR-20260724-JD-001 |
| SQLite sync strategy to Engram (batch vs streaming) | Memory | ADR-20260724-JD-002 |
| Hermes protocol format (JSON-RPC vs custom) | Integration | ADR-20260724-JD-003 |
| Plugin system design (BaseAction ABC vs decorator registry) | Architecture | ADR-20260724-JD-004 |
| PyQt6 vs Textual for HUD | UI | ADR-20260724-JD-005 |

---

## 13. Security Considerations

| Riesgo | Mitigación |
|--------|-----------|
| Screen capture expone datos sensibles | OCR solo para detectar ventana activa, no almacena imágenes; todas las capturas se borran tras procesar |
| Comandos de voz pueden ser grabados | El ring buffer es circular, se descarta cada 5s si no hay wake word; el audio procesado se almacena solo en SQLite local con TTL 24h |
| Hermes API transporta JWT de founder | JWT almacenado en keyring del SO, no en archivo plano; refresh token rotado cada 15 min |
| Control de escritorio permite daño | Comandos destructivos requieren PIN; hay una lista negra de acciones bloqueadas en `config.yaml` |
| GPU monitoring via nvidia-smi expone metadatos | Solo métricas de utilización, no memoria de procesos ni nombres |

---

## 14. JR-Lite 15-Point Compliance

- [x] 1. Objetivo claro en 1 línea
- [x] 2. Value Driver identificado (8 drivers con tabla)
- [x] 3. FR numerados (12 FRs con prioridad)
- [x] 4. Success criteria verificables (12 items)
- [x] 5. Gherkin scenarios (5 happy path + 6 edge cases documentados)
- [x] 6. Edge cases documentados (8 ECs con manejo)
- [x] 7. Enums tipados (wake_word_engine, connection_status, reminder_repeat, action_priority)
- [x] 8. Data classes frozen (models: Event, Reminder, QueueItem, ContextSnapshot)
- [x] 9. Módulos < 200 líneas (cada action en su archivo, HUD separado, memory separado)
- [x] 10. Dependencias explícitas (22 dependencias con alternativas)
- [x] 11. Eventos definidos (15 eventos con payload)
- [x] 12. Kill criteria (7 condiciones claras)
- [x] 13. Scale criteria (5 condiciones progresivas)
- [x] 14. Docstrings con FR reference
- [x] 15. Score calculado (SCORE.md)

---

## 15. Referencias

- [Mark L](https://github.com/aymenfurter/mark-l) — Asistente de escritorio always-on con porcupine, pyautogui, whisper, TTS
- [Hermes Gateway](process/has/HAS-002-index.md) — Protocolo de comunicación entre agentes SDC
- [Engram API](process/has/HAS-003-index.md) — Memoria persistente multi-capa
- [Enterprise Score](process/has/HAS-004-index.md) — Sistema de métricas empresariales
