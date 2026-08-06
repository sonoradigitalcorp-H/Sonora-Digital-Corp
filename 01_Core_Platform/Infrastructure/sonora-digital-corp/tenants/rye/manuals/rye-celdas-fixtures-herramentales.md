---
type: manual
title: Configuración de Celdas, Fixtures y Herramentales
tags: [celda, fixture, herramental, setup, cambio de pieza]
version: 1.0
timestamp: 2026-08-03
vigencia: vigente
fuente: RYE (integrador de líneas BMW/Rivian/VW/Mercedes)
---

# Configuración de Celdas, Fixtures y Herramentales — RYE

## 1. Setup de celda (cambio de producción)
1. Verificar el fixture/herramental de la nueva pieza (clave locator 3-2-1).
2. Cargar el programa de la pieza correcta (validar nombre vs pieza).
3. Alinear la UFRAME/UTOOL a los nuevas puntos de referencia.
4. Ejecutar dry-run (sin pieza) para validar trayectorias y límites.
5. Verificar la soldadura con una pieza de prueba (control de primer artículo).

## 2. Fixtures y herramentales
- **Diseño**: soportes y locators posicionan la pieza. Redundancia asegura
  repetibilidad ±0.05mm en líneas automotrices.
- **Verificación**: medir desgaste y desalineación periódicamente.
- **Cambio**: al cambiar herramental, recalibrar la referencia del robot.

## 3. Nuevas piezas
1. Revisar planos y fixture de la pieza nueva.
2. Definir puntos de pick/place y soldadura.
3. Simular en OLP antes de programar en línea.
4. Ajustar velocidad/ciclo y validar tolerancia.

## 4. Backups de configuración por celda
- Guardar por celda: parámetros, posiciones, programas, fixtures (fotos).
- Registrar en kb_rye para consulta rápida del bot.

## 5. Buenas prácticas con IA
- El bot consulta el setup de cada celda (conceptos curados de este repo).
- Cambios de celda/pieza se documentan y se alimentan al conocimiento para
  que la IA asista en el próximo cambio.
