# SPEC-20260718-CLONE-SERVICE — Servicio de Clon Publicitario

| Campo | Valor |
|-------|-------|
| **ID** | `SPEC-20260718-CLONE-SERVICE` |
| **Fecha** | 2026-07-18 |
| **Autor** | Mystic (SDC AI Orchestrator) |
| **Tier** | 3 |
| **Estado** | activo |
| **Score requerido** | ≥75 |

---

## 1. Objetivo

Crear un servicio de clon publicitario donde el cliente paga un pack, envía 15-20 fotos + audio por WhatsApp/Telegram, y el sistema entrena un LoRA facial + clon de voz para generar fotos, videos y audio con su identidad visual y vocal para campañas de marketing.

---

## 2. Value Driver

- **Revenue**: cada cliente paga $49-199 USD por pack
- **Retention**: genera assets ilimitados → el cliente vuelve por más
- **Automation**: pipeline 100% automático sin intervención humana
- **Founder-independence**: el sistema opera solo vía agente conversacional

---

## 3. Functional Requirements

| FR# | Descripción |
|-----|-------------|
| **FR-01** | **Recolección conversacional**: El agente recibe fotos y audio del cliente por WhatsApp/Telegram, las valida, y confirma cuándo tiene el mínimo requerido (15 fotos + 30s audio) |
| **FR-02** | **Validación de calidad**: El sistema verifica que las fotos tengan rostro detectable, buena iluminación, y variedad de ángulos. El audio debe tener voz clara sin ruido excesivo |
| **FR-03** | **Entrenamiento**: Entrenar LoRA facial (Flux) con las fotos del cliente + clonar su voz (MiniMax/OmniVoice). Guardar modelos en Content Server |
| **FR-04** | **Generación bajo demanda**: El cliente pide fotos/videos/audio con su identidad. El sistema usa los modelos entrenados para generar assets publicitarios |
| **FR-05** | **Post-procesamiento y entrega**: Convertir a múltiples formatos (9:16, 16:9, 1:1), añadir branding SDC, watermark opcional, y entregar en Supabase Storage con enlace público |
| **FR-06** | **Gestión de créditos y pricing**: Cada pack incluye créditos. Cada generación consume créditos. El sistema notifica al agotarse |

---

## 4. Success Criteria

- [ ] FR-01: Agente recolecta 15+ fotos + audio por WhatsApp/Telegram sin intervención manual
- [ ] FR-02: Validación rechaza fotos sin rostro y audio con ruido excesivo
- [ ] FR-03: LoRA entrenado en <15 min, clon de voz en <2 min
- [ ] FR-04: Foto generada con face similarity >0.75 contra fotos originales
- [ ] FR-04: Video generado con lip sync accuracy >0.8
- [ ] FR-05: Assets entregados en Supabase en 3 formatos (9:16, 16:9, 1:1)
- [ ] FR-06: Créditos se descuentan correctamente por cada generación
- [ ] TDD: 40+ tests pasando
- [ ] Gherkin: 19+ escenarios cubiertos
- [ ] Score: ≥75 en evaluación
- [ ] Lint: 0 errores (ruff)
- [ ] Sin secrets hardcodeados en código

---

## 5. Gherkin Scenarios

| Archivo | Escenarios |
|---------|-----------|
| `gherkin/clone-recollection.feature` | 4 escenarios (recolección fotos/audio, validación, detección "terminé") |
| `gherkin/clone-training.feature` | 4 escenarios (entrenar LoRA, clonar voz, validar calidad, fallo) |
| `gherkin/clone-generation.feature` | 5 escenarios (foto, video talking-head, video cuerpo, TTS, iterar) |
| `gherkin/clone-delivery.feature` | 3 escenarios (entrega Supabase, enlaces, multi-formato) |
| `gherkin/clone-pricing.feature` | 3 escenarios (comprar pack, consumir crédito, renovar) |

---

## 6. Edge Cases

| EC# | Descripción |
|-----|-------------|
| EC1 | Cliente envía fotos borrosas o sin rostro → agente pide re-enviar |
| EC2 | Cliente envía audio <10s o con ruido excesivo → agente pide más |
| EC3 | Cliente envía fotos en 20 mensajes separados durante horas → agente trackea progreso |
| EC4 | LoRA entrenado no se parece al cliente (face similarity <0.6) → re-entrenar con más fotos |
| EC5 | Cliente paga pero nunca envía fotos → expira después de 7 días |
| EC6 | FAL.ai falla durante entrenamiento (timeout, error) → reintentar con backoff exponencial |
| EC7 | Cliente quiere video de cuerpo completo pero solo envió selfies → pedir fotos de cuerpo |
| EC8 | Assets generados expiran en Supabase → política de retención de 30 días |

---

## 7. Technical Approach

### Arquitectura

