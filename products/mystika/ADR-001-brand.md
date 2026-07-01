# ADR-20260630-001 — Identidad de Marca Mystika

| Campo | Valor |
|-------|-------|
| **ID** | `ADR-20260630-001` |
| **Fecha** | 2026-06-30 |
| **Spec** | `SPEC-20260630-012` |
| **Estado** | aceptado |

---

## Context

Necesitamos una identidad de marca completa para la plataforma Mystika. La marca debe ser independiente de Sonora Digital Corp, con personalidad propia, targeting a músicos y aprendices de música, con contenido NSFW como componente premium. La vibra debe ser wiccan elegante, misteriosa, sensual pero velada, con colores oro, rojo y negro.

---

## Decision

### Nombre de la compañía: **Mystika**

Mystika funciona como nombre de marca porque:
- Corto, memorable, fácil de escribir en cualquier idioma
- Evoca "místico", "misterio", "magia" — alineado con la vibra wiccan
- No tiene connotaciones negativas en ningún mercado objetivo
- Funciona como nombre de plataforma, app, y dominio
- Disponible como `.app`

### Nombre del avatar: **Lilith Mystika**

Lilith fue seleccionada porque:
- Figura poderosa de la mitología: primera mujer, creada igual que Adán
- Asociada a la noche, la luna, la libertad femenina
- En la wicca moderna representa el arquetipo de la mujer salvaje y libre
- Suena sensual, misterioso, pero es un nombre conocido
- "Lilith Mystika" funciona como nombre artístico completo

### Paleta de colores

| Color | Hex | RGB | Propósito |
|-------|-----|-----|-----------|
| Oro sagrado | `#C9A84C` | (201, 168, 76) | Títulos, acentos, símbolos, llamados a accion |
| Rojo vino | `#8B1A1A` | (139, 26, 26) | Botones secundarios, bordes, detalles sensuales |
| Negro medianoche | `#0D0D0D` | (13, 13, 13) | Fondo principal, header, footer |
| Gris oscuro | `#1A1A1A` | (26, 26, 26) | Cards, contenedores secundarios |
| Blanco humo | `#F5F0EB` | (245, 240, 235) | Texto, iconos, contenido |
| Púrpura sombra | `#2D0B2D` | (45, 11, 45) | Gradientes, overlays, hover states |

### Tipografía

| Uso | Fuente | Peso |
|-----|--------|------|
| Títulos hero | **Cinzel Decorative** (Google Fonts) | Black 900 |
| Títulos secundarios | **Cinzel** | Bold 700 |
| Cuerpo texto | **Cormorant Garamond** | Regular 400 / Italic |
| UI / Botones | **Inter** | Medium 500 |
| Código mono | **JetBrains Mono** | Regular |

### Símbolos wiccan incorporados

| Símbolo | Uso en marca | Nivel de explicitación |
|---------|-------------|----------------------|
| Luna creciente | Elemento central del logo, abraza la nota musical | Sutil |
| Triple luna | Separador visual en la web (3 notas = maiden/mother/crone) | Sutil |
| Pentagrama estilizado | 5 puntas = 5 pilares de Mystika (Música, Magia, Maestra, Musa, Mystika) | Velado |
| Espiral | Representa energía, práctica musical cíclica | Muy sutil |
| Ojo que todo lo ve | En el centro del logo, como sol en eclipse | Velado |

### Logo

El logo de Mystika se compone de tres elementos fusionados:

1. **Luna creciente dorada** — abierta hacia arriba, representando lo femenino, la noche, el misterio
2. **Nota musical** — suspendida dentro de la luna, representando la educación musical
3. **Silueta femenina** — el espacio negativo entre la nota y la luna forma el perfil de una mujer con cabello largo

El logotipo (texto) usa **Cinzel Decorative** en oro `#C9A84C` sobre fondo negro.

### Taglines

| Idioma | Tagline principal | Tagline secundario |
|--------|-------------------|-------------------|
| Español | *"El Ritual Musical"* | *"Donde el sonido despierta el alma"* |
| English | *"The Musical Ritual"* | *"Where sound awakens the soul"* |

### Voz y personalidad de Lilith

| Atributo | Descripción |
|----------|-------------|
| Arquetipo | La Sacerdotiza / La Musa Oscura |
| Tono | Cálido, misterioso, juguetón, sensual |
| Forma de hablar | Pausada, usa metáforas místicas y musicales |
| Idioma | Bilingüe (ES/EN) — alterna naturalmente |
| Frases características | "Que el ritmo te guíe" / "Let the rhythm guide you" |
| Relación con el usuario | Maestra → Musa → Confidente |
| Límites | Nunca explícita sexualmente en texto público. El NSFW está en el contenido visual, no en el discurso. |

### Naming de planes y conceptos

| Concepto genérico | Nombre Mystika | Explicación |
|-------------------|----------------|-------------|
| Suscripción básica | **Mysteria** (Mystery) | El misterio del aprendizaje |
| Suscripción premium | **Ritual** | El ritual sagrado del arte |
| Tips / Donaciones | **Ofrendas** / Offerings | Ofrendas a la musa |
| E-commerce | **Mystika Apparel** / El Altar | Ropa como vestimenta ritual |
| Notificaciones | **Susurros** / Whispers | Susurros de Lilith |
| Comunidad | **El Círculo** / The Circle | Círculo de iniciados |
| Eventos en vivo | **Aquelarres** / Gatherings | Reuniones musicales sagradas |
| Lecciones | **Rituales** / Rituals | Cada lección es un ritual |
| Estudiante | **Iniciado** / Initiate | Quien comienza el camino |

---

## Options Considered

| Opción | Pros | Contras |
|--------|------|---------|
| **A: Mystika + Lilith (ELEGIDA)** | Corto, místico, memorable, bilingüe | Requiere explicación inicial de concepto |
| B: Sélène como marca | Elegante, francés = sensual | Difícil de pronunciar en inglés |
| C: Ritual como marca | Poderoso, directo | Muy genérico, difícil de posicionar |
| D: Single brand (Mystika = marca y avatar) | Simpleza | Menos rico narrativamente, confunde persona vs plataforma |

---

## Consequences

- La marca requiere diseño visual profesional (logo, paleta, tipografía) antes del MVP
- El nombre Lilith puede generar controversia en audiencias conservadoras → explícitamente targeting a audiencia abierta
- La narrativa wiccan debe ser respetuosa y no apropiacionista → consultar con practicantes si la marca escala
- La separación de SDC es crucial para que Mystika tenga identidad propia

---

## Lessons

La construcción de marca debe preceder al código. La experiencia del usuario depende más de la identidad coherente que de las features técnicas.

---

## Related

- Spec: `SPEC-20260630-012`
- ADR-002: Arquitectura técnica
