# INVENTARIO DE MIGRACIÓN — OVH → CONTABO (FASE 2)

**Fecha:** 2026-09-03
**Estado:** EN PROCESO — acceso a Contabo pendiente (SSH bloqueado)
**Fuente:** `ESTADO.md` (canónico). OVH `149.56.46.173` inalcanzable desde laptop → inventario reconstruido de ESTADO.md + opencode.db (sesión migración `ses_f98467...`).

> ⚠️ Este inventario es PRELIMINAR. Cuando obtenga acceso a Contabo y/o OVH, se verifica en vivo (solo lectura) antes de migrar nada.

## Clasificación
- **A** = migrar directamente (rsync/config)
- **B** = reconstruir en Contabo (docker/reproducible)
- **C** = revisar manualmente
- **D** = no migrar

| # | SERVICIO | CONTENEDOR/PROCESO | PUERTO | DATOS PERSISTENTES | CONFIG | DEPENDENCIAS | CLASE |
|---|----------|-------------------|--------|--------------------|--------|--------------|-------|
| 1 | vps-ai-server | python (systemd `vps-ai-server.service`) | 8643 | ledger, registros | `/opt/hermes/vps_ai_server.py`, `.env.secrets` | LLM OpenRouter, STT, TTS, Supabase | **B/C** |
| 2 | hermes-gateway | Hermes (systemd `hermes-gateway.service`) | 8642 | SQLite `memory_store.db`, config | `/home/mystic/.hermes/config.yaml` | OpenRouter, LLM | **B** |
| 3 | sdc-stt | faster-whisper (systemd `sdc-stt.service`) | 5292 | modelo whisper small int8 | `/opt/hermes/voice/stt_server.py` | — | **B** |
| 4 | sdc-tts | edge-tts / kokoro (systemd `sdc-tts.service`) | 5293 | kokoro onnx (311MB) + voices.bin (falta) | `/opt/hermes/voice/tts_server.py` | edge-tts | **B** |
| 5 | hermosillo-webhook | telegram webhook (systemd `hermosillo-webhook.service`) | 5291 | SQLite `leads_hermosillo_cont.db` | `/opt/hermes/hermosillo/` | token TG, edge-tts | **B** |
| 6 | tubandera-bot | telegram bot (systemd `tubandera-bot.service`) | — | SQLite `tubandera.db` (usuarios/familiares/avances) | `/opt/hermes/tubandera/` | token TG, Qdrant, Supabase | **B** |
| 7 | nginx | reverse proxy | 80/443 | certs SSL | nginx conf + override | todos | **B** |
| 8 | cloudflared-tunnel | Cloudflare tunnel | — | credentials `a8f01806` | `/etc/cloudflared/config.yml` | Cloudflare | **B/C** |
| 9 | ollama | docker (compose) | 11434 | modelos: qwen3:4b, nomic-embed-text, all-minilm | compose | GPU/CPU | **B** |
| 10 | qdrant | docker (compose) | 6333 | colecciones: tubandera_kb, engram_memories (+kbs) | compose | ollama embed | **B** |
| 11 | n8n | docker (compose) | 5678 | 33 workflows, credenciales | compose | — | **C** |
| 12 | postgres-metrics | docker (compose) | 5432 (loopback) | 6 tablas métricas | compose | sync_metrics | **B** |
| 13 | kokoro-tts | docker | 8880 | kokoro onnx | compose | — | **B** |
| 14 | prometheus | docker | 9090 | time-series | /opt/monitoring | exporters | **C** |
| 15 | grafana | docker | 3000 | dashboards | /opt/monitoring | prometheus | **C** |
| 16 | node_exporter | docker | 9100 | — | /opt/monitoring | — | **D** |
| 17 | wacli-keepalive | systemd | — | store `/home/mystic/.wacli` | env | WhatsApp | **C** |
| 18 | Supabase (BD leads/citas) | **externa** | — | `public.citas`, `public.leads` | env | — | **A** (no migrar, solo re-apuntar) |
| 19 | fail2ban | systemd | — | jails | — | — | **B** |

## CRON JOBS (recrear en Contabo)
| Cron | Programación | Función |
|------|--------------|---------|
| suite_test | cada hora | health 9/9 |
| sync_metrics | cada 10 min | SQLite→Postgres metrics |
| run_automejora | cada 15 min | observación evals |
| automejora-suggest | domingo 5am | propuestas de prompt |
| audio_matutino | 8am | briefing de voz |

## VARIABLES DE ENTORNO / SECRETOS (requieren revisión al cortar)
- `OPENROUTER_API_KEY` (deepseek-v4-flash-0731) — aplicar en nuevo `.env.secrets` (chmod 600)
- `TELEGRAM_*_TOKEN` (tubandera, hermosillocont, sonora, etc.)
- `GEMINI_API_KEY`, `FAL_KEY`, `COMPOSIO_API_KEY`
- `SUPABASE_URL` / `SUPABASE_KEY` (citas + leads)
- `WACLI_BIN`, credenciales cloudflared (tunnel `sonoradigitalcorp`)

## IPs QUE CAMBIAN
- **OVH `149.56.46.173`** (viejo) → **Contabo `109.199.101.225`** (nuevo)
- `config.yaml` `base_url: http://149.56.46.173:11434/v1` → `109.199.101.225`
- Todos los endpoints internos que apuntan a la IP OVH

## DNS (SOLO FASE 7 — NO tocar hasta autorización)
- Registrar **A / AAAA** de `sonoradigitalcorp.com` → `109.199.101.225`
- Cloudflare: reducir TTL previo al cutover. Mantener OVH como rollback.
- Web hoy: **HTTP 530** (origin caído) — el cutover a Contabo restaura la página.

## ORDEN DE DESPLIEGUE EN CONTABO (una vez con acceso)
1. SSH key → verificar root
2. Instalar Docker Engine + docker-compose
3. Reconstruir compose: ollama, qdrant, n8n, postgres-metrics, kokoro (B)
4. Instalar runtime python (venv `/opt/hermes/venv`), edge-tts, faster-whisper
5. rsync servicios sistema: vps_ai_server.py, stt/tts, hermosillo, tubandera (desde repo local)
6. nginx + certs
7. cloudflared-tunnel (credentials `a8f01806`)
8. systemd units + Restart=always + fail2ban + crons
9. Punto de verificación FASE 6 (matriz) → recién ahí DNS

## ROLLBACK
- No tocar OVH (convive como rollback) hasta que Contabo pase FASE 6 completa.
- Mantener DNS apuntando a Cloudflare para poder redirigir a cualquiera de los dos origins.

---
*Este inventario se marcará ✅/verificado en vivo cuando se obtenga acceso. No migrar nada hasta FASE 4 (plan) autorizada.*