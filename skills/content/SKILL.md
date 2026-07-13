---
name: content
description: Operate the daily content factory. Use when the user asks to generate content, run the pipeline, or check content status.
---

# Content Skill

Operates the daily content pipeline for all tenants. Generates videos, reels, and podcasts for each artist.

## Commands

- `/generar-campaña "description" --artista Name --tipo clase|promo|podcast`
- `/daily-status` — check today's content generation status
- `/pipeline-run` — force run the daily pipeline now

## Pipeline

1. `rag_search` → context (stats + news + trends)
2. `llm_chat` → generate script with context
3. `generate_video` → FAL + LoRA → raw video
4. `export_video` → FFmpeg → 4 platform formats
5. `whisper_transcribe` → subtitles
6. `engram_save` → record
7. Redis → notify agents
