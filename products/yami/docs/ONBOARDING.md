# Onboarding — Noel

Bienvenide al ecosistema. Esto es lo que necesitas para empezar.

## 1. Clonar el repo

```bash
git clone https://github.com/perrykingla69-cyber/SonoraDigitalCorp-Yami.git
cd SonoraDigitalCorp-Yami
```

## 2. Instalar OpenCode

```bash
npm install -g @opencode/cli
```

Verifica: `opencode --version` → debe mostrar v1.x+

## 3. Configurar OpenCode

```bash
opencode init
# Elige OpenRouter como provider
# Ingresa tu API key de OpenRouter
# Elige tu LLM preferido (ej: Claude 3.5 Sonnet, DeepSeek V3, Qwen 2.5)
```

Config file: `~/.config/opencode/config.json`

## 4. Leer la constitución

- `constitution/TRUTH.md` — jerarquía de verdad
- `constitution/RULES.md` — 10 reglas absolutas
- `AGENTS.md` — quick reference del flujo

## 5. Flujo de trabajo

### Tú propones un spec
1. Creas una Issue con `feature request` template
2. Escribes el spec en `specs/<n>-<nombre>/spec.md`
3. Abres PR con el spec → yo lo reviso y apruebo
4. Implementas con OpenCode
5. Abres PR con la implementation → yo reviso y mergeo

### Yo propongo un spec
1. Igual pero al revés: yo escribo spec → tú apruebas → yo implemento → tú revisas

## 6. Reglas de PR

- Título: `[<tipo>] <descripción>` (tipo: spec, adr, feat, fix, chore)
- Siempre incluir test coverage
- CI debe pasar (lint + typecheck + tests)
- Esperar al menos 1 approval antes de mergear

## 7. Contacto

- GitHub Issues para discusión asíncrona
- WhatsApp para urgencias
- El bot de Telegram notificará cuando haya PRs nuevos o cambios de estado

## 8. LLM de preferencia

Tú eliges. Claude 3.5 Sonnet recomendado para code generation, DeepSeek para debugging. Todo via OpenRouter.
