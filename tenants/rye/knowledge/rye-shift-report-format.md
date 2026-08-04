# RYE Reporte de Turno — Formato

Campos obligatorios por celda:
- ciclo (segundos)
- downtime (minutos)
- partes_ok
- partes_ng
- pendientes[]

Prompt corto: "reporte de turno celda N" → capturar los 5 campos.

Regla: si downtime > 5% del turno, alertar a supervisión.

Pendientes típicos:
1. Revisión de grietas en soldadura J2
2. Lubricación eje articulación
3. Calibrar visión Cognex
4. Validar par de torque PIN
