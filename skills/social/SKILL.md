---
name: social
description: Social media content research and trend analysis via Playwright + Firecrawl. Use for researching trends, analyzing content, or scraping social data.
version: 1.0.0
updated: 2026-07-13
---

# Social Skill

Research social media trends, analyze content, and generate strategy recommendations.

## Tools que usa
- `firecrawl_scrape` — extraer contenido de URLs
- `browser_navigate` — navegar sitios
- `browser_extract` — extraer contenido específico
- `llm_chat` — analizar tendencias
- `rag_search` — buscar contexto histórico
- `engram_save` — guardar hallazgos

## Pipeline (10:00)
1. `firecrawl_scrape` → tendencias del día
2. `browser_extract` → contenido relevante
3. `llm_chat` → analizar y resumir
4. `engram_save` → guardar tendencias

## Ejemplo
```
Analiza tendencias de TikTok para contenido musical
```
