# Score — SPEC-SDC-PLATFORM

| Métrica | Peso | Score (0-10) | Justificación |
|---------|------|--------------|---------------|
| Revenue Impact | 1x | 10 | Canal directo de ingresos recurrentes: licencias mensuales + markup revendedor + revenue share. Cada cliente puede escalar su propia base de sub-clientes. |
| Scalability | 1x | 9 | Multi-tenant nativo: un deploy PostgreSQL + MCP Gateway sirve N revendedores, cada uno con N clientes. Sin cuellos de botella evidentes. |
| Reusability | 1x | 10 | 3 agentes canónicos (Voz, CRM, Social) reutilizables por cualquier industria. Pricing dinámico desde YAML. Mismo gateway para todos. |
| Automation Impact | 1x | 9 | Provisioning de licencias, facturación y KPIs 100% automáticos vía MCP. Solo registro inicial requiere acción humana. |
| Knowledge Impact | 1x | 7 | Captura eventos de plataforma en events.jsonl. Pricing documentado en YAML. Sin mecanismo de lecciones aprendidas explícito aún. |
| Reliability | 1x | 7 | Fallback a valores hardcoded si YAML falla. Circuit breaker en MCP Gateway. Sin HA planning en v1. |
| Founder Independence | 1x | 9 | Reseller auto-servicio: catálogo, compra, gestión de clientes, todo sin founder. Solo caídas mayores requieren intervención. |
| Operational Simplicity | 1x | 8 | Stack simple: vanilla JS + FastAPI + PostgreSQL + MCP. Sin colas, sin workers, sin orquestadores complejos. |
| Customer Value | 1x | 10 | Resuelve el problema real de agencias/consultoras que quieren revender IA sin construirlo. Pricing claro, markup controlado, sin vendor lock-in. |
| FinOps Efficiency | 1x | 6 | Sin tracking de costos por tenant aún. Costos de MCP Gateway y modelos compartidos. Potencial de optimización future. |

**Total: 85/100** → **PASA** (corte: ≥60)

**Veredicto:** Aprobado
**Aprobado por:** OpenClaw (score automático)
