# Patrones — Soluciones Recurrentes

## P1. Nueva feature

```
Issue "feature request"
  → Author escribe spec en specs/<n>-<nombre>/spec.md
  → Reviewer aprueba spec
  → Label "approved" en Issue
  → implementador.sh: branch → OpenCode implementa → PR
  → Reviewer aprueba PR
  → Merge a main
  → Lesson en memory/lecciones.json
```

## P2. Error de implementación

```
Tests fallan en PR
  → Author corrige o rechaza PR
  → Si es error del spec: actualizar spec.md
  → Si es error de implementación: corregir código
  → CI pasa → reviewer aprueba
```

## P3. Nueva tecnología

```
Discovery en Issue o spec
  → DISCOVERY.md con opciones
  → ADR en specs/adr/<n>-<decision>/
  → Si se aprueba ADR: crear spec de migración
  → Si se rechaza: archivar ADR como rejected/
```

## P4. Onboarding de nuevo producto YAMI

```
1. Crear carpeta en apps/<producto>/
2. Crear spec en specs/<n>-<producto>/
3. Implementar con OpenCode
4. Deploy a Vercel (cada producto su propio proyecto)
5. Registrar en GBrain si aplica
```

## P5. Lección aprendida

```
Post-sprint:
  1. ¿Qué salió bien?
  2. ¿Qué salió mal?
  3. ¿Qué haríamos diferente?
  4. Escribir en memory/lecciones.json
  5. Si el patrón se repite 3+ veces: promover a memory/patrones.md
```
