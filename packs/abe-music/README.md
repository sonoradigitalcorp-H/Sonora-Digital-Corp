# ABE Music OS

Sistema operativo de agentes para artistas musicales.

## Agentes

| Agente | Skills | Canales |
|---|---|---|
| Asistente Ejecutivo | finance, promotion | WhatsApp, Telegram, Voz |
| Marketing | promotion, releases | WhatsApp, Telegram |
| Booking | booking | Voz, WhatsApp |

## Skills

| Skill | Acciones |
|---|---|
| streams | consultar, analizar, reportar streams por plataforma |
| releases | programar, notificar, distribuir lanzamientos |
| promotion | crear campañas, programar ads, medir ROI |
| booking | gestionar agenda, cotizar, confirmar fechas |
| finance | registrar ingresos/gastos, generar reportes, conciliar |

## Canales

- WhatsApp Business API
- Voz (Twilio / Voximplant)
- Telegram Bot

## Despliegue

```bash
./scripts/deploy-pack.sh --pack packs/abe-music --tenant "ABE Music"
```
