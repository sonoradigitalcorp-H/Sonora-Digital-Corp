# SPEC — Pipeline Auto-Enforcement + Engram Learning Loop

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260701-001` |
| **Fecha** | 2026-07-01 |
| **Autor** | OpenClaw |
| **Tier** | 2 |
| **Estado** | activo |
| **Score requerido** | ≥60 |

---

## 1. Objetivo

Cerrar el ciclo de aprendizaje: cada SPEC completado → auto-store en Engram, cada inicio de tarea → auto-query de contexto relevante, cada error del sistema → auto-store como lección. El sistema mejora solo con cada operación.

---

## 2. Value Driver

knowledge, automation, founder-independence

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| FR1 | `process-pipeline.sh complete` llama a `store_spec_completion()` automáticamente |
| FR2 | Orquestador ejecuta `query_engram_context()` antes de `agent.run()` |
| FR3 | Error correction detecta fallos → `store_learning()` con tag "error" |
| FR4 | Engram context formateado se inyecta en el prompt del agente |
| FR5 | Tests: verificar ciclo completo (store → query → inject) |

---

## 4. Success Criteria

- [ ] Completar un SPEC → aparece en Engram automáticamente
- [ ] Agente ejecuta tarea → recibe contexto de experiencias pasadas
- [ ] Error del sistema → se guarda como lección
- [ ] Engram: 209 → 300+ memorias

---

## 5. Technical Approach

- Hook en `process-pipeline.sh`: al final de `complete`, llama a `pipeline-bridge.py store`
- Hook en `orchestrator.py`: antes de `agent.run()`, llama a `query_engram_context()` + `format_engram_context()` y lo agrega al context
- Error correction service: capturar exit codes no-zero → `store_learning()`

---

## 6. Dependencies

- pipeline_bridge.py existente ✅
- Engram con importance scoring ✅
- process-pipeline.sh CLI ✅

---

## 7. Kill Criteria

Si el auto-query hace que los agentes sean más lentos (>500ms overhead), desactivar y dejar como manual.

---

## 8. Scale Criteria

Cuando Engram tenga >1000 memorias, implementar pruning automático (borrar importance=0 con >90 días sin access).
