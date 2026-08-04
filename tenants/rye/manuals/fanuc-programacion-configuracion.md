---
type: manual
title: FANUC Programación y Configuración con IA
model: [R-2000iC, M-710iC, R-30iB, R-30iC]
tags: [fanuc, programacion, configuracion, karel, ia]
version: 1.0
timestamp: 2026-08-03
vigencia: vigente
fuente: RYE + mejores prácticas FANUC 2026
---

# Programación y Configuración de Robots FANUC — Guía con IA

## 1. Estructura de programación
- **TPP (Teach Pendant Program)**: lenguaje principal de FANUC. Instrucciones:
  `LBL[]`, `JMP[]`, `IF[i]`, `CALL`, `UFRAME[]`, `UTOOL[]`.
- **KAREL**: lenguaje de alto nivel para lógica avanzada, comunicación y
  personalización. Variables de sistema con `$`: `$SN`, `$PR[]`, `$DLM[]`.
- **Movimiento**: `J` (articular), `L` (lineal), `C` (circular). Velocidad en
  mm/s o grados/s. Precisión por `FINE`/`CNT`.

## 2. Configuración de la celda
- **UFRAME**: sistema de coordenadas de la pieza (base de referencia).
- **UTOOL**: herramienta/soldador (punto TCP). Calibrar el TCP elimina errores
  de posición de SRVO-075.
- **Positions**: guardar en `$PR[]` para referenciar puntos de home y límites.

## 3. Cómo la IA acelera esto (mejores prácticas 2026)
- Generar programas esqueleto TPP/KAREL con LLM y validar contra el manual.
- Usar simulación OLP (offline): RoboDK/ROBOGUIDE para validar trayectorias
  antes de tocar el robot.
- Programación por voz / asistentes codifican posiciones y lógica repetitiva.
- Digital twin: simular la celda para predecir colisiones y optimizar el ciclo.

## 4. Guardas y alarmas
- **SRVO-075** (posición fuera de límite): revisar workspace, COLLISION.DAO,
  reset, home. Configurar soft limits (PARAM 1101-1108).
- **SRVO-105/107** (velocidad de marcha/seguridad): críticos — detener y escalar.
- Verificar keep relay y e-stop en la configuración de protecciones.

## 5. Buenas prácticas de configuración con IA
1. Documentar cada configuración en formato markdown (este repo).
2. Cargar configs a kb_rye para que el bot las consulte.
3. Versionar cambios de PARAM (traza en git).
4. Antes de generar/configurar con IA, darle el contexto exacto del robot
   (modelo, célula, cliente, versión de software).
