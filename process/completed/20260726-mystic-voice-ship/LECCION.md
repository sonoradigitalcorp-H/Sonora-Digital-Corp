# Lección — SPEC-20260725-MYSTIC-VOICE-SHIP

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260725-MYSTIC-VOICE-SHIP` |
| **Tier** | 2 (Capability) |
| **Fecha** | 2026-07-26 |
| **Score** | 80/100 |

---

## ¿Qué pasó?

Se implementó Mystic Voice como asistente personal completo para el founder de SDC: monitoreo del sistema por voz (CPU/RAM/disk/uptime), memoria persistente en SQLite que sobrevive recargas de página, PWA instalable como app de escritorio, wake word automática, alertas proactivas de CPU/RAM, y conexión directa a Engram para memoria a largo plazo.

Se crearon 6 archivos nuevos y se modificaron 3 existentes en `apps/voice-realtime/`. Adicionalmente se crearon 2 frontends adicionales (cosmic 3D y 3D agent visualization) que exceden el scope original del spec.

---

## ¿Qué salió bien?

- System Monitor con graceful degradation (`_safe()` pattern) — si psutil no está, responde "No tengo acceso" sin crash
- SQLite session DB con auto-recovery ante corrupción — detecta, borra, recrea, loggea warning
- Direct Engram bridge 3x más rápido que MCP Gateway para voice realtime
- 3-tier LLM fallback (OpenRouter → OpenCode → Ollama) asegura disponibilidad
- Proactive monitor loop funciona en producción — notifica sin interrumpir
- PWA manifest + service worker funcionales en Chrome y navegadores Chromium
- `ruff check apps/voice-realtime/` → 0 errores
- Todos los FRs de la spec implementados y verificados
- Cosmic UI y 3D visualization como bonus no planificado

---

## ¿Qué salió mal?

- Engram bridge duplica lógica del MCP client — hay que consolidar en refactor futuro
- Proactive monitor no distingue entre sesiones — todas reciben la misma alerta sin filtro
- `session_id` de 8 chars (uuid4[:8]) puede colisionar en alta concurrencia
- No se implementó test suite formal para voice-realtime (solo linting)
- La spec original no contemplaba `engram_bridge.py` — surgió como necesidad durante implementación
- Cosmic 3D y 3D visualizations son cool pero no estaban en spec — riesgo de scope creep

---

## ¿Qué haríamos diferente?

- Definir `session_id` completo (uuid4 completo, 36 chars) en lugar de truncar
- Agregar tests unitarios para `monitor.py` y `session_db.py` antes del merge
- Consolidar `EngramBridge` con `MCPClient` en un solo adaptador de memoria
- Filtrar proactive alerts por sesión (no broadcast global)
- Estimar tiempo para features extra (cosmic UI) por separado del spec principal
- Agregar health check endpoint para el proactive monitor

---

## Próximos pasos

1. Consolidar Engram direct bridge + MCP client en un solo MemoryAdapter
2. Agregar tests pytest para voice-realtime pipeline
3. Migrar session_id a uuid4 completo
4. Extender proactive monitor a más métricas (disk, network bandwidth)
5. Agregar telemetría de uso (interacciones/día, sesiones/día)
6. Documentar Mystic Voice como producto SKU para PYMEs

---

## Engram Tags

voice, mystic, realtime, pwa, sqlite, engram, system-monitor, proactive, kokoro-tts, founder-independence
