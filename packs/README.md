# Sonora Packs

Generador de packs de industria para Sonora Digital Corp.

Cada pack es un Sistema IA completo para un nicho: barberías,
pastelerías, clínicas dentales, etc. Incluye agents, skills,
prompts, seed data y dashboard.

## Uso

```bash
cd sonora-packs

opencode --agent sdc-pack-generator \
  "Crea el pack barbershop para México. \
   Canales: WhatsApp y voz. \
   Agentes: ventas, producción, contabilidad. \
   Skills: citas, inventario, precios, facturación, marketing."
```

## Estructura

```
sonora-packs/
├── .opencode/agents/       ← Agents que usa OpenCode
├── .opencode/skills/       ← Skills para generar packs
├── templates/              ← Templates base de packs
├── core-reference/         ← Docs y ejemplos del core
├── scripts/                ← Deploy y validación
├── generated/              ← Packs generados aquí
└── opencode.jsonc          ← Config de OpenCode
```

## Modelos

- Default: `opencode/deepseek-v4-flash-free`
- Tareas complejas: `opencode/kimi-k2.6`
