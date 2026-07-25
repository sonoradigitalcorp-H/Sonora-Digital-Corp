# Playbooks — Sonora Digital Corp

Los playbooks son recetas paso a paso para que agentes (humanos o IA) ejecuten
procedimientos estandarizados. Cada playbook sigue el mismo formato:

```
## Goal
## Prerequisites
## Steps
## Verification
## Rollback
```

## Índice

| Playbook | Descripción |
|----------|-------------|
| `onboard-cliente.md` | Incorporar un nuevo cliente al sistema |
| `crear-producto.md` | Crear un nuevo producto SDC |
| `recuperacion-vps.md` | Recuperar VPS tras caída o OOM |

## Cómo crear un playbook nuevo

1. Copiar `_template.md` (próximamente)
2. Nombrar con kebab-case: `hacer-algo.md`
3. Incluir Goal, Prerequisites, Steps, Verification, Rollback
4. Registrar en este índice
