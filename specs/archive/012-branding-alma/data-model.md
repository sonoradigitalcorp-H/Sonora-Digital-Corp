# Data Model: Branding y Alma
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| SoulPrompt | id, version, content, tone, rules | Prompt del alma del sistema |
| BrandVoice | id, name, tone, audience | Voz de marca |
| TelegramBot | id, token, username, webhook, status | Bot de Telegram desplegado |
## Relaciones
```
(SoulPrompt)-[:DEFINES]->(BrandVoice)
(BrandVoice)-[:EXPRESSED_VIA]->(TelegramBot)
```
