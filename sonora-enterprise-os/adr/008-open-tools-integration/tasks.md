---
id: 008
title: Open Tools Integration
---

# Tasks: Open Tools Integration

## Fase 1 — Instalación (3 tasks, 0.5d)

### [ ] 008-01: Descargar e instalar Open Design
- Descargar OD desde open-design.ai o GitHub Releases
- `od mcp install hermes` para integrar con JARVIS
- Verificar: `od --version` y `od search-files "landing"` funciona
- **File:** `services/open-design/INSTALL.md`
- **Verify:** OD responde en puerto 7456

### [ ] 008-02: Instalar Aider
- `pip install aider-chat` en el entorno Python
- Configurar API key (Claude o local via Ollama)
- Probar: `aider --model claude-sonnet --lint` en `src/`
- **File:** `bin/aider-session.sh`
- **Verify:** Aider puede editar un archivo y crear commit

### [ ] 008-03: Crear design systems en OD
- Crear `design-systems/sonoran-sunset/DESIGN.md` (paleta AzREC)
- Crear `design-systems/zamora/DESIGN.md` (estilo Abe Music Hub)
- Probar: generar landing con cada uno
- **File:** `design-systems/*/DESIGN.md`
- **Verify:** OD genera landing en <60s con CSS correcto

## Fase 2 — Integración JARVIS (3 tasks, 1d)

### [ ] 008-04: Scripts wrapper OD + Aider
- `bin/od-generate.sh`: recibe brief + skill + design system → genera y deploya
- `bin/aider-session.sh`: recibe tarea + files → edita y commit
- **Files:** `bin/od-generate.sh`, `bin/aider-session.sh`
- **Verify:** `./bin/od-generate.sh "landing zamora"` produce HTML en `/tmp/`

### [ ] 008-05: Service systemd para OD daemon
- Crear `sonora-open-design.service`
- Proxy nginx: `/design/` → localhost:7456
- **Files:** `/etc/systemd/system/sonora-open-design.service`
- **Verify:** `curl localhost:7456` responde

### [ ] 008-06: Pipeline generación desde Telegram
- Conectar OD + Aider al orquestador de JARVIS
- Comando: `/genera landing zamora` → OD → deploy
- **Files:** `src/core/tools/open_design.py`
- **Verify:** Mensaje Telegram genera y despliega landing

## Fase 3 — Payment Pipeline (4 tasks, 2d)

### [ ] 008-07: Registro Bitso Business
- Usuario se registra en business.bitso.com
- Pasa KYC (2-6 semanas)
- Obtiene API key + secret + CLABE virtual
- **Files:** `.env` (BITSO_API_KEY, BITSO_SECRET)

### [ ] 008-08: Webhook de pagos
- `services/payments/webhook.py`: recibe notificación Bitso
- Verifica firma HMAC SHA-256
- Marca pago como recibido en BD
- **Files:** `services/payments/webhook.py`, `services/payments/requirements.txt`
- **Verify:** `curl -X POST localhost:8767/webhook/bitso` con payload de prueba

### [ ] 008-09: Liberación automática
- Al recibir webhook: enviar contenido digital por Telegram/Email
- Actualizar estado en Neo4j
- Notificar al usuario
- **Files:** `services/payments/releaser.py`
- **Verify:** Pago de prueba → contenido liberado en <5s

### [ ] 008-10: Dashboard de pagos
- Tabla en webui: pagos recibidos, productos, fechas
- Gráfica de ingresos semanal
- **Files:** `webui/routes/payments_router.py`
- **Verify:** `GET /api/payments` devuelve historial

## Fase 4 — Automatización Total (3 tasks, 2d)

### [ ] 008-11: CI con Aider review
- GitHub Action: al crear PR, Aider revisa y comenta
- Auto-merge si test + lint pasan y Aider aprueba
- **Files:** `.github/workflows/review.yml`
- **Verify:** PR con cambio simple → review automático en <2min

### [ ] 008-12: Automation semanal en OD
- Brief semanal → OD genera deck automático
- Skill: `weekly-report` con datos de Neo4j
- **Files:** `automation/open-design-weekly.sh`
- **Verify:** Deck semanal se genera y deploya

### [ ] 008-13: Pipeline completo end-to-end
- Prueba: brief → OD genera → Aider pule → deploy → cobro
- Documentar en `docs/pipeline-completo.md`
- **Files:** `docs/pipeline-completo.md`
- **Verify:** Pipeline completo funciona de inicio a fin
