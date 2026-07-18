# clone-service — Clon Publicitario SDC

**Template**: SKILL-TEMPLATE.md v1.0.0
**Version**: 1.0.0
**Audit ID**: SKILL-CLONE-001

---

## 1. Business Objective

Permitir que clientes compren un pack de clon publicitario, envíen fotos y audio por WhatsApp/Telegram, y reciban fotos, videos y audio con su identidad visual y vocal para campañas de marketing.

## 2. Inputs (Gherkin)

```gherkin
Dado que el cliente compró un pack de clon publicitario
Cuando envía 15-20 fotos + 30s audio por WhatsApp/Telegram
```

## 3. Outputs (Gherkin)

```gherkin
Entonces el sistema entrena un LoRA facial con las fotos
Y clona la voz desde el audio
Y el cliente puede pedir:
  - Fotos con su cara en cualquier escenario
  - Videos talking-head o cuerpo completo
  - Audio TTS con su voz
Y los assets se entregan en Supabase en 3 formatos (9:16, 16:9, 1:1)
```

## 4. Events

```
Events:
- clone.client_registered: cliente compra pack
- clone.photos_collected: 15+ fotos recibidas
- clone.photos_rejected: foto no pasa validación
- clone.training_started: inicia entrenamiento LoRA
- clone.lora_trained: LoRA completado
- clone.voice_cloned: voz clonada
- clone.generated: asset generado
- clone.credits_low: créditos < 20%
```

## 5. Dependencies

```
Dependencies:
- FAL.ai: LoRA training + image/video generation
- OmniVoice: voice cloning + TTS (puerto 3900)
- Supabase: storage for photos, models, assets
- FFmpeg: video/audio processing
- OpenClaw: WhatsApp/Telegram gateway (puerto 18789)
```

## 6. Tools

```
Tools:
- lora_mcp: validate_photos, train_lora, check_face_quality
- voice_clone_mcp: validate_audio, clone_voice, list_voices, generate_tts
- generate_mcp: gen_photo, gen_video, gen_tts
- ffmpeg_mcp: ffmpeg_convert, ffmpeg_assemble, ffmpeg_multiformat
- credit_mcp: create_pack, consume_credit, get_credits
```

## 7. Policies

```
Policies:
- Minimum 15 photos for LoRA training
- Minimum 10s audio for voice cloning
- Credits must be deducted before any generation
- Assets expire after 30 days in Supabase
- Client consent must be recorded before training
- Face similarity must be > 0.6 to accept LoRA
```

## 8. Success Metrics

```gherkin
Success Metrics:
- training_time: Given 15 photos When train LoRA Then minutes
  Target: < 15 min
- face_similarity: Given LoRA trained When test generation Then similarity
  Target: > 0.75
- generation_cost: Given asset generated When check FAL cost Then USD
  Target: < $0.20
- delivery_formats: Given video When export Then format count
  Target: ≥ 3
```

## 9. Failure Conditions

```
Failure Conditions:
- FAL training timeout (>10 min)
- Face similarity < 0.6
- Audio SNR < 15dB
- Supabase upload fails
- FFmpeg conversion fails
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. FAL timeout → retry with 30s/60s/120s backoff, max 3
2. Low similarity → notify client, request more photos
3. Bad audio → notify client, request cleaner recording
4. Upload fail → retry 2x, log error, save locally
5. FFmpeg fail → return original format, log warning
```

## 11. Business Value

```
Business Value: Nuevo servicio de revenue recurrente ($49-199/cliente).
Costo real ~$5-6 por cliente + $0.01-0.15 por asset.
Margen > 90%. Pipeline 100% automático.
```

## 12. Parent OS

```
Parent OS: Sales, Content
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: process/active/ADR-20260718-CLONE-SERVICE.md
- Events: clone.*
- SPEC: process/active/SPEC-20260718-CLONE-SERVICE.md
- Tests: tests/test_clone_*.py (70+)
```
