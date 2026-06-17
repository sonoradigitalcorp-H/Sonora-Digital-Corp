---
id: 000
title: Constitución del Sistema
status: active
type: foundation
---

# Spec 000 — Constitución del Sistema

## Propósito
Documento fundacional que establece los principios, reglas y arquitectura del sistema JARVIS. Toda especificación debe pasar el **Constitution Check** antes de ser implementada.

## Principios
1. **Separación de Responsabilidades**: Lógica determinista vs LLM. El motor de decisión es 100% código, el LLM solo genera respuestas.
2. **Privacidad y Control Local**: Datos en máquina local. Solo conexión externa = LLM vía opencode-go.
3. **Arquitectura Modular**: Componentes independientes, Docker, comunicación vía REST/MCP.
4. **Calidad y Testing**: Cobertura mínima 80% en código determinista.
5. **SDD Obligatorio**: Spec → Plan → Tasks → Code → Verify → Commit. Sin excepción.

## Archivos
- `constitution.md` — Texto completo de la constitución
- `plan.md` — Plan de implementación
- `tasks.md` — Tareas
- `spec.md` — Este archivo

## Dependencias
- Ninguna (es el spec fundacional)

## Verification
- [ ] Constitution.md existe y está ratificado
- [ ] Todos los specs activos pasan Constitution Check
- [ ] Preflight corre sin errores
