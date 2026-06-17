---
name: d3-visualization
description: "Crear gráficos y visualizaciones de datos con D3.js."
version: 1.0.0
---

# D3.js Visualization

**Propósito**: Visualizar datos del ecosistema (métricas, stats, analytics).

## Setup

```html
<script src="https://d3js.org/d3.v7.min.js"></script>
```

## Gráficos Estándar

### 1. Bar Chart (métricas)
```javascript
const svg = d3.select("#chart").append("svg").attr("width", w).attr("height", h);
svg.selectAll("rect").data(data).enter().append("rect")
  .attr("x", (d, i) => i * barWidth)
  .attr("y", d => h - d.value)
  .attr("width", barWidth - 2)
  .attr("height", d => d.value)
  .attr("fill", "#00d4ff");
```

### 2. Line Chart (tendencias)
```javascript
const line = d3.line().x(d => x(d.date)).y(d => y(d.value));
svg.append("path").datum(data).attr("d", line).attr("stroke", "#00d4ff");
```

### 3. Force Graph (relaciones)
```javascript
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).distance(100))
  .force("charge", d3.forceManyBody().strength(-300));
```

## Colores

Usar SOLO los colores del design system:
- Primary: #00d4ff
- Secondary: #7b2ff7
- Accent: #ff6b35
- Success: #4ade80
- Warning: #facc15
- Error: #f87171
