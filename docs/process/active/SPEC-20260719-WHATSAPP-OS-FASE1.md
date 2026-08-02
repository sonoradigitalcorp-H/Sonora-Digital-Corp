# SPEC-20260719-WHATSAPP-OS-FASE1 — Sonora OS v3: WhatsApp Foundation

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260719-WHATSAPP-OS-FASE1` |
| **Fecha** | 2026-07-19 |
| **Autor** | Mystic (SDC Orchestrator) |
| **Tier** | 3 |
| **Estado** | activo |
| **Score requerido** | ≥75 |
| **Padre** | `SPEC-20260719-WHATSAPP-OS` (iniciativa maestra) |
| **Depende de** | `SPEC-20260718-ONBOARDING`, `SPEC-20260718-CLONE-SERVICE` |

---

## 1. Objetivo

Construir la base de WhatsApp para Sonora OS v3: un único MCP server (`wacli_mcp.py`) con todas las herramientas de mensajería, un webhook persistente que escucha mensajes entrantes, catálogo de servicios consultable, generador de links wa.me y thumbnails de audio — todo conectado al bus de eventos.

---

## 2. Value Driver

| Métrica | Impacto |
|---------|---------|
| **Automation** | Mensajes entrantes y salientes 100% event-driven |
| **Revenue** | wa.me links + catálogo habilitan ventas sin fricción |
| **Founder-independence** | WhatsApp se autocontiene, no requiere intervención manual |
| **Knowledge** | Cada mensaje se emite como evento trazable |

---

## 3. Functional Requirements

| FR# | Descripción | Prioridad |
|-----|-------------|-----------|
| **FR-01** | **Unificar wacli MCP**: Mergear `wacli_server.py` en `wacli_mcp.py`. Añadir: `send_audio_thumbnail`, `create_qr`, `read_qr`, `get_contacts` | 🔴 |
| **FR-02** | **Webhook persistente**: Listener continuo de WhatsApp que publica eventos al event bus | 🔴 |
| **FR-03** | **wa.me link generator**: Tool que genera links personalizados por cliente con ref_code + UTM | 🔴 |
| **FR-04** | **Catálogo WhatsApp**: Catálogo de servicios/productos en JSON, consultable por WhatsApp | 🔴 |
| **FR-05** | **Audio thumbnail**: CLI tool que toma un audio MP3/OGG, genera waveform thumbnail con PIL, y lo envía como preview antes del audio completo | 🟡 |
| **FR-06** | **Skills WhatsApp**: Skill formal para onboarding y catálogo | 🟡 |

---

## 4. Success Criteria

- [ ] `wacli_mcp.py` unificado con 8 tools: `send_text`, `send_file`, `send_voice`, `send_audio_thumbnail`, `create_qr`, `read_qr`, `get_contacts`, `check_status`
- [ ] `wacli_server.py` deprecado y eliminado
- [ ] `apps/whatsapp/webhook.py` escucha mensajes y emite `whatsapp:message:received`
- [ ] `tools/wa-me-link.md` genera wa.me válidos con ref_code
- [ ] `tools/audio-thumbnail.md` genera PNG de waveform
- [ ] `state/whatsapp/catalog.json` existe y es válido
- [ ] 35/35 evals estructurales pasan
- [ ] Tests nuevos para MCP tools y webhook pasan
- [ ] Score ≥75

---

## 5. Gherkin Scenarios

Ver `gherkin/SPEC-20260719-WHATSAPP-OS-FASE1.feature`

---

## 6. Edge Cases

| EC# | Descripción |
|-----|-------------|
| EC1 | Número de teléfono sin prefijo `521` → normalizar automáticamente |
| EC2 | Archivo de audio no existe → error claro: `file not found: {path}` |
| EC3 | `wacli` no está instalado → retornar `{"success": false, "error": "wacli not found"}` |
| EC4 | Webhook pierde conexión → auto-reconnect con backoff exponencial |
| EC5 | QR code inválido o ilegible → retornar `{"valid": false}` |
| EC6 | wa.me link con ref_code vacío → omitir parámetro `text` |

---

## 7. Technical Approach

### 7.1 Arquitectura

```
WhatsApp Web / wacli
        │
        ▼
