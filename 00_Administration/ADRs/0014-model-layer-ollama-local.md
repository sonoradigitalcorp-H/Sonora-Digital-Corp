# ADR 0014: Modelo por capa — Ollama local $0 (orquestador) + deepseek-0731 (chat web)

**Fecha**: 2026-08-26
**Estado**: IMPLEMENTADO
**Autor**: MYSTIC / SDC

## Contexto

Se pidió migrar TODO el backend a modelos locales gratuitos de Ollama en el VPS, con
verificación "sin mentiras" (test E2E real, no mocks). Se detectó una **inconsistencia
documental** que este ADR resuelve:

- **ADR-0013** (2026-08-23) documenta `nemotron-free` como PRIMARY (eval 83% vs 50%).
- **ESTADO.md** + `vps_ai_server.py` (2026-08-23 tarde) revirtieron a `deepseek` PRIMARY.

## Verificación en vivo (2026-08-26) — la verdad actual

| Modelo | Estado real hoy | Evidencia |
|--------|-----------------|-----------|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **OVERLOADED** | Logs gateway: `Upstream error from Nvidia: Service temporarily overloaded` (repetido) |
| `deepseek/deepseek-v4-flash-0731` | **FUNCIONA** | Chat web respondió en ~2-3s con copy natural |
| `ollama/qwen3:4b` (local) | **FUNCIONA, lento** | ~5.7 t/s en CPU; 20-40s por respuesta de chat |

**Conclusión**: ADR-0013 quedó desactualizado. Nemotron se volvió inestable (overload).
Deepseek volvió a ser PRIMARY para chat web. Ollama local asume el orquestador.

## Decisión — modelo por capa

| Capa | Modelo | Costo | Razón |
|------|--------|-------|-------|
| **Chat web** (`vps_ai_server.py` :8643) | `deepseek-v4-flash-0731` PRIMARY | ~$0.14/M in | Rápido, preciso; nemotron overloaded |
| Fallback chat | `nemotron-free` → `ollama/qwen3:4b` → offline | $0 | Resiliencia en 3 niveles |
| **Orquestador Hermes** (`:8642`, config.yaml) | `ollama/qwen3:4b` (`custom:ollama-local`) | $0 | Tareas de fondo, no necesita latencia |
| **Embeddings RAG** (Qdrant) | `nomic-embed-text` 768d + `all-minilm` 384d | $0 | Local, instantáneo |
| **TTS / STT** | `kokoro-tts` + `faster-whisper` | $0 | Local |

## Correcciones de infraestructura aplicadas

1. **`OLLAMA_ENDPOINT`** en `.env` apuntaba a `http://149.56.46.173:11434` (IP pública,
   cerrada por binding loopback). Corregido a `http://127.0.0.1:11434`.
2. **`custom_providers.ollama-local`** en `config.yaml` usaba la misma IP pública.
   Corregido a loopback. Referencia canónica: `provider: custom:ollama-local`.
3. **Hermes home en VPS** = `/home/mystic/.hermes` (NO `/home/ubuntu/.hermes`; el user
   SSH es `ubuntu` pero el home real es `/home/mystic`). Todos los scripts/tests deben
   usar la ruta absoluta `/home/mystic/.hermes`, nunca `~/.hermes` en contexto VPS.

## Túnel MCP reparado

El MCP `hermes-gateway` de opencode daba timeout 30s porque apuntaba a `127.0.0.1:8642`
local VACÍO (el gateway real vive en el VPS). Solución:

- Servicio systemd user `hermes-tunnel.service` (autossh `-M 0 -N -T`) que expone
  VPS `8642` (gateway), `8643` (api) y `11434` (ollama) en local.
- Alias SSH `sdc-prod` con `IdentityFile ~/.ssh/id_ed25519_sdc` (antes faltaba → publickey denied).

## Suite E2E "sin mentiras"

`03_Sandbox_and_RnD/tests/integration/test_e2e_sistema.py` — 28 tests reales (SSH/HTTP/SQL,
sin mocks) + `tests/features/e2e_sistema.feature` (Gherkin). Cobertura: VPS 7 servicios,
Ollama modelos/embeddings, API keys, Hermes gateway+AI server, túnel MCP, cowork agentes
(registry sin skills fantasma), metadata Qdrant + RAG tenant-id, bases pobladas, WACLI,
Composio.

## Justificación del costo

- **El orquestador y embeddings** (mayor volumen de tokens) van en Ollama **$0**.
- **El chat web** (bajo volumen, necesita latencia) usa deepseek (~$0.14/M in). Con $2.73
  restantes en la key alcanza para miles de chats.
- No existe modelo "más barato que deepseek de calidad similar": los gratis (nemotron,
  gemma, llama-8b) son rate-limited u overloaded, o menos capaces.

## Consecuencias

- **ADR-0013 queda SUPERADO** en el punto "nemotron PRIMARY" (por overload de Nvidia).
  El resto (clean_reply, eval, copy de venta) sigue vigente.
- Ollama `qwen3:4b` es lento en CPU (~5.7 t/s): válido para orquestador, NO para chat web.

## Archivos Modificados
- `/home/mystic/.hermes/config.yaml` (VPS) — `model.provider: custom:ollama-local`, `qwen3:4b`
- `/home/mystic/.hermes/.env` (VPS) — `OLLAMA_ENDPOINT` → loopback
- `/opt/hermes/vps_ai_server.py` (VPS) — `MODEL_CHAIN` deepseek PRIMARY + fallback ollama
- `~/.config/systemd/user/hermes-tunnel.service` — autossh túnel
- `~/.ssh/config` — alias `sdc-prod` con IdentityFile
- `03_Sandbox_and_RnD/tests/integration/test_e2e_sistema.py` — 28 tests

---

*ADR aprobado por MYSTIC — 2026-08-26*
