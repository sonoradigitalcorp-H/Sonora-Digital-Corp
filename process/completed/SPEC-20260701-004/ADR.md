# ADR-20260701-004 — Capability Registry + Decision Engine

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260701-004` |
| **Fecha** | 2026-07-01 |
| **Spec** | `SPEC-20260701-004` |
| **Estado** | aceptado |

---

## Context

`sync.py` importaba `fetch_artist` de Deezer directo — orden fijo, sin fallback real. Agregar un collector nuevo requería cambiar código en sync.py. Sin abstracción entre "qué necesito" (capability) y "quién lo provee" (provider). Necesitábamos un sistema donde el runtime consulte un registry, elija el mejor proveedor según disponibilidad, y ejecute contra cualquier fuente sin cambiar código cliente.

## Decision

### 1. Capability Registry first

**Decisión:** Construir el registry de capacidades primero, antes que Planner/Policy/Marketplace/20 capas. El registry fuerza todas las abstracciones.

**Alternativa:** Construir capas de arriba hacia abajo (Planner → Policy → Engine → Registry).

**Por qué:** Registry es la base de datos de todas las abstracciones. Sin registry, las capas superiores no tienen foundation. Adagio: "build the registry, everything else falls out of it."

### 2. JSON declarativo + Pydantic validation

**Decisión:** Registry en `config/registry.json` con schema validado por Pydantic v2 en `planner/models.py`.

**Alternativa:** Registry en base de datos (Qdrant/Neo4j) o código Python.

**Por qué:** JSON es portable, versionable en git, editable por cualquier agente/OS, sin dependencias de runtime. Pydantic da type safety sin setup.

### 3. Fallback chain por weight, no health-first

**Decisión:** `execute_capability()` prueba providers en orden de weight ascendente. Si el primero falla, intenta el siguiente automáticamente. Health check es informativo (cache TTL 5min), no bloqueante.

**Alternativa:** Health check blocking — solo ejecutar providers healthy, abortar si todos están down.

**Por qué:** Health checks pueden fallar por network glitch mientras el provider está realmente disponible. Fallback en runtime es más robusto. Health check da prioridad pero no exclusión.

### 4. Executor pattern (strategy)

**Decisión:** Cada `contract_type` tiene un executor dedicado: `http.py`, `cli.py`, `browser.py`, `mcp.py`, `sdk.py`.

**Alternativa:** Todo en una función gigante con if/elif.

**Por qué:** Cada executor tiene lógica distinta (httpx vs asyncio subprocess vs Playwright vs MCP tools). Separación limpia, testeable individualmente, extensible sin tocar existentes.

### 5. Eventos a JSONL append-only

**Decisión:** Todos los eventos del engine se emiten a `state/logs/events.jsonl` en formato JSONL (una línea por evento).

**Alternativa:** Base de datos (Qdrant, PostgreSQL) o logs de sistema.

**Por qué:** JSONL es append-only, zero setup, zero dependencies, grep-friendly, importable a cualquier sistema. Suficiente para auditoría y debugging.

## Consequences

**Positivo:**
- sync.py migrado sin cambiar collectors — zero regresión
- 3 capabilities, 10 providers, todo declarativo
- 70 tests, 79 total pasando
- Browser scraping funcional para TikTok, Spotify, Instagram (login wall detectado)
- Costo $0 en APIs
- Fallback probado: si Deezer falla, Apple Music responde

**Trade-offs:**
- Browser scraping es frágil a cambios HTML — requiere monitoreo
- JSON registry sin UI — Abraham no puede editarlo (no necesita hacerlo)
- Health checks no blocking pueden ejecutar provider unhealthy si falla cache
- Execution timeout fijo (30s) — algunos providers (TikTok browser) pueden exceder

## Related

- Spec: `SPEC-20260701-004`
- Registry: `config/registry.json`
- Events: `CapabilityExecuted`, `ProviderFailed`, `ProviderDegraded`, `ProviderRecovered`, `NoProviderAvailable`, `RegistryUpdated`, `SyncCycleStarted`, `SyncCycleCompleted`
