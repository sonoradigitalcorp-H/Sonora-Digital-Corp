# speckit.analyze

**Description**: Validación cruzada: constitución + spec + plan.

**Usage**: `/speckit.analyze <spec-id>`

**Prompt**:
```
Eres un validador de consistencia. Verifica que la SPEC {spec-id} y su plan sean consistentes con la constitución.

Pasos:
1. Lee `.specify/memory/constitution.md`
2. Lee `process/active/SPEC-{spec-id}.md`
3. Lee `process/active/plan-{spec-id}.md`
4. Verifica consistencia:
   - ¿La SPEC respeta las invariantes de negocio?
   - ¿El plan cubre todos los requerimientos funcionales?
   - ¿El plan respeta los gates de la constitución?
5. Reporta violaciones (si hay) o genera SCORE-{spec-id}.md con aprobación
6. Output: `process/active/SCORE-{spec-id}.md`
```
