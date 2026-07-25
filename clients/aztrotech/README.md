# AztroTech — Cliente

Cliente empresarial: César Holguín — CEO de AztroTech.mx

## Estructura

```
clients/aztrotech/
├── README.md           ← Este archivo
├── ai/                 ← Configuración de AI (persona, secrets, modelo)
│   ├── config.yaml     ← Config general del tenant
│   ├── persona.md      ← Personalidad de Mystic
│   └── secrets.yaml    ← Tokens y secrets (NO COMMIT)
├── booking/            ← Sistema de booking (calendario + API)
│   ├── models.py       ← Modelos de datos
│   ├── store.py        ← Persistencia (JSON)
│   ├── availability.py ← Lógica de disponibilidad
│   ├── booking_flow.py ← Flujo de agendamiento
│   ├── api_server.py   ← API REST (puerto 8901)
│   ├── notify.py       ← Notificaciones a César
│   └── data/
│       └── bookings.json ← Base de datos de citas
├── telegram/           ← Bot de Telegram @Aztro_tech_bot
│   ├── bot.py          ← Bot Mystic con conversación GPT vía OpenRouter
│   ├── .env            ← Variables de entorno (OPENROUTER_API_KEY, 600)
│   └── bot.log         ← Logs del bot
├── whatsapp/           ← Integración WhatsApp (wacli)
│   └── sync.sh         ← Script de sync (opcional)
├── voice/              ← Voz y clonación
│   ├── cesar/          ← Voz de César
│   │   ├── original/   ← Audio original (cesar-audio.f4a, 2:46, WhatsApp)
│   │   └── processed/  ← Audio procesado (cesar-audio-16khz.wav, listo para clonar)
│   ├── tts.py          ← Interfaz unificada de TTS (futuro)
│   └── stt.py          ← Whisper STT wrapper (futuro)
├── branding/           ← Assets visuales
│   ├── cesar/          ← Fotos de César
│   │   ├── avatar.jpg  ← Foto seleccionada para avatar del bot
│   │   └── originals/  ← 9 fotos originales de WhatsApp
│   └── logo/           ← Logo de AztroTech
├── realtime-voice/     ← Llamadas de voz en tiempo real (en planeación)
│   └── README.md       ← Arquitectura y plan de implementación
├── data/               ← Datos de negocio
│   ├── catalog.md      ← Catálogo de servicios
│   ├── faq.md          ← Preguntas frecuentes
│   └── services.md     ← Descripción de servicios
├── scripts/            ← Scripts utilitarios
├── services/           ← Archivos de servicio (local)
└── memory/             ← Memoria del agente
```

## Servicios activos

| Servicio | Puerto | Systemd | Estado |
|----------|--------|---------|--------|
| Calendar API | 8901 | `sdc-aztrotech-calendar` | ✅ Running |
| Telegram Bot | — | `sdc-aztrotech-telegram` | ✅ Running |
| WhatsApp Sync | — | `whatsapp-sync` (user) | ✅ Running |

## URLs

- Web calendario: https://calendario.sonoradigitalcorp.com
- Bot Telegram: https://t.me/Aztro_tech_bot
- WhatsApp César: https://wa.me/526621072254

## Próximos pasos

1. Clonar voz de César con Qwen3-TTS
2. Construir servidor WebSocket para voz en tiempo real
3. Frontend web con orb y micrófono
4. Integrar llamadas de voz en flujo de booking
