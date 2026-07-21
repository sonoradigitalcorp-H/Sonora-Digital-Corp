# Capability Matrix — Sonora Digital Corp

## SDC Capabilities (8 con código real)

| Capability | Backend | MCP Tool | Status | Agent |
|---|---|---|---|---|
| sync-artist-data | skills/sync-artist-data/ | sync_artist_data | active | collector |
| analyze-artist | skills/analyze-artist/ | analyze_artist | active | research-agent |
| search-knowledge | skills/search-knowledge/ | search_knowledge | active | — |
| score-artist | skills/score-artist/ | score_artist | active | research-agent |
| generate-video | skills/generate-video/ | generate_video | experimental | video-agent |
| manage-crm | skills/manage-crm/ | manage_crm | experimental | sales-agent |
| publish-track | skills/publish-track/ | publish_track | experimental | marketing-agent |
| process-payment | skills/process-payment/ | process_payment | experimental | finance-agent |

## Backends oficiales (por dominio)

| Dominio | Backend oficial | Expuesto como |
|---|---|---|
| WhatsApp/Telegram/Slack/Discord | Hermes Gateway | MCP tool hermes_* |
| Browser automation | Hermes browser_tool | MCP tool browser_* |
| TTS/STT/Voz | Hermes tts_registry | MCP tool hermes_* |
| Imagen/Video (FAL/ComfyUI) | Hermes image_gen/video_gen | MCP tool hermes_* |
| Finanzas (Stripe/Shopify) | OpenClaw skills | MCP tool openclaw_* |
| Memoria | SDC Engram + Qdrant + Neo4j | MCP tool memory_* |
| Infra | OpenClaw healthcheck + mcporter | MCP tool sonora_* |
| Prompts/Behavior | Policy packs (global) | System prompt |

## Policy packs (antes OpenCode skills)

| Policy | Aplica a | Archivo |
|---|---|---|
| self-verifier | Todos los agentes | constitution/policies/verify.yaml |
| rate-limiter | Todos los agentes | constitution/policies/rate-limit.yaml |
| response-builder | Todos los agentes | constitution/policies/response.yaml |
| path-extractor | Todos los agentes | constitution/policies/paths.yaml |
| network-audit | Solo infra | constitution/policies/network.yaml |
