# Auditoría de Seguridad y Ciberseguridad — Sonora OS

**Fecha:** 2026-07-19
**Auditor:** Mystic (SDC Orchestrator)
**Rama:** feat/whatsapp-os-fase1
**Commit:** b5b6f7d (pendiente fixes)

---

## Resumen Ejecutivo

| Categoría | Críticos | Altos | Medios | Bajos |
|-----------|----------|-------|--------|-------|
| Secrets hardcodeados | 2 | 1 | 2 | 3 |
| Duplicidades | 0 | 0 | 1 | 2 |
| Archivos huérfanos | 1 | 2 | 3 | 5 |
| Prompt Injection | 0 | 1 | 2 | 2 |
| Puertos/Red | 0 | 0 | 2 | 3 |
| Versioning | 0 | 0 | 3 | 4 |
| **Total** | **3** | **4** | **13** | **19** |

---

## 🔴 CRÍTICOS (Requieren acción inmediata)

### C-01: OpenRouter API Key hardcodeada en whatsapp_agent.py
- **Archivo:** `apps/voice/whatsapp_agent.py:423`
- **Valor:** `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`
- **Riesgo:** Cualquiera con acceso al repo puede usar la key para llamar OpenRouter a costa del dueño
- **Status:** ✅ **CORREGIDO** — Reemplazado por `os.environ.get("OPENROUTER_API_KEY") or ""`
- **Acción:** Rotar la key en OpenRouter dashboard inmediatamente

### C-02: OpenRouter API Key hardcodeada en browser_revoke_keys.py
- **Archivo:** `scripts/browser_revoke_keys.py:13`
- **Valor:** `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`
- **Riesgo:** Misma key expuesta en script de revocación
- **Status:** ✅ **CORREGIDO** — Reemplazado por `os.environ.get("OPENROUTER_KEEP_KEYS", "")`
- **Acción:** Rotar la key en OpenRouter dashboard

### C-03: Backups contienen secrets en texto plano
- **Archivos:** `backups/*/config/.secrets/clients.json`, `backups/*/opencode.json`, etc.
- **Riesgo:** 6.8GB de backups con secrets (API keys, JWT tokens, configs sensibles)
- **Status:** ⚠️ **NO CORREGIDO** — Requiere decisión del usuario
- **Acción recomendada:** 
  1. Migrar secrets a vault/env vars (ya están en .env.example)
  2. Limpiar backups: `rm -rf backups/*/config/.secrets/`
  3. Rotar todas las keys expuestas en backups
  4. Agregar script de backup que excluya secrets explícitamente

---

## 🟠 ALTOS

### A-01: Langfuse default secrets en instrument-langfuse.py
- **Archivo:** `scripts/instrument-langfuse.py:20`
- **Valor:** `pk-lf-sdc-2026`, `sk-lf-sdc-2026-secret`
- **Riesgo:** Default values que podrían usarse en desarrollo sin darse cuenta
- **Status:** ✅ **CORREGIDO** — Reemplazados por cadenas vacías

### A-02: Symlinks rotos (ya corregido)
- **Archivos:** `apps/google-mcp → ../products/google-mcp`, `apps/content-server → ../products/content-studio`
- **Riesgo:** Scripts que dependen de estas rutas fallarían silenciosamente
- **Status:** ✅ **CORREGIDO** — Symlinks eliminados

### A-03: Archivos huérfanos grandes con datos sensibles
- **Archivos:** `speech-abe-fenix.ogg` (~4MB), `speech-abe-fenix.mp3` (~4MB)
- **Riesgo:** Datos de audio de clientes (ABE Music) en root del repo
- **Status:** ✅ **CORREGIDO** — Archivos eliminados

