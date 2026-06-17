# Research: Orquestación de Agentes
**Spec**: spec.md
---
## Tecnologías Evaluadas
| Opción | Ventajas | Desventajas | Decisión |
|--------|----------|-------------|----------|
| AgentOrchestrator propio | Control total, 10 agentes, routing determinista | Más código propio | ✅ Seleccionado |
| LangChain | Ecosistema grande, chains, tools | Complejidad, breaking changes upstream | ❌ Descartado |
| CrewAI | Multi-agente, roles | Dependencia externa | ❌ Descartado |
## Decisión Arquitectónica
- **Selección**: AgentOrchestrator propio con routing por keywords (determinista)
- **Motivo**: Sin dependencias externas, 330 tests, control total
## Limitaciones
1. Routing solo por keywords — no entiende contexto semántico
2. Sin balanceo de carga entre agentes
