# Lección — SPEC-20260721-MYSTIC-SHIELD

| Campo | Valor |
|-------|-------|
| **Spec** | `SPEC-20260721-MYSTIC-SHIELD` |
| **Tier** | 3 |
| **Fecha** | 2026-07-21 |

---

## ¿Qué pasó?

Se construyó el MVP de Mystic Shield en ~2 horas: un servicio SaaS de diagnóstico de ciberseguridad con IA que escanea la red del cliente, analiza con LLM, genera PDF + audio, y envía al CEO por WhatsApp y Email.

---

## ¿Qué salió bien?

- [x] Pipeline completo funcional: scan → analyze → PDF → audio → WA → Email
- [x] Código modular: MCP server reutilizable + FastAPI + landing estática
- [x] Fix de async bug en edge-tts (asyncio.run dentro de event loop)
- [x] Fix de LLM error handling (OpenRouter response sin 'choices')
- [x] Fix de opencode.json (paths rotos a sonora-enterprise-os/)
- [x] Landing profesional dark-mode con planes de precios
- [x] Captura de leads con notificación al admin

---

## ¿Qué salió mal?

- [ ] Ping sweep sobre 127.0.0.1 escanea todo el /24 (254 IPs locales) — no hay daño pero es ruido
- [ ] Audio skipping cuando edge-tts tarda >10s — considerar timeout más largo
- [ ] Sin tests unitarios todavía
- [ ] Sin deploy a VPS — solo probado local
- [ ] El escaneo de puertos es TCP connect (lento) — naabu SYN scan sería 10x más rápido

---

## ¿Qué haríamos diferente?

- Usar Naabu para port scan en vez de socket.connect() — 10x más rápido
- Agregar Redis queue desde el inicio si anticipamos >5 clientes
- Tests unitarios primero (TDD) ahorraría debug de async
- Configurar SMTP real en lugar de localhost:25

---

## Engram Tags

mystic-shield, security, mvp, saas, ciberseguridad, diagnostico-automatico, openclaw-skill
