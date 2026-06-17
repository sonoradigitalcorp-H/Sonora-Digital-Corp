# Implementation Plan: Content Engine & Automation

**Branch**: `003-content-engine` | **Date**: 2026-06-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/003-content-engine/spec.md`

## Summary

Automated content pipeline: n8n workflow engine for automation, content generation (text + images), video pipeline (script → TTS → render), multi-platform social scheduling, and Agent CFO for business intelligence.

## Technical Context

**Language/Version**: Python 3.11+, JavaScript (n8n nodes), TypeScript (dashboard)

**Primary Dependencies**: n8n (Docker), ComfyUI (image gen), FFmpeg (video), ElevenLabs API (TTS), social APIs, FastAPI

**Storage**: PostgreSQL (content + schedules), SQLite (n8n), S3/MinIO (media assets)

**Testing**: pytest for pipeline logic, n8n workflow export/import testing, Playwright for dashboard

**Target Platform**: Linux with NVIDIA GPU (optional, CPU fallback for video)

**Project Type**: Automation pipeline with n8n + custom services

**Performance Goals**: Content gen < 60s, video render < 5min (60s clip), social post within 1min of schedule

**Constraints**: GPU recommended for video + image gen, all credentials encrypted, safety filter mandatory

**Scale/Scope**: < 100 pieces/day, < 10 social accounts, < 50 n8n workflows

## Constitution Check

| Principle | Compliance | Status |
|-----------|-----------|--------|
| **I. Separación de Responsabilidades** | Pipeline orchestrator is deterministic Python. LLM/image gen/TTS are isolated services called via API. Pipeline logic does not depend on any single generator being available. | ✅ PASS |
| **II. Privacidad y Control Local** | Content generated locally when possible (ComfyUI for images). Social API tokens encrypted. No content sent to unauthorized third parties. | ✅ PASS |
| **III. Arquitectura Modular** | n8n, ComfyUI, video renderer, social publisher are independent Docker services. Each can be replaced. | ✅ PASS |
| **IV. Calidad y Testing** | Pipeline state machine tests. Content validation tests. Social posting mock tests. Safety filter tests. | ✅ PASS |
| **V. Documentación** | n8n workflows exported as JSON and versioned. Pipeline stages documented with expected inputs/outputs. | ✅ PASS |

**Result**: PASS. No violations.

## Project Structure

```text
specs/003-content-engine/
├── plan.md              # This file
├── spec.md              # Feature specification
├── tasks.md             # Implementation tasks
├── checklists/          # Quality checklists
└── contracts/           # API contracts

config/n8n/              # n8n workflow exports (JSON)
src/
├── content/             # Content pipeline
│   ├── generator.py     # Text + image generation
│   ├── video.py         # Video pipeline (script→render)
│   ├── scheduler.py     # Publishing scheduler
│   └── safety.py        # Content safety filter
├── social/              # Social media publishers
│   ├── instagram.py     # Instagram Graph API
│   ├── tiktok.py        # TikTok API
│   ├── youtube.py       # YouTube Data API
│   ├── twitter.py       # X/Twitter API
│   └── linkedin.py      # LinkedIn API
├── cfo/                 # Agent CFO
│   ├── dashboard.py     # Metrics and visualization
│   └── analyst.py       # Trend detection and recommendations
└── api/                 # FastAPI endpoints
```
