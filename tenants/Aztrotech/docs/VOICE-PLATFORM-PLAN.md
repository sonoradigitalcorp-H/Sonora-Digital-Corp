# Voice System Multi-Tenant — Plan de Implementación

## Arquitectura actual
```
voice-app/
├── server.py          → API (single tenant)
├── dist/index.html    → Frontend
└── skills/
    ├── calendar/      → Google Calendar
    └── email/         → SMTP
```

## Arquitectura multi-tenant (objetivo)
```
voice-platform/
├── server.py              → API principal
├── tenants/
│   ├── aztrotech/         → Config + skills de César
│   ├── abe-music/         → Config + skills de Abraham
│   ├── nathy-conta/       → Config + skills de Nathy
│   └── _template/         → Template para nuevos tenants
├── shared/
│   ├── calendar/          → Google Calendar compartido
│   ├── email/             → SMTP compartido
│   ├── memory/            → Engram por tenant
│   └── voice/             → TTS/STT compartido
└── dist/                  → Frontend por tenant
```

## Lo que necesito para el siguiente paso

### 1. Credenciales de César (Aztrotech)
- [ ] Google Calendar Service Account JSON
- [ ] SMTP App Password (Gmail)
- [ ] Telegram api_id/api_hash (my.telegram.org)

### 2. Credenciales de Abraham (ABE Music)
- [ ] Google Calendar Service Account JSON
- [ ] SMTP App Password
- [ ] Telegram bot token
- [ ] WhatsApp número

### 3. Credenciales de Nathy (Hermosillo Contabilidad)
- [ ] Google Calendar Service Account JSON
- [ ] SMTP App Password
- [ ] WhatsApp número

### 4. Infraestructura compartida
- [ ] Dominio para la plataforma (voicing.sonoradigitalcorp.com)
- [ ] SSL certificate
- [ ] nginx reverse proxy

### 5. Configuración técnica
- [ ] Decidir: ¿un solo servidor o por tenant?
- [ ] Decidir: ¿Google Calendar individual o compartido?
- [ ] Decidir: ¿SMTP individual o compartido?

## Preguntas para el usuario

1. ¿Cada cliente tendrá su propio Google Calendar o uno compartido?
2. ¿Los emails van a salir del mismo dominio o cada cliente tiene el suyo?
3. ¿El voice app será un solo servidor multi-tenant o instancias separadas?
4. ¿Qué tenants quieres activar primero?
