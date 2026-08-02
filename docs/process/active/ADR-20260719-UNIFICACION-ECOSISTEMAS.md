# ADR — Unificación OpenClaw ↔ Hermes ↔ opencode

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260719-UNIFICACION-ECOSISTEMAS` |
| **Fecha** | 2026-07-19 |
| **Spec** | SPEC-20260719-UNIFICACION |
| **Estado** | activo |

## Contexto
El sistema tiene 3 ecosistemas de skills que no comparten formato ni registro:
- **OpenClaw**: 42 plugins instalados en VPS, solo 1 documentado en el repo (clone-service)
- **Hermes**: 12 Telegram skills en formato JSON, no reusables fuera de Telegram
- **opencode**: 10 skills skeleton incompletas (solo frontmatter)
- **skills/ root**: Skills en formato SDC pero sin estandarizar al template de 14 campos

## Decisión
1. **Estandarizar todas las skills al formato SKILL-TEMPLATE.md** (14 campos obligatorios)
2. **Convertir Hermes JSON a SKILL.md** manteniendo triggers y templates
3. **Documentar OpenClaw plugins como skills formales** con mapping a SDC tools
4. **Completar skills skeleton con contenido real** siguiendo el template
5. **Crear un Skill Registry central** (skills index) que liste todas las skills disponibles

## Opciones Consideradas
| Opción | Pros | Contras |
|--------|------|---------|
| **SKILL-TEMPLATE.md universal (elegido)** | Un solo formato para todo el ecosistema | Migración de skills existentes |
| Mantener 3 formatos distintos | Sin trabajo de migración | Inconsistencia, skills no reusables |
| Crear nuevo formato híbrido | Podría ser mejor | Más trabajo, otro estándar que mantener |

## Consecuencias
- Positivas: Cualquier skill puede ser usada por cualquier agente/canal
- Positivas: 14 campos aseguran documentación completa (business value, recovery, etc.)
- Trabajo: ~28 skills requieren migración/creación

## Lecciones
- El template de 14 campos es extenso pero garantiza skills production-ready
- Las skills skeleton existentes (analytics, payments, etc.) ya tienen herramientas y propósito definidos, solo falta estructura completa
