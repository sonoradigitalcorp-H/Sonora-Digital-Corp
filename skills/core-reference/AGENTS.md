# Agentos Reference para Pack Generator

## Estructura de un Agent

```yaml
id: {pack}.{agent_name}
name: Nombre visible
role: Rol del agente
skills:
  - {pack}.{skill_name}
channels:
  - whatsapp
  - voz
  - telegram
model: opencode/deepseek-v4-flash-free
temperature: 0.7
memory:
  working: true
  long_term: true
handoff:
  to: {pack}.{other_agent}
  condition: "usuario frustrado o pide supervisor"
```

## Tipos de agentes disponibles

| Tipo | Descripción |
|---|---|
| conversational | Chat con memoria, el default |
| task | Ejecuta una tarea específica |
| analyst | Consulta datos y genera reportes |
| creative | Genera contenido (texto, imagen, video) |
| support | RAG + tickets + handoff |

## Reglas

- Siempre incluir system prompt en español
- No hardcodear API keys (usar env vars)
- Memory config debe incluir tenant isolation
- Handoff conditions en lenguaje natural
- Maximum 3 handoffs por agente
