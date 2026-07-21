# Clone Agent Harness — Servicio de Clon Publicitario

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: HARNESS-CLONE-001

---

## 1. Mission

Gestionar el ciclo de vida completo del servicio de clon publicitario: recibir fotos/audio del cliente por WhatsApp/Telegram, validar calidad, entrenar LoRA facial + clon de voz, y generar assets publicitarios (fotos, videos, TTS) bajo demanda.

## 2. Capabilities

| Capability | Descripción | Eventos |
|------------|-------------|---------|
| `clone-person` | Entrenar modelo facial + voz de un cliente y generar contenido con su identidad | `clone.client_registered`, `clone.photos_collected`, `clone.lora_trained`, `clone.voice_cloned`, `clone.generated` |

## 3. Skills

| Skill | Descripción | Source |
|-------|-------------|--------|
| clone-recollection | Recibir y validar fotos/audio del cliente vía WhatsApp/Telegram | `skills/clone-service.skill.md` |
| clone-training | Entrenar LoRA facial + clonar voz | `mcp/servers/lora_mcp.py`, `mcp/servers/voice_clone_mcp.py` |
| clone-generation | Generar fotos, videos, TTS con identidad del cliente | `mcp/servers/generate_mcp.py` |
| clone-delivery | Procesar y entregar assets en múltiples formatos | `mcp/servers/ffmpeg_mcp.py` |

## 4. Policies

- No entrenar LoRA con menos de 15 fotos
- No clonar voz con audio <10 segundos
- Cada generación debe descontar créditos antes de ejecutar
- No revelar FAL_KEY, tokens, o secrets al cliente
- Todos los assets expiran a los 30 días
- El cliente debe dar consentimiento explícito antes de entrenar

## 5. Memory Scope

| Operación | Capas |
|-----------|-------|
| Read | Layer 1 (Working): estado actual del cliente, fotos recibidas |
| Read | Layer 3 (Project): modelos entrenados, créditos |
| Write | Layer 1 (Working): progreso de recolección |
| Write | Layer 3 (Project): LoRA ID, voice ID, créditos |

## 6. Approval Requirements

| Acción | Nivel |
|--------|-------|
| Entrenar LoRA | none (automático tras validación) |
| Generar foto/video | none (automático, descontando créditos) |
| Re-entrenar LoRA por baja calidad | notify (avisar al cliente) |
| Reembolsar créditos | approve (requiere humano) |

## 7. Failure Modes

| Falla | Detección |
|-------|-----------|
| FAL training timeout | HTTP timeout exception |
| Fotos sin rostro detectable | validation retorna has_face=false |
| Audio con SNR bajo | validation retorna snr_db < threshold |
| LoRA con face similarity baja | similarity score < 0.6 |
| Supabase upload fails | HTTP status != 200/201 |
| FFmpeg conversion fails | subprocess exit code != 0 |

## 8. Recovery Procedures

| Falla | Recuperación |
|-------|-------------|
| FAL training timeout | Reintentar con backoff exponencial (3 intentos, 30s/60s/120s) |
| Fotos sin rostro | Notificar cliente: "Esta foto no tiene rostro detectable. ¿Puedes enviar otra?" |
| LoRA baja calidad | Notificar cliente: pedir más fotos desde diferentes ángulos |
| Supabase error | Reintentar 2 veces, si falla guardar localmente y reintentar después |
| FFmpeg error | Log error, devolver URL original sin conversión |

## 9. Metrics

| Métrica | Gherkin | Target |
|---------|---------|--------|
| Recollection time | Dado cliente activo Cuando completa 15 fotos Entonces tiempo transcurrido | < 24h |
| Training time | Dado 15 fotos validadas Cuando entrena LoRA Entonces minutos | < 15 min |
| Face similarity | Dado LoRA entrenado Cuando genera foto de prueba Entonces similarity | > 0.75 |
| Generation cost | Dado asset generado Cuando revisa costo FAL Entonces USD | < $0.20 |
| Credit accuracy | Dado pack con N créditos Cuando consume M assets Entonces créditos restantes = N-M | 100% |
| Delivery formats | Dado video generado Cuando exporta multi-formato Entonces cantidad de formatos | ≥ 3 |

## 10. Tests

```gherkin
Funcionalidad: Clone Agent
  Escenario: Ciclo completo de clon publicitario
    Dado un cliente que compró un pack
    Cuando envía 15 fotos + 30s audio por WhatsApp
    Y el sistema entrena LoRA + clona voz
    Y el cliente pide "Una foto mía en oficina ejecutiva"
    Entonces se genera una foto con su cara
    Y se entrega en Supabase con 3 formatos
    Y se descuentan los créditos correctamente
```

## 11. Observability

| Aspecto | Valor |
|---------|-------|
| Log level | INFO |
| Eventos | `clone.*` (8 eventos definidos) |
| Monitoreo | LangFuse para costos y latencia |
| Health check | Credit MCP: `GET /health` → {status, active_clients, credits_total} |

## 12. Dependencies

| Dependencia | Tipo | Para qué |
|-------------|------|----------|
| FAL.ai | service | Entrenar LoRA + generar fotos/video |
| OmniVoice | service | Clonar voz + generar TTS |
| Supabase Storage | service | Guardar fotos, modelos, assets |
| Content Server | service | Cache y serve de assets |
| FFmpeg | tool | Post-procesamiento video/audio |
| OpenClaw | service | Gateway WhatsApp/Telegram |
| Whisper MCP | tool | Transcripción de audio |

---

## Validation Checklist

- [x] Mission is one sentence, measurable
- [x] All capabilities map to events
- [x] All skills reference existing skill definitions
- [x] All policies are enforceable
- [x] Memory scope is defined for read and write
- [x] Approval requirements cover all critical actions
- [x] All failure modes have recovery procedures
- [x] All metrics have Gherkin definitions
- [x] Tests exist and pass
- [x] Observability endpoints are defined
- [x] All dependencies are documented
