# Agent Context

Last updated: 2026-06-09

## Active Specifications

- **000-constitucion**: Constitution v2.0.0 (fused: 7 niveles, 11-step SDD v2)
- **001-memoria-persistente**: Memory with Neo4j + Qdrant
- **002-servidor-mcp**: MCP Server with 10 tools
- **003-web-ui**: Web UI with SSE streaming
- **004-voz**: Voice interface (STT/TTS/Wake Word)
- **005-orquestacion-agentes**: 7 agents orchestration
- **006-infraestructura**: Security, testing, Docker, CI/CD

## Project Rules

- Model: opencode/deepseek-v4-flash-free (via opencode-go)
- Architecture: Python/FastAPI + Neo4j + Qdrant + Docker
- Methodology: SDD v2 (constitution binding) — 11-step cycle: Revenue Gate → Discovery → Spec → BDD/ATDD → ADR → Plan → Tasks → Code → Verify → Delivery Gate → Archive