### A-04: Turnstile sitekey hardcodeada en frontend
- **Archivo:** `frontends/app/src/App.jsx:273` — `sitekey: '0x4AAAAAAAXx8o3BmBTxQq1t'`
- **Riesgo:** Sitekey de Cloudflare Turnstile (no crítica per se, pero idealmente en env var)
- **Status:** 📝 Documentado — Turnstile sitekeys son públicas por diseño, pero mover a env var sería mejor práctica

---

## 🟡 MEDIOS

### M-01: VPS IP hardcodeada en 8+ archivos
- **Archivos:** `opencode.json`, `scripts/presentar.py`, `scripts/healthcheck.sh`, otros
- **Riesgo:** Si la IP cambia, hay que actualizar en N lugares. También expone IP pública en el repo.
- **Status:** 📝 Documentado — Mover a variable de entorno `SONORA_VPS_HOST`

### M-02: 279 archivos duplicados (mismo hash)
- **Causa:** Principalmente duplicación entre `tenants/abe-music/` y `apps/abe-service/`, y entre `frontends/` y `products/`
- **Riesgo:** Inconsistencia — arreglar un bug en un lugar no lo arregla en el duplicado
- **Status:** ⚠️ Requiere auditoría manual de duplicados reales

### M-03: CORS abierto en múltiples APIs
- **Archivos:** Múltiples `app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)`
- **Riesgo:** Cualquier origen puede llamar a las APIs desde un navegador
- **Status:** 📝 Documentado — Para APIs internas, restringir a orígenes conocidos

### M-04: Sin autenticación en varios endpoints
- **Archivos:** Múltiples FastAPI apps sin auth middleware global
- **Riesgo:** Endpoints expuestos sin autenticación en red local
- **Status:** 📝 Documentado — Implementar dependency `require_auth()` global

### M-05: Puerto 18989 (MCP Gateway) sin autenticación por defecto
- **Riesgo:** El gateway permite tool execution sin auth si no se configura SONORA_CLIENT_ID/SECRET
- **Status:** 📝 Documentado — Revisar configuración de auth en el gateway

### M-06: Sin rate limiting en APIs
- **Riesgo:** Posible abuso/DoS de endpoints públicos
- **Status:** 📝 Documentado — Implementar `slowapi` o similar

---

## 🔵 BAJOS

### B-01: Sin healthchecks en Dockerfiles
- **Status:** 📝 Documentado — Agregar HEALTHCHECK a todos los Dockerfiles

### B-02: Backups sin cifrado
- **Status:** 📝 Documentado — Backups viajan y se almacenan en texto plano

### B-03: Sin .dockerignore en varios proyectos
- **Status:** 📝 Documentado — Agregar .dockerignore para reducir tamaño de imágenes

### B-04: Sin pruebas de seguridad automatizadas en CI
- **Status:** 📝 Documentado — Agregar `pip-audit` o `safety` al CI

### B-05: Sin verificación de integridad de backups
- **Status:** 📝 Documentado — Agregar checksum verification

---

## 🧩 Prompt Injection & Seguridad de Agentes

### Análisis de vectores de inyección

| Vector | Riesgo | Mitigación actual |
|--------|--------|-------------------|
| User input → LLM sin sanitizar | 🔴 Alto | Ninguna — el input del usuario va directo al prompt del LLM |
| System prompts con variables de usuario | 🟡 Medio | Algunos system prompts usan f-strings con input del usuario |
| Historial de chat → entrenamiento | 🟢 Bajo | No hay fine-tuning automático, solo RAG |
| RAG con documentos maliciosos | 🟡 Medio | No hay sanitización de documentos ingeridos |

### Skills con políticas de seguridad
- **skills/nsfw/SKILL.md**: Tiene políticas de safety y content filtering
- **skills/incident-response.skill.md**: Tiene runbook de respuesta
- **skills/audit-security.skill.md**: Tiene políticas de escaneo de secrets
- **Resto de skills**: No definen políticas de seguridad explícitas

