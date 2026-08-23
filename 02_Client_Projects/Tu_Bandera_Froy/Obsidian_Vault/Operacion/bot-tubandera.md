# Operación del Bot Tu Bandera

## Arquitectura (2026-08-23)
- **Bot TG**: `@TBasistente_bot` → `tubandera-bot.service` en VPS `/opt/hermes/tubandera/` (polling propio especializado).
- **Cerebro**: `vps_ai_server.py` :8643 endpoint unificado `person:tubandera` (SOUL experto + router intents + CTA determinista).
- **Hermes**: control plane — tenant `tubandera` registrado en tenants.json, bot en config.yaml (`enabled:false`, sin doble poll), gateway :8642.
- **RAG**: Qdrant `tubandera_kb` (Nomic 768d) ← este vault espejado a `/opt/hermes/tubandera/kb/`.
- **Trazabilidad**: `tubandera.db` — usuario nuevo → tenant_id `TB-{chat_id}` automático; familiares con permiso.
- **Guardas**: `guards.py` filtra prompt injection antes del LLM (bot) + SOUL resiste en endpoint.

## Comandos útiles
- Estado: `systemctl status tubandera-bot`
- Logs: `journalctl -u tubandera-bot -f`
- Reindexar KB: `python3 /opt/hermes/tubandera/indexador_kb.py`
- Suite: `/opt/hermes/venv/bin/python3 /opt/hermes/scripts/suite_test.py` (cron horario)

## Pendientes
- wacli auth (notificaciones WhatsApp a Roberto/familiares) — pairing físico
- Canal TG comunidad + "Aprende sobre adicciones"
- Fotos de Roberto → grupo/familiar (usa registrar_foto + permiso)
