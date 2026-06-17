# Implementation Plan: Content Creation Pipeline

**Spec**: spec.md

## Technical Context
- **Video**: Fal.ai API + Playwright
- **Audio**: Edge-TTS + Whisper STT
- **Text**: DeepSeek V4 + Engram
- **Automation**: n8n + cron + GitHub Actions
- **Delivery**: Telegram + Email + Web + WhatsApp

## Constitution Check
| Principio | Cómo lo cumple |
|-----------|---------------|
| Separación de responsabilidades | LLM escribe guiones, Fal.ai genera video, n8n orquesta |
| Privacidad y control | Contenido local, solo APIs externas para generación |
| Arquitectura modular | Cada formato es un skill independiente |
| Calidad y testing | Tests unitarios para cada paso del pipeline |

## Implementation Phases
### Phase 1: Daily Pipeline
- [ ] n8n workflow: Daily Content Generator
- [ ] Cron: 6AM research, 7AM script, 8AM video, 9AM audio, 10AM deliver

### Phase 2: Multi-format
- [ ] Video → Podcast conversion
- [ ] Article → Infographic
- [ ] Multi-language support

### Phase 3: Multi-channel
- [ ] Email via Brevo
- [ ] Telegram broadcast
- [ ] Ghost CMS publish
