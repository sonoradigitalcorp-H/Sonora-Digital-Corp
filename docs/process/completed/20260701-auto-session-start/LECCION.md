# Lección — SPEC-20260630-000

## ¿Qué pasó?
Se implementó auto session start + session memory para eliminar fricción de inicio.

## ¿Qué salió bien?
- Scripts bash simples y robustos
- Manejo graceful de archivos faltantes
- Reglas aprendidas persisten entre sesiones

## ¿Qué salió mal?
- state/ultima-sesion.json no existía (nadie había ejecutado close-session.sh)

## Tags
session, memory, automation, bash
