# Instrucciones de Sincronización

Este vault se sincroniza automáticamente desde Engram (memoria persistente).

## Sincronización Manual

```bash
bash ~/sonora-digital-corp/scripts/sync-brain-vault.sh
```

## Comandos Rápidos

- `brain-sync` → Sincroniza Engram → Obsidian
- `brain-open` → Abre Obsidian con este vault
- `brain-status` → Muestra estado del cerebro digital

## Plugins Recomendados

- **Dataview** — Consultas SQL sobre tus notas
- **Templater** — Templates avanzados
- **Graphviz** — Visualización de grafos
- **Kanban** — Boards de proyectos

## Estructura del Vault

```
sdc-brain-vault/
├── Dashboard/        ← Panel principal
├── Observations/     ← Engram auto-export
├── Sessions/         ← Historial de sesiones
├── Projects/         ← Proyectos activos
├── People/           ← Contactos y personas
├── Decisions/        ← Decisiones arquitectónicas
├── Learnings/        ← Aprendizajes y descubrimientos
├── Graph/            ← Relaciones entre nodos
├── Canvas/           ← Mapas visuales
└── Templates/        ← Plantillas para nuevos nodos
```
