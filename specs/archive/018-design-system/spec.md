# Feature Specification: Design System & UI Standards

**Feature**: 018-design-system
**Created**: 2026-06-10
**Status**: Active
**Input**: Sistema de diseño unificado para todo el ecosistema JARVIS/Sonora Digital Corp.

---

## Objetivo

Crear un patrón de creación consistente para TODAS las interfaces del ecosistema:
- Web UI
- Tienda
- Dashboard
- Páginas de productos
- Presentaciones
- Cualquier nueva interfaz

---

## Problemática Actual

| Problema | Impacto |
|----------|---------|
| Cada página usa estilos diferentes | Inconsistencia visual |
| No hay design tokens | Colores, tipografía, espaciado arbitrarios |
| No hay componente library | Código duplicado |
| No hay skill de UI/UX | Cada agente inventa su propio diseño |
| No hay spec de frontend | Sin estándares de calidad visual |

---

## Design Tokens (estándar para TODO)

### Colores
```json
{
  "primary": "#00d4ff",
  "secondary": "#7b2ff7",
  "accent": "#ff6b35",
  "success": "#4ade80",
  "warning": "#facc15",
  "error": "#f87171",
  "background": "#0a0a1a",
  "surface": "rgba(255,255,255,0.03)",
  "text": "#e0e0e0",
  "text-muted": "rgba(255,255,255,0.5)"
}
```

### Tipografía
- Font family: `'Segoe UI', system-ui, sans-serif`
- Headings: 800 weight
- Body: 400 weight, 1.6 line-height
- Scale: 1.25 ratio (1rem, 1.25rem, 1.563rem, 1.953rem, 2.441rem, 3.052rem)

### Espaciado
- Base: 8px
- Scale: 8, 16, 24, 32, 48, 64, 96, 128

### Componentes
- Cards: border-radius 16px, border 1px solid rgba(255,255,255,0.08)
- Buttons: border-radius 12px, padding 16px 32px
- Inputs: border-radius 8px, border 1px solid rgba(255,255,255,0.1)

---

## Tech Stack Estándar

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| 3D/Visual | Three.js (r128) | Partículas, escenas 3D, interactividad |
| UI Framework | Vanilla + CSS Grid | Sin dependencias pesadas, rápido |
| Animaciones | CSS animations + JS | Performance nativa |
| Charts | D3.js (v7) | Visualización de datos |
| Icons | Unicode emojis | Sin dependencias externas |

**Prohibido**: React, Vue, Angular para páginas simples. Solo Three.js + D3.js para visualizaciones.

---

## Skills de UI/UX (nuevas)

| Skill | Propósito | Archivo |
|-------|-----------|---------|
| ui-design-system | Aplicar design tokens y componentes | `.opencode/skills/ui-design-system/SKILL.md` |
| threejs-scene | Crear escenas 3D con Three.js | `.opencode/skills/threejs-scene/SKILL.md` |
| d3-visualization | Crear gráficos con D3.js | `.opencode/skills/d3-visualization/SKILL.md` |
| component-library | Usar componentes reutilizables | `.opencode/skills/component-library/SKILL.md` |

---

## Reglas de Creación

1. **Antes de crear cualquier UI**: Cargar design tokens
2. **Usar componentes existentes**: No reinventar
3. **Three.js solo para**: Visualizaciones 3D, partículas, escenas interactivas
4. **D3.js solo para**: Gráficos de datos, visualizaciones estadísticas
5. **Vanilla CSS para**: Todo lo demás
6. **Responsive**: Mobile-first, grid auto-fit
7. **Performance**: Sin frameworks pesados, CDN solo para Three.js/D3.js

---

## Criterios de Éxito

- [ ] Todas las páginas usan los mismos design tokens
- [ ] Componentes reutilizables documentados
- [ ] Skills de UI/UX creadas y funcionales
- [ ] Páginas existentes migradas al design system
- [ ] Spec 018 completa con plan, tasks, checklist

---

**Spec**: spec.md
**Plan**: plan.md
**Tasks**: tasks.md
**Checklist**: checklist.md
**Research**: research.md
**Data Model**: data-model.md
**Contracts**: contracts/README.md
