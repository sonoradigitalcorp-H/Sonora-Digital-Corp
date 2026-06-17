# Feature Specification: Browser-Based Video Pipeline

**Feature**: 020-video-pipeline
**Created**: 2026-06-10
**Status**: Active
**Input**: Pipeline de creación de video usando browser automation (Seedance, Kling, Runway) + Fal.ai + TTS.

---

## Objetivo

Crear videos de ultra calidad cinematográfica sin GPU propia:
1. **Script**: DeepSeek V4 escribe guión cinematográfico
2. **Key frames**: Fal.ai genera imágenes de alta calidad
3. **Video**: Browser automation abre Seedance/Kling → pega prompts → descarga
4. **Voiceover**: Edge-TTS genera narración estilo Bryan Tracy/Alex Hormozi
5. **Edición**: FFmpeg + Playwright para ensamblar
6. **Entrega**: Landing page + Telegram + Email

---

## Stack Tecnológico

| Herramienta | Rol | Conexión |
|------------|-----|----------|
| **Fal.ai** | Imágenes clave | OpenClaw MCP → HTTP |
| **Seedance** | Video gratuito | Playwright browser |
| **Kling** | Video gratuito | Playwright browser |
| **Playwright** | Automatización browser | OpenClaw skill |
| **DeepSeek V4** | Script | LLM $0 |
| **Edge-TTS** | Voiceover | CLI |
| **FFmpeg** | Edición/ensamble | CLI |
| **n8n** | Pipeline | HTTP 5679 |
| **Engram** | Memoria | SQLite |

---

## Pipeline

```
Script (DeepSeek) ──► Key Frames (Fal.ai) ──► Video (Browser) ──► Voiceover (TTS) ──► Edición (FFmpeg) ──► Entrega
```

## Criterios de Éxito
- [ ] Script cinematográfico escrito
- [ ] Key frames generados con Fal.ai
- [ ] Browser automation funcional
- [ ] Voiceover generado
- [ ] Video ensamblado y entregado
- [ ] Landing page Coming Soon publicada
