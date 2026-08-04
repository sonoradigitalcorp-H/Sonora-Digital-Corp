---
type: manual
title: FANUC Reparación y Mantenimiento de Robots
model: [R-2000iC, M-710iC, R-30iB]
tags: [fanuc, reparacion, mantenimiento, servo, motor, greasing]
version: 1.0
timestamp: 2026-08-03
vigencia: vigente
fuente: RYE + manuales de servicio FANUC
---

# Reparación y Mantenimiento de Robots FANUC — Guía

## 1. Diagnóstico de fallas (SRVO)
| Alarma | Causa | Acción |
|--------|-------|--------|
| SRVO-001 | Sobrecarga servo | Verificar fricción, carga, freno; lubricar, revisar eje |
| SRVO-032 | Exceso de torque | Recalcular inercia (PARAM 1121), verificar acoplamiento |
| SRVO-075 | Posición fuera de límite | Workspace, COLLISION.DAO, reset, home |
| SRVO-104 | Comunicación servo | Revisar cableado, reiniciar controlador EIP |
| SRVO-105/107 | Seguridad velocidad | DETENER y escalar — crítico |

## 2. Mantenimiento preventivo
- **Lubricación**: ejes articulación según intervalo del fabricante (grasa
  específica); revisar niveles.
- **Rodamientos/frenos**: verificarlos en ejes de alta carga (J2 spot-weld).
- **Cableado**: inspeccionar mangueras del brazo (fatiga por movimiento).
- **Backup de parámetros**: respaldar keep relay, PARAM, posiciones en cada
  intervención.

## 3. Mantenimiento correctivo
1. Bloquear y etiquetar (lockout/tagout) antes de cualquier intervención.
2. Liberar el robot, verificar el defecto con el teach pendant.
3. Sustituir el componente (motor, freno, encoder) siguiendo el manual.
4. Calibrar TCP y posiciones después del reemplazo.
5. Reajustar soft limits y verificar con ciclo de prueba.

## 4. Backup y restauración
- **Image Backup**: completo (controlador). Respaldar a USB antes de cambios.
- **File Backup**: programas y parámetros (cada cambio).
- Guardar copias numeradas/versionadas para trazabilidad.
