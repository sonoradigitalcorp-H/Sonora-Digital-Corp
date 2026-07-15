# Agent Spec Reference para Pack Generator

## Formato completo

```yaml
nexus_agent_spec: "1.0"
id: {pack}.{agent_name}
name: Nombre
role: Rol descriptivo
version: 1.0.0
type: conversational | task | analyst | creative | support | orchestrator

runtime:
  model: opencode/deepseek-v4-flash-free
  temperature: 0.7
  max_tokens: 2048

system_prompt: |
  Prompt del agente en español.

skills:
  - {pack}.{skill1}
  - {pack}.{skill2}

channels:
  - whatsapp
  - voz

memory:
  working: true
  short_term: true
  long_term: true

handoffs:
  - to: {pack}.{other_agent}
    condition: "el usuario está frustrado o pide supervisor"

onboarding:
  questions:
    - "¿Cómo te llamas?"
    - "¿Qué servicios ofreces?"
    - "¿Cuál es tu horario?"

daily_briefing:
  time: "08:00"
  channel: whatsapp
  sections:
    - resumen_del_dia
    - metricas_clave
    - tareas_pendientes
    - alertas
    - sugerencias
```

## Reglas

- System prompt siempre en español y específico del nicho
- Skills listadas deben existir en el pack
- Canales: whatsapp, voz, telegram (mínimo 1)
- Handoff conditions son obligatorias
- Daily briefing template obligatorio
- Onboarding questions máximo 7
