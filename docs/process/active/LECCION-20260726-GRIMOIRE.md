# LECCIÓN — Mystic Grimoire: Agentic OS 3D Infinity

| Campo | Valor |
|-------|-------|
| **ID** | `LECCION-20260726-GRIMOIRE` |
| **Fecha** | 2026-07-26 |
| **Sesión** | Reconstrucción total del frontend + wake word + browser actions |
| **Tags** | `frontend`, `svelte`, `threejs`, `voice`, `wakeword`, `kokoro`, `playwright`, `costos` |

---

## 🧠 Resumen de la Sesión

### Objetivo
Construir el Agentic OS de Sonora Digital Corp: un frontend 3D con el símbolo del infinito (∞) que representa el sistema, conectado en tiempo real con voz, memoria, y agentes.

### Problemas detectados

1. **VPS sin SSH** — disco al 93% (89G/96G). Causa más probable: swap llena + logs sin rotar.
2. **Contenedores caídos** — postgres, neo4j, qdrant, redis, n8n, supabase: todas las imágenes descargadas pero ningún contenedor corriendo (excepto Gitea).
3. **Repos divergidos** — Local y VPS estaban en ramas diferentes con commits distintos. Se unificó en Gitea.
4. **Portal JS vacío** — El directorio `portal/js/` estaba vacío, el frontend 3D no existía realmente.

### Logros de la sesión

| Logro | Detalle |
|---|---|
| **Gitea como SSOT** | Se creó el repo, se unificaron local+VPS, DNS `git.sonoradigitalcorp.com` configurado |
| **Kokoro TTS conectado** | Kokoro-82M (voz `em_alex`) como primario en Mystic Voice. Test: 139KB / 2.9s de audio |
| **Wake Word** | openWakeWord detecta "Hey Jarvis" (threshold 0.5). Streaming continuo de audio |
| **Browser Actions** | Playwright navega sitios + Kokoro lee contenido en voz alta |
| **Intent Router** | Intents de navegación: "navega a X", "busca Y" con extracción de URLs |
| **Cost Tracker DB** | SQLite inicializada con muestra de datos. Endpoint `/api/cost/daily` |
| **Frontend Svelte** | Proyecto Svelte 4 + Three.js con ∞ 3D, paneles HUD, WebSocket |
| **Pipeline de voz** | WakeWord → VAD → Whisper STT → Intent Router → Browser/LLM → Kokoro TTS |

### Arquitectura resultante

```
🔮 Wake Word ("Hey Jarvis") → openWakeWord
   ↓ detectado
🎤 Streaming audio → VAD → Whisper STT
   ↓ texto
🧠 Intent Router → browse/search → BrowserActions (Playwright)
   ↓                        ↓
Template/LLM          Kokoro lee la web
   ↓                        ↓
🔊 Kokoro TTS (voz em_alex) ← ─ ─ ─ ┘
   ↓
🎵 Audio + soundscape → WebSocket → Svelte Grimoire 3D
```

### Costos actuales

| Concepto | Costo |
|---|---|
| VPS OVH | $15/mes |
| Dominio | $12/año |
| OpenRouter (deepseek-v4-flash) | $0.00026/chat ~ $2.60/10K chats |
| Ollama local (llama3.2:3b) | $0 (CPU) |

### Próximos pasos (pendientes)

1. **Liberar disco en VPS** (cuando SSH reconecte) para levantar Postgres + Neo4j + Qdrant
2. **Conectar Engram + Brain Service** con las DBs para memoria persistente multi-cliente
3. **Implementar Mystic Shield** (extraído a repo propio en commit 451ec35b)
4. **Dashboard dinámico** — que el agente inyecte queries SQL y renderice paneles en el Grimoire
5. **Despliegue del Grimoire** → `grimorio.sonoradigitalcorp.com`

### Referencias

- `apps/grimoire/` — Proyecto Svelte (local, no en VPS aún)
- `apps/voice-realtime/` — Servidor de voz con Kokoro + wake word
- `portal/grimoire.html` — Versión HTML estática del Grimoire (en VPS)
- `products/galaxy-backend/` — Backend con endpoints de costos y sistema
- `data/cost_tracker.db` — Base de costos por tenant
- `config/cost-rates.yaml` — Tarifas de LLMs y servicios
- `tenants/registry.yaml` — 8 tenants configurados
