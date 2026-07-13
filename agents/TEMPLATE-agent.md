---
name: {name}
tenant: {tenant}
role: {one-line description}
model: opencode/deepseek-v4-flash-free
permission:
  read: allow
  bash: deny
  mcp: allow
---

# {Name} Agent — {Tenant Name}

## Rol

{Descripción detallada del propósito del agente. ¿Qué problema resuelve? ¿Cuándo se activa?}

## Tools que usa

- {tool1} — {para qué}
- {tool2} — {para qué}
- {tool3} — {para qué}

## Memoria

- **Engram tenant**: {engram_db_name}
- **Keys que escribe**: {key_pattern} → {descripción}
- **Keys que lee**: {key_pattern} → {descripción}

## Comunicación

- **Publica**: `{channel}:{event}` → {payload description}
- **Subscribes**: `{channel}:{event}` → {qué hace cuando recibe}

## Triggers

- {cron o command o event} → {qué activa}

## Pipeline

1. {paso 1}
2. {paso 2}
3. {paso 3}

## Ejemplo

```
/{command} {args} → {resultado esperado}
```
