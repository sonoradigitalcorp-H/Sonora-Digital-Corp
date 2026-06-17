# Data Model: Design System

**Spec**: spec.md

## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| DesignToken | name, value, category, description | Token de diseño reutilizable |
| Component | name, styles, variants, usage | Componente UI reutilizable |
| Page | url, components, tokens, threejs, d3 | Página web del ecosistema |

## Relaciones
```
(Page)-[:USES]->(Component)
(Component)-[:USES]->(DesignToken)
(Page)-[:HAS_THREEJS]->(ThreeScene)
(Page)-[:HAS_D3]->(D3Chart)
```
