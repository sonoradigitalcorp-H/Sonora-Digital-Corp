# SDC Agent OS — Pipelines Completos

## Mapa de Skills → Agentes → Comandos → CRON

```
SKILL                  AGENTE QUE USA     COMANDO          CRON
─────────────────────────────────────────────────────────────────────
lovable               mystic/builder      /lovable         on-demand
creator               mystic              /crear           on-demand
content               content-agent       /generar         06:00 🎬
design                mystic              /design          on-demand
analytics             ceo-agent           /report          08:00 📊
social                marketing-agent     /tendencias      10:00 🌐
payments              sales-agent         /reconciliar     12:00 💳
monitor               monitor-agent       /status          */5 🔍
deploy                creator-agent       /deploy          on-demand
```

## CRON Schedule

```
00 06 * * *   daily-content   → content skill        → genera videos del día
00 08 * * *   daily-analytics → analytics skill       → reporte de revenue
00 10 * * *   daily-social   → social skill           → tendencias y contenido
00 12 * * *   daily-payments → payments skill         → reconciliación de pagos
*/5 * * * *   health-check   → monitor skill          → verificar servicios
00 12 * * 0   weekly-review  → quality skill          → self-improvement semanal
```

## Comandos OpenCode

| Comando | Skill | Descripción |
|---------|-------|-------------|
| `/generar` | content | Genera contenido diario para artistas |
| `/report` | analytics | Reporte de revenue y métricas |
| `/tendencias` | social | Analiza tendencias del momento |
| `/reconciliar` | payments | Revisa y reconcilia pagos |
| `/status` | monitor | Healthcheck del sistema |
| `/deploy` | deploy | Deploya nueva app o landing |
| `/design` | design | Componente UI con shadcn |
| `/crear` | creator | Crea empresa agent-native |
