# speckit.clarify

**Description**: Quality gate: resuelve ambigüedades en la SPEC.

**Usage**: `/speckit.clarify <spec-id>`

**Prompt**:
```
Eres un revisor de calidad. Revisa la SPEC {spec-id} en `process/active/SPEC-{spec-id}.md`.

Pasos:
1. Lee la SPEC completa
2. Identifica marcadores `[NEEDS CLARIFICATION]` o ambigüedades
3. Para cada ambigüedad, genera una pregunta al usuario
4. El usuario responde; actualiza la SPEC con la respuesta
5. Si no hay ambigüedades, reporta "SPEC clara — sin ambigüedades"
6. Actualiza `.specify/memory/context.md`
```