┌─────────────────────┐
│  wacli CLI          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐     ┌─────────────────┐
│  wacli_mcp.py       │────▶│  Hermes/Event   │
│  (8 tools)          │     │  Bus            │
└──────────┬──────────┘     └─────────────────┘
           │
           ▼
┌─────────────────────┐
│  webhook.py         │
│  (listener 24/7)    │
└─────────────────────┘
```

### 7.2 Archivos a crear/modificar

**Nuevos:**
- `apps/whatsapp/webhook.py`
- `tools/wa-me-link.md`
- `tools/audio-thumbnail.md`
- `state/whatsapp/catalog.json`
- `skills/whatsapp-onboarding.skill.md`
- `skills/whatsapp-catalog.skill.md`
- `gherkin/SPEC-20260719-WHATSAPP-OS-FASE1.feature`
- `process/active/SCORE-20260719-WHATSAPP-OS-FASE1.md`

**Modificados:**
- `mcp/servers/wacli_mcp.py` (merge + nuevas tools)
- `mcp/servers/wacli_server.py` (eliminar tras merge)
- `agents/registry.yaml` (agregar triggers/capabilities si aplica)

### 7.3 Patrón de implementación

1. Tests primero (TDD) para cada tool
2. Merge de `wacli_server.py` → `wacli_mcp.py`
3. Nuevas tools con `_ensure_to()` robusto
4. Webhook con asyncio + Redis Streams
5. Validación: `pytest` + `make eval`

---

## 8. Dependencies

- `wacli` CLI instalado
- `ffmpeg` para conversión de audio
- `Pillow` para thumbnails
- `qrcode` para generación de QR
- `pyzbar` o `opencv` para lectura de QR
- Redis (event bus)
- `mcp` SDK (ya instalado)

---

## 9. Events to Emit

| Evento | Cuándo | Payload |
|--------|--------|---------|
| `whatsapp:message:received` | Llega mensaje de WhatsApp | `{ from, text, media?, timestamp, message_id }` |
| `whatsapp:message:sent` | Se envía mensaje | `{ to, text?, media?, cost_tokens, message_id }` |
| `whatsapp:qr:created` | QR generado | `{ client_id, qr_path, wa_me_link }` |
| `whatsapp:qr:read` | QR leído | `{ data, valid }` |
| `whatsapp:catalog:requested` | Cliente pide catálogo | `{ client_id, timestamp }` |

---

## 10. Kill Criteria

- Si `wacli_mcp.py` rompe funcionalidad existente (no puede enviar mensajes) → revertir merge
- Si webhook consume >100MB de RAM o no reconecta en 60s → reescribir con polling
- Si tests de MCP no pasan → no mergear

---

## 11. Scale Criteria

- **>100 mensajes/día**: Separar webhook a systemd service dedicado
- **>1,000 mensajes/día**: Cola de mensajes con Redis Streams + worker
- **>10,000 mensajes/día**: Múltiples instancias webhook con load balancer

---

## 12. ADR

### ADR-001: Unificar MCP servers
**Decisión:** Mergear `wacli_server.py` a `wacli_mcp.py`.
**Razón:** Una sola fuente de verdad para WhatsApp. `wacli_server.py` era un duplicado con funcionalidad incompleta.

### ADR-002: Webhook persistente vs polling
**Decisión:** Webhook persistente con auto-reconnect.
**Razón:** Menor latencia y menor consumo de recursos que polling cada N segundos.

### ADR-003: wa.me como entry point
**Decisión:** Links wa.me como punto de entrada principal.
**Razón:** No requiere QR ni app adicional; funciona en cualquier dispositivo.
