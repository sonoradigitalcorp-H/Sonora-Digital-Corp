---
name: design
description: Generate premium UI components with shadcn/ui, three.js, Tailwind CSS. Use when the user asks to create a design, landing page, dashboard, hero section, or UI component. NOT for generating full apps — use lovable for that.
version: 1.0.0
updated: 2026-07-14
---

# Design Skill

Generate production-ready React/TypeScript components with shadcn/ui, @react-three/drei, framer-motion, and Tailwind CSS.

## Stack

| Library | Version | Uso |
|---------|---------|-----|
| `@shadcn/react` | latest | Componentes base (Button, Card, Dialog, Tabs, Table, etc.) |
| `@react-three/drei` | ^10 | Helpers 3D (Sparkles, Float, Text3D, Stars, MeshTransmissionMaterial, ContactShadows, Environment) |
| `@react-three/fiber` | ^9 | React renderer for Three.js |
| `framer-motion` | ^12 | Animaciones (layout, scroll, spring) |
| `lucide-react` | latest | Iconos |
| `tailwindcss` | ^4 | Estilos utilitarios |

## Output format

Cada componente es un archivo individual `.tsx`. Usar:

```tsx
import { Button } from '@shadcn/react'
import { Sparkles } from '@react-three/drei'
import { motion } from 'framer-motion'
import { Camera } from 'lucide-react'
```

## Patrones de diseño

### Glassmorphism
```tsx
<div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl shadow-2xl">
```

### Botón con gradiente gold
```tsx
<Button className="bg-gradient-to-r from-amber-500 to-yellow-500 hover:from-amber-600 hover:to-yellow-600 text-black font-semibold">
```

### Hero 3D con partículas
```tsx
import { Canvas } from '@react-three/fiber'
import { Sparkles, Float } from '@react-three/drei'

<section className="relative h-screen">
  <Canvas className="absolute inset-0">
    <Sparkles count={100} scale={2} size={2} />
    <Float speed={2}>
      <mesh>{/* geometry */}</mesh>
    </Float>
  </Canvas>
  <div className="relative z-10 flex items-center justify-center h-full">
    <h1 className="text-6xl font-bold">{/* title */}</h1>
  </div>
</section>
```

### shadcn Card con hover glass
```tsx
<Card className="backdrop-blur-md bg-white/5 border-white/10 hover:bg-white/10 transition-all">
  <CardHeader>
    <CardTitle>{title}</CardTitle>
    <CardDescription>{desc}</CardDescription>
  </CardHeader>
  <CardContent>{children}</CardContent>
</Card>
```

### Dashboard metric card
```tsx
<Card>
  <CardHeader className="flex flex-row items-center justify-between pb-2">
    <CardTitle className="text-sm font-medium">{label}</CardTitle>
    <Icon className="h-4 w-4 text-muted-foreground" />
  </CardHeader>
  <CardContent>
    <div className="text-2xl font-bold">{value}</div>
    <p className="text-xs text-muted-foreground">{change}</p>
  </CardContent>
</Card>
```

## Reglas

1. NO generar apps completas — solo componentes/páginas individuales
2. NO usar inline styles — siempre Tailwind classes
3. NO truncar código — siempre completo
4. Incluir imports exactos de cada librería
5. Dark mode por defecto (`dark` class en html)
6. Responsive mobile-first
7. Un componente por archivo
