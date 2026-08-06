---
type: index
title: RYE Manuales — Índice
timestamp: 2026-08-03
---

# Base de Datos de Manuales RYE

Índice de manuales cargados. Cada manual tiene frontmatter (tipo, modelo,
tags, versión) y se indexa en kb_rye para consulta del bot.

## Manuales de programación
- **FANUC Programación y Configuración** → [fanuc-programacion-configuracion.md](fanuc-programacion-configuracion.md)
  — TPP/KAREL, UFRAME/UTOOL, IA para programar, soft limits.

## Manuales de reparación/mantenimiento
- **FANUC Reparación y Mantenimiento** → [fanuc-reparacion-mantenimiento.md](fanuc-reparacion-mantenimiento.md)
  — tabla SRVO, preventivo/correctivo, backups.

## Manuales de celdas/fixtures/herramentales
- **Celdas, Fixtures y Herramentales** → [rye-celdas-fixtures-herramentales.md](rye-celdas-fixtures-herramentales.md)
  — setup, cambio de pieza, nuevos productos, backups por celda.

## Manuales de integración con IA
- **Integración Robots + IA industrial** → [rye-integracion-ia-industrial.md](rye-integracion-ia-industrial.md)
  — Ethernet/IP, Cognex, soldadoras, IA predictiva.

## Cómo agregar un manual
1. Copiar un archivo con frontmatter a `tenants/rye/manuals/`.
2. Agregarlo a este índice (ruta canónica).
3. Ejecutar el ingest para indexarlo:
   `TENANT_ID=rye KNOWLEDGE_DIR=.../tenants/rye/manuals python3 scripts/ingest_qdrant_openrouter.py`
4. El bot ya lo consultará por RAG.
