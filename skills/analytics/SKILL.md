---
name: analytics
description: Generate business reports and dashboards from Hasura data. Use when the user asks for reports, metrics, KPIs, or data analysis.
version: 1.0.0
updated: 2026-07-13
---

# Analytics Skill

Generate business intelligence reports and dashboards using Hasura, Engram, and RAG data.

## Tools que usa
- `hasura_query` — consultar artists, transactions, products
- `engram_search` — buscar memorias y patrones
- `rag_search` — contexto adicional
- `llm_chat` — generar análisis y recomendaciones

## Pipeline diario (08:00)
1. `hasura_query` → revenue del día, streams, transacciones
2. `engram_search` → eventos relevantes de ayer
3. `llm_chat` → genera reporte ejecutivo
4. `engram_save` → guarda reporte del día

## Ejemplo
```
Genera reporte semanal de ABE Music con revenue por artista
```