```
WhatsApp/Telegram (cliente)
       │
       ▼
OpenClaw Gateway ←→ Agente conversacional
       │
       ├── FR-01: valida fotos/audio → Supabase Storage (/clients/{id}/raw/)
       │
       ├── FR-02: Face validation (insightface/retinaface) + audio SNR check
       │
       ├── FR-03: FAL flux-lora-trainer (15-20 fotos) → LoRA weights
       │           OmniVoice/MiniMax voice clone (30s audio) → voice model
       │           Guarda en: /clients/{id}/models/
       │
       ├── FR-04: FAL flux-lora (con LoRA) → foto
       │           FAL seedance/kling + veed-lipsync → video
       │           OmniVoice/FAL minimax-tts → audio con voz clonada
       │
       ├── FR-05: FFmpeg → convert/assemble/export multi-formato
       │           Content Server → cache + serve
       │           Supabase Storage → entrega al cliente
       │
       └── FR-06: Credit system → SQLite/Redis → descuenta por asset
```

### MCP Tools

| Tool | Server | Función |
|------|--------|---------|
| `train_lora` | `lora_mcp.py` (enhance) | Entrenar LoRA con 15+ fotos, validar calidad |
| `clone_voice` | `voice_clone_mcp.py` (new) | Clonar voz desde audio, listar voces |
| `gen_photo` | `generate_mcp.py` (new) | Generar foto con LoRA + prompt |
| `gen_video` | `generate_mcp.py` | Generar video talking-head o cuerpo completo |
| `gen_tts` | `generate_mcp.py` | Texto → audio con voz clonada |
| `ffmpeg_convert` | `ffmpeg_mcp.py` (enhance) | Convertir a multi-formato |
| `ffmpeg_assemble` | `ffmpeg_mcp.py` | Ensamblar video + audio + branding |
| `validate_photos` | `lora_mcp.py` | Validar calidad de fotos recibidas |
| `validate_audio` | `voice_clone_mcp.py` | Validar calidad de audio |

### Almacenamiento

```
Supabase Storage: sdc-assets bucket
  /clients/{client_id}/
    raw/photos/{uuid}.jpg       ← fotos originales del cliente
    raw/audio/{uuid}.wav        ← audio original
    models/lora.safetensors     ← LoRA entrenado
    models/voice/{voice_id}/    ← modelo de voz
    output/photos/{uuid}.jpg    ← fotos generadas
    output/videos/{uuid}.mp4    ← videos generados
    output/audio/{uuid}.wav     ← audio generado
```

---

## 8. Dependencies

- **FAL_KEY** — API key para FAL.ai (ya configurado en content server, `FAL_KEY`)
- **OmniVoice** — Docker en puerto 3900 (ya desplegado)
- **Supabase** — Bucket `sdc-assets` (ya configurado)
- **Content Server** — Puerto 8765 (ya desplegado)
- **OpenClaw** — Gateway en puerto 18789 (ya desplegado)
- **FFmpeg** — Binario en sistema (ya disponible vía ffmpeg_mcp.py)
- **Whisper MCP** — Transcripción de audio (ya desplegado)
- **Python** — httpx, hashlib, json (stdlib + httpx ya instalado)

---

## 9. Events to Emit

| Evento | Cuándo | Payload |
|--------|--------|---------|
| `clone.client_registered` | Cliente compra pack | `{client_id, tenant_id, pack_type, credits}` |
| `clone.photos_collected` | Cliente completa 15+ fotos | `{client_id, count}` |
| `clone.photos_rejected` | Foto no pasa validación | `{client_id, reason}` |
| `clone.training_started` | Inicia entrenamiento LoRA | `{client_id, photos_count}` |
| `clone.lora_trained` | LoRA completado | `{client_id, weight_id, face_similarity}` |
| `clone.voice_cloned` | Voz clonada | `{client_id, voice_id}` |
| `clone.generated` | Asset generado | `{client_id, type, url, credits_used}` |
| `clone.credits_low` | Créditos <20% | `{client_id, remaining}` |

---

## 10. Kill Criteria

- FAL.ai no permite entrenar LoRAs personalizados (solo inference)
- Costo por entrenamiento LoRA > $15 USD (inviable para el pricing)
- Face similarity de LoRA entrenado <0.6 sistemáticamente
- Tiempo de entrenamiento > 30 minutos consistente
- El cliente tipo no entiende el flujo conversacional

---

## 11. Scale Criteria

- **>50 clientes/mes**: Considerar GPU propia (RunPod/Vast.ai) en vez de FAL para reducir costos
- **>200 clientes/mes**: Automatizar dashboard de autoservicio (sin intervención del agente)
- **>1000 clientes/mes**: Sistema de colas y workers dedicados
- **Calidad inconsistente**: Evaluar FaceFusion como backend adicional
