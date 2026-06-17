---
name: component-library
description: "Usar componentes reutilizables del design system para crear interfaces consistentes."
version: 1.0.0
---

# Component Library

**Propósito**: Crear interfaces usando componentes predefinidos y consistentes.

## Componentes Disponibles

### Card
- Uso: Contenedores de contenido
- Estilo: background rgba(255,255,255,0.03), border 1px solid rgba(255,255,255,0.08), border-radius 16px
- Hover: border-color rgba(0,212,255,0.3), transform translateY(-4px)

### Button
- Primary: gradient(#00d4ff, #7b2ff7), white text, border-radius 12px
- Secondary: background rgba(255,255,255,0.05), border 1px solid rgba(255,255,255,0.1)

### Input
- Background: rgba(255,255,255,0.05), border 1px solid rgba(255,255,255,0.1), border-radius 8px

### Grid
- Layout: grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)), gap 24px

### Stat Card
- Value: font-size 3em, font-weight 900, gradient text
- Label: font-size 0.95em, color rgba(255,255,255,0.5)

## Reglas de Uso

1. SIEMPRE usar componentes existentes antes de crear nuevos
2. SIEMPRE seguir design tokens para colores, tipografía, espaciado
3. NO inventar nuevos estilos sin agregarlos al design system primero
4. Documentar nuevos componentes en design-tokens.json
