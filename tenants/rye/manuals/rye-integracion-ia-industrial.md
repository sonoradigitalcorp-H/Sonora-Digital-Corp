---
type: manual
title: Integración de Robots con IA (Visión, PLC, Comunicaciones)
tags: [ia, vision, cognex, plc, ethernet, integracion]
version: 1.0
timestamp: 2026-08-03
vigencia: vigente
fuente: RYE (Cognex, Lincoln, Yaskawa, FANUC)
---

# Integración de Robots con IA Industrial — RYE

## 1. Comunicaciones
- **Ethernet/IP**: estándar para robots + PLC + visión. Configurar EDS, IP,
  y testear el handshake (si la señal no cruza, SRVO-104 frecuente).
- **I/O discretas**: señales OK/NG a entrada digital del robot. Timeout =
  bajar cinta y detener.
- **PROFINET / DeviceNet**: según el equipo (FANUC soporta varios).

## 2. Visión Cognex In-Sight
- Configurar la cámara In-Sight por Ethernet/IP.
- Recetas por pieza: cambiar receta al cambiar de producto.
- Señales: part-present y OK/NG. Verificar que el timeout no paralice la celda.
- En SRVO-104/falla de visión, revisar la conexión antes de culpar al robot.

## 3. Soldadoras (Lincoln Electric, Yaskawa)
- Controlar inicio/fin de soldadura, parámetros (voltaje, amperaje, velocidad
  de alambre) por protocolo o I/O.
- Coordinar con el robot para el ciclo de spot-weld.

## 4. IA aplicada a la integración
- Asistentes que detectan desalineación de fixtures con visión.
- Diagnóstico automático de alarmas (este bot).
- Digital twin para predecir colisiones y optimizar ciclo.
- Monitoreo predictivo de mantenimiento (downtime por celda).

## 5. Tolerancias
- Líneas automotrices: ±0.05mm. Verificar TCP, fixture y referencia en cada setup.
