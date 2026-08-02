# Feature Specification: Sistema Autónomo 24/7

**Feature**: 017-autonomous-system
**Created**: 2026-06-10
**Status**: Active
**Input**: Sistema de agentes autónomos que trabajan 24/7 sin intervención del usuario.

---

## Objetivo

Crear un sistema que:
1. Ejecute tareas de forma autónoma (healthchecks, backups, ideas, tests)
2. Procese ideas del usuario con un pipeline riguroso (investigar→prototipar→testear→reportar)
3. Verifique cada afirmación antes de comunicarla al usuario
4. Ahorre tokens al máximo (cache, skills, modelos locales)
5. Aprenda de errores pasados y no los repita

---

## Principios de Funcionamiento (no negociables)

### 1. Verificación antes de Afirmación
- Ninguna afirmación de "funciona" se hace sin antes ser probada físicamente
- Prohibido: "HTTP 200 = funciona". HTTP 200 solo significa "respondió"
- Cada endpoint debe ser probado con contenido real, no solo código de estado

### 2. Pipeline de Ideas
- Toda idea pasa por: Investigar → Prototipar → Testear → Reportar → Aprobar → Commit/Archivar
- No se salta pasos. No se optimiza antes de tiempo.
- Si algo falla: se archiva en Engram con la razón del fallo.

### 3. Autonomía 24/7
- Healthchecks cada 15 minutos
- Procesamiento de ideas cada hora
- Backup diario a las 3 AM
- Reporte semanal los lunes 9 AM
- Cleanup automático de logs y backups viejos

### 4. Ahorro de Tokens
- Cachear respuestas comunes en Engram
- Detectar patrones repetitivos y convertirlos en skills (0 tokens)
- Usar comandos shell en lugar de LLM para tareas simples
- Batch de operaciones para reducir llamadas

---

## Componentes del Sistema

### Skills de OpenCode (3 nuevas)

| Skill | Propósito | Archivo |
|-------|-----------|---------|
| self-verifier | Verificar antes de afirmar | `.opencode/skills/self-verifier/SKILL.md` |
| idea-protocol | Pipeline de ideas | `~/.config/opencode/skills/idea-protocol/SKILL.md` |
| token-saver | Optimizar tokens | `~/.config/opencode/skills/token-saver/SKILL.md` |

### Scripts de Automatización

| Script | Propósito | Schedule |
|--------|-----------|----------|
| `scripts/autonomous.sh` | Ciclo autónomo 24/7 | Cada 15 min |
| `scripts/install-cron.sh` | Instalar cron jobs | Una vez |
| `scripts/backup.sh` | Backup con evidencia de errores | Diario 3 AM |

### Specs Relacionados

| Spec | Propósito |
|------|-----------|
| 016 | SDD Agent Harness (pipeline de fases) |
| 017 | Sistema Autónomo 24/7 (este) |

---

## Reglas de Operación (para mí y futuros agentes)

### Lo que NO debo hacer nunca más

1. ❌ Decir que algo funciona sin haberlo probado yo mismo
2. ❌ Confiar en HTTP codes como única métrica
3. ❌ Overpromising ("todo está listo")
4. ❌ Omitir errores o bugs conocidos
5. ❌ Saltarme pasos del pipeline SDD

### Lo que DEBO hacer siempre

1. ✅ Verificar cada endpoint con contenido real antes de reportar
2. ✅ Si hay error: mostrar el error exacto, no esconderlo
3. ✅ Si no sé: decir "no lo sé, voy a verificarlo"
4. ✅ Cada afirmación respaldada con evidencia (logs, capturas)
5. ✅ Commit de cada cambio significativo con mensaje SDD

---

## Criterios de Éxito

- [ ] 0 afirmaciones falsas sobre el estado del sistema
- [ ] Pipeline de ideas ejecutándose autónomamente
- [ ] Ahorro de tokens >50% en tareas repetitivas
- [ ] Backup automático funcionando sin intervención
- [ ] Sistema autónomo ejecutándose 24/7 vía cron

---

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|--------|------------|
| Afirmaciones falsas por no verificar | Skill self-verifier obligatorio antes de cada reporte |
| Gasto excesivo de tokens | Cache en Engram + detección de patrones repetitivos |
| Sistema autónomo causando errores | Lock file evita ejecución simultánea; logs de cada acción |
| Pérdida de datos por backup mal hecho | Backup.sh tiene manifiesto + log de errores + verificación |

---

**Spec**: spec.md  
**Plan**: plan.md  
**Tasks**: tasks.md  
**Checklist**: checklist.md  
**Status**: ✅ Activo  
