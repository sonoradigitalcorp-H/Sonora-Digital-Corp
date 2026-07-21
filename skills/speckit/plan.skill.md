# speckit.plan

**Description**: Crea plan de implementación desde la SPEC.

**Usage**: `/speckit.plan <spec-id>`

**Prompt**:
```
Eres un arquitecto de software. Crea un plan de implementación para la SPEC {spec-id}.

Pasos:
1. Lee `process/active/SPEC-{spec-id}.md`
2. Lee `.specify/templates/plan-template.md` para el formato
3. Evalúa complejidad técnica (baja/media/alta)
4. Crea `process/active/plan-{spec-id}.md` con:
   - Resumen técnico
   - Stack tecnológico (lenguaje, frameworks, almacenamiento)
   - Constitution Check (gates que debe pasar)
   - Estructura de proyecto
   - Complexity Tracking
5. Incluye referencias a `skills/index.yaml` para capacidades existentes
```
