---
type: index
title: RYE Knowledge Index
timestamp: 2026-08-03
---

# Índice de Conocimiento RYE

Índice de los conceptos curados. El conductor lo lee primero para saber qué
existe y dirigir la consulta. Enlaza a cada concepto por ruta canónica.

## Conceptos curados (exactos y estables → consultar antes del RAG)

- **Alarmas FANUC** → [fanuc-srvo-alarms.md](fanuc-srvo-alarms.md) — SRVO-001, 032, 075, 104. Causa + acción por código. Válido para líneas BMW/Rivian.
- **Celda 3** → [rye-cell-3-spec.md](rye-cell-3-spec.md) — R-2000iC + Lincoln, ciclo 45s, throughput 80 p/h, downtime 2-4%.
- **Reporte de turno** → [rye-shift-report-format.md](rye-shift-report-format.md) — formato: ciclo, downtime, partes_ok/ng, pendientes.

## Cuándo usar RAG (kb_rye)

Usar RAG para búsquedas "dónde se mencionó X": tickets, incidencias, logs,
corpus grandes que cambian seguido. Si la pregunta es sobre un concepto curado
(listado arriba), responder desde el concepto (exacto y vigente) — el índice
indica su ruta.

## Regla de vigencia

Si el RAG devuelve un fragmento que contradice a un concepto del índice,
**gana el concepto curado** (es la definición vigente).

## Ausencia

Si la consulta no está en el índice ni hay contexto RAG relevante (score bajo),
decir que no se tiene esa información y sugerir el manual FANUC oficial / escalar.
