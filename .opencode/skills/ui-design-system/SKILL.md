---
name: ui-design-system
description: "Aplicar design tokens y componentes de Sonora Digital Corp a cualquier interfaz."
version: 1.0.0
---

# UI Design System

**Propósito**: Garantizar consistencia visual en TODAS las interfaces del ecosistema.

## Design Tokens

Cargar desde `/home/mystic/jarvis/config/design-tokens.json`

### Uso obligatorio

1. **Colores**: Usar SOLO los colores definidos en design-tokens.json
2. **Tipografía**: Seguir la escala tipográfica (1.25 ratio)
3. **Espaciado**: Usar SOLO los valores de spacing scale
4. **Border radius**: sm(8), md(12), lg(16), xl(20), full(9999)

## Componentes Reutilizables

### Card
```css
.card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 24px;
  transition: all 0.3s ease;
}
.card:hover {
  border-color: rgba(0,212,255,0.3);
  transform: translateY(-4px);
}
```

### Button Primary
```css
.btn-primary {
  background: linear-gradient(135deg, #00d4ff, #7b2ff7);
  color: #fff;
  border-radius: 12px;
  padding: 16px 32px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}
```

### Grid Layout
```css
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; }
```

## Reglas

1. NO usar colores fuera del design system
2. NO usar frameworks pesados (React, Vue, Angular) para páginas simples
3. Three.js SOLO para visualizaciones 3D
4. D3.js SOLO para gráficos de datos
5. Vanilla CSS para todo lo demás
6. Mobile-first, responsive con grid auto-fit
