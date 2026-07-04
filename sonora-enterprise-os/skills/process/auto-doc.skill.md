# Auto-Doc

**Parent OS**: Knowledge OS
**Tier**: 2
**Description**: Genera documentación de proceso (SPEC, SCORE, ADR, LECCION, gherkin, events) desde resumen de sesión

## Usage
- `python3 scripts/auto-doc.py --auto`
- `python3 scripts/auto-doc.py --spec-id {ID} --title "{title}" --tier {1-3} --summary "{summary}"`

## Templates
- `process/templates/SPEC.md`
- `process/templates/SCORE.md`
- `process/templates/ADR.md`
- `process/templates/LECCION.md`
- `process/templates/EVENT.md`
- `process/templates/GHERKIN.md`

## Output Directory
`process/completed/{SPEC-ID}/`