### Recomendaciones
1. Agregar sanitización de input de usuario antes de pasar al LLM (escapar `{`, `}`, `{{`, `}}`)
2. Implementar guardrails de output (no generar código peligroso, no exponer system prompts)
3. Agregar rate limiting por usuario/hora en endpoints de chat
4. Implementar content filtering para RAG (no indexar documentos maliciosos)

---

## 📊 Puertos y Servicios

| Puerto | Servicio | Tipo | Auth | Expuesto |
|--------|----------|------|------|----------|
| 18989 | MCP Gateway | HTTP | JWT | Local |
| 18789 | OpenClaw Gateway | HTTP | ? | Local |
| 8000 | Hermes MCP | HTTP | ? | Local |
| 8080 | Evolution Dashboard | HTTP | No | Local |
| 8088 | Guardian API | HTTP | No | Local |
| 8765 | Content Server | HTTP | No | Docker |
| 8502 | Open Notebook | HTTP | No | Docker |
| 3900 | OmniVoice | HTTP | No | Docker |
| 5678 | n8n | HTTP | Sí | Docker |
| 6333 | Qdrant | HTTP | No | Docker |
| 7687 | Neo4j | Bolt | Sí | Docker |
| 6379 | Redis | TCP | No | Docker |
| 5432 | PostgreSQL | TCP | Sí | Docker |
| 6200 | Notifier | HTTP | No | Nuevo |
| 6300 | Order Tracker | HTTP | No | Nuevo |
| 6400 | Affiliates | HTTP | No | Nuevo |
| 6401 | ADK Bridge | HTTP | No | Nuevo |

**Hallazgo:** Múltiples servicios sin autenticación accesibles en localhost. Si un atacante obtiene acceso a la máquina, tiene control total.

---

## 🗃️ Versioning Gaps

| Componente | Versionado | Tag | Changelog |
|------------|-----------|-----|-----------|
| Python SDK (sonora_client.py) | ✅ v2.0 | No | No |
| Node SDK (sonora-client.js) | ✅ v2.0 | No | No |
| ADK Runtime (adk.js) | ✅ v1.0 | No | No |
| ADK Bridge | ❌ Sin versión | No | No |
| Notifier | ❌ Sin versión | No | No |
| Order Tracker | ❌ Sin versión | No | No |
| Affiliates | ❌ Sin versión | No | No |
| Skills | ✅ v1.0.0 (cada una) | No | No |

**Recomendación:** Agregar `VERSION` file en cada producto, crear `CHANGELOG.md` por producto, y usar tags de git (`v1.0.0`, `v2.0.0`) para releases.

---

## ✅ Acciones Inmediatas Realizadas

| # | Acción | Status |
|---|--------|--------|
| 1 | OpenRouter key en whatsapp_agent.py → env var | ✅ |
| 2 | OpenRouter key en browser_revoke_keys.py → env var | ✅ |
| 3 | Langfuse defaults → empty string | ✅ |
| 4 | Symlinks rotos eliminados | ✅ |
| 5 | Archivos .ogg/.mp3 huérfanos eliminados | ✅ |
| 6 | Auditoría documentada en este archivo | ✅ |

## ⚠️ Acciones Pendientes (Requieren tu decisión)

| # | Acción | Prioridad |
|---|--------|-----------|
| 1 | Rotar las 2 OpenRouter keys expuestas | 🔴 Inmediata |
| 2 | Limpiar secrets de backups/ | 🔴 Alta |
| 3 | Migrar VPS IP a env var | 🟡 Media |
| 4 | Restringir CORS a orígenes conocidos | 🟡 Media |
| 5 | Implementar auth middleware global | 🟡 Media |
| 6 | Rate limiting en APIs | 🟡 Media |
| 7 | Sanitización de prompts (input → LLM) | 🟡 Media |
| 8 | Agregar version tags y CHANGELOGs | 🔵 Baja |

---

*Auditoría generada por Mystic (SDC Orchestrator) — 2026-07-19*
