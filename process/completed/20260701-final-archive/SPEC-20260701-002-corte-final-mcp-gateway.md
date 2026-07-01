# SPEC-20260701-002: Corte Final — MCP Gateway como Entry Point Real

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-002` |
| **Fecha** | 2026-07-01 |
| **Autor** | Strategy OS |
| **Tier** | 2 |
| **Estado** | borrador |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Completar la migración a Native Agent OS: eliminar FastAPI como entry point de API, migrar los 15 routers restantes a MCP tools, y hacer que TODO el tráfico pase por el MCP Gateway exclusivamente.

---

## 2. Value Driver

**founder-independence** — el fundador ya no necesita tocar nginx/FastAPI para exponer una nueva funcionalidad. **automation** — eliminar la última capa legacy de routing.

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | Migrar 15 routers FastAPI restantes a MCP tools |
| FR2 | Sacar FastAPI del medio: nginx solo apunta a :18989, no más /api/legacy/ |
| FR3 | FastAPI solo sirve web UI (sin API endpoints) |
| FR4 | Provider Router conectado al FinOps (cost tracking por capability) |
| FR5 | Web UI funciona 100% via /api/mcp/{path} proxy |
| FR6 | CI/CD verifica que no haya llamadas directas a FastAPI API |
| FR7 | Los 3 routers ya migrados (sales, score, voice) se prueban end-to-end via MCP únicamente |

---

## 4. Success Criteria

- [ ] nginx solo tiene 1 location block: `proxy_pass :18989`
- [ ] Los 3 routers migrados responden via MCP gateway, no via FastAPI
- [ ] 15 routers nuevos migrados a MCP tools → 44 + X = 59+ tools total
- [ ] Provider Router escribe cost tracking a `state/finops.jsonl`
- [ ] Web UI funciona via proxy MCP
- [ ] `curl http://localhost:8000/api/*` devuelve 404 o redirect
- [ ] CI/CD testea que no haya endpoints FastAPI directos

---

## 5. Plan de Ataque (por Valor)

```
Prioridad ALTA (lo que libera más valor):

1. Provider Router → FinOps (conectar cost tracking)
   └── 1 archivo, 30 min, impacto inmediato en visibilidad de costos

2. Migrar 5 routers de mayor tráfico a MCP tools
   └── sessions, brain, content, store, webhooks
   └── ~2h cada uno

3. Cortar nginx: eliminar /api/legacy/
   └── 1 línea en 4 archivos

Prioridad MEDIA:

4. Migrar 10 routers restantes
   └── commands, sdc, mysticverse, payments, abe, zamora, 
        approvals, files, skills, app

5. CI/CD: test que verifica 0 endpoints legacy activos

Prioridad BAJA:

6. Limpiar y deprecar código legacy
```
---

## 6. Gherkin Scenarios

Ver `gherkin/SPEC-20260701-002.feature`

---

## 7. Edge Cases

- [EC1] Algún cliente externo llama a FastAPI directo → redirect 301 con aviso de deprecación
- [EC2] MCP Gateway caído → FastAPI legacy NO debe activarse (seguridad > disponibilidad)
- [EC3] Tool migrada pero la ruta FastAPI sigue funcionando → error hasta que se limpie

---

## 8. Dependencies

- MCP Gateway funcionando (ya ✅)
- Todos los servicios Docker arriba
- Los 3 routers ya migrados en Fase 1 (sales, score, voice)

---

## 9. Events to Emit

| Evento | Cuando |
|--------|--------|
| `router_migrated` | Cada router FastAPI migrado a MCP tool |
| `nginx_cutover` | nginx cambia a :18989 exclusivamente |
| `fastapi_deprecated` | FastAPI deja de ser API gateway |
| `finops_connected` | Provider Router conectado a cost tracking |
| `legacy_cleaned` | Código legacy eliminado |

---

## 10. Kill Criteria

- Si después de migrar los primeros 5 routers, el web UI deja de funcionar por más de 2h
- Si el corte de nginx rompe servicios en producción

---

## 11. Scale Criteria

- Cuando todas las tools estén migradas + FinOps conectado → Native Agent OS alcanza el estado **completo**
- Próximo hito: Workflow Engine multi-agente
