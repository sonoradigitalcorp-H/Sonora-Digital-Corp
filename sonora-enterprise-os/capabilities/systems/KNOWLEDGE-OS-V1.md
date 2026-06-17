# KNOWLEDGE OS V1 — Sonora Digital Corp

**Propósito**: El conocimiento del negocio no se pierde. No depende de tu memoria.

---

## REALIDAD

Tu knowledge management técnico (Neo4j + Qdrant + Engram) es excelente.
Tu knowledge management de **negocio** no existe.

## LO QUE NECESITAS SABER (y no está en ningún lado)

| Área | Dónde está ahora | Dónde debería estar |
|------|-----------------|-------------------|
| Quién es cada cliente | Tu cabeza | `clients/<cliente>/profile.md` |
| Qué compró cada cliente | Tu cabeza | `clients/<cliente>/contract.md` |
| Problemas de clientes | Tu cabeza | `clients/<cliente>/issues.md` |
| Lecciones de ventas | En ningún lado | `systems/SALES-OS-V1.md` — sección lecciones |
| Competencia | En ningún lado | `company/competitors.md` |
| Pricing decisions | Tu cabeza | `systems/REVENUE-OS-V1.md` |
| Contactos | Telegram + cabeza | `company/contacts.md` |

## KNOWLEDGE STRUCTURE

```
/knowledge/
├── clients/                    # Un archivo por cliente
│   └── abe-music.md
├── market/
│   ├── icp.md                  # Ideal Customer Profile
│   ├── competitors.md          # Competencia directa
│   └── positioning.md          # Cómo te diferencias
├── sales/
│   ├── objections.md           # Objeciones comunes + respuestas
│   ├── lessons.md              # Lecciones aprendidas en ventas
│   └── scripts.md              # Scripts que funcionaron
├── product/
│   ├── roadmap.md              # Lo que sigue (solo lo que tiene clientes)
│   ├── pricing-history.md      # Cambios de precio + resultados
│   └── feedback.md             # Feedback de clientes
└── founder/
    ├── decisions.md            # Decisiones importantes + por qué
    └── time-log.md             # Dónde inviertes tiempo
```

## CRITICAL: BUSINESS FAILURES

Por cada error de negocio (cliente perdido, venta fallida, propuesta rechazada):

```markdown
# Post-mortem: [Fecha] — [Situación]

## Qué pasó
[Descripción]

## Por qué pasó
[Causa raíz: ¿no calificamos? ¿precio? ¿timing?]

## Qué aprendí
[Lección]

## Qué haré diferente
[Acción concreta]

## Sistema que cambia
[¿Qué documento/proceso actualizar?]
```

## WEEKLY KNOWLEDGE REVIEW (domingo, 30 min)

1. ¿Qué aprendí esta semana sobre clientes?
2. ¿Qué aprendí sobre ventas?
3. ¿Qué aprendí sobre mi producto?
4. ¿Algo que documentar en alguna parte?

## REGLAS

1. **Si no está escrito, no lo sabes.** Documenta decisiones de negocio como documentas decisiones técnicas (ADRs).
2. **Cada cliente tiene un archivo.** Sin excepción.
3. **Cada error se documenta.** Sin excepción.
4. **Knowledge de negocio > knowledge técnico** para los próximos 90 días.
