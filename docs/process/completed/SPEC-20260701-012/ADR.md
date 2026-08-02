# ADR-20260701-012 — Migrar JARVIS Agents a V2

## Context
Los 17 agentes JARVIS usaban llamadas directas a servicios y LLM externo. Se migraron al nuevo ecosistema: Redis para comunicación, Ollama local para decisiones, HermesClient para herramientas.

## Decision
1. AgentBaseV2 con Redis pub/sub + ask_ollama() + HermesClient
2. V2 agents: Research, Memory, Review — primeros migrados
3. OrchestratorV2 con routing por keywords
4. Los agentes legacy se mantienen hasta migración completa

## Consequences
- 6 tests para V2 agents
- 149 tests totales
- CI verde (#240)
