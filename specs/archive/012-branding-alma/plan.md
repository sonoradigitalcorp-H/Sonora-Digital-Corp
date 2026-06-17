# Implementation Plan: Branding y Alma del Sistema

**Spec**: spec.md

---

## Constitution Check

| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | Branding en prompts/ y system prompt, no en lógica |
| Privacidad y control | Identidad local, sin telemetría |
| Arquitectura modular | Prompts intercambiables por canal |
| Calidad y testing | Tests de system prompt con mock LLM |

## Archivos

| Archivo | Propósito |
|---------|-----------|
| `prompts/soul/v1.0-soul-prompt.md` | Prompt principal de Mystic |
| `prompts/soul/v1.0-mystic-image-prompt.md` | Prompt de generación de imagen |
| `webui/fastapp.py` | System prompt inline para Mystic |
| `.opencode/agents/mystic.md` | Config de agente Mystic en opencode |

---

*Plan generated from spec*
