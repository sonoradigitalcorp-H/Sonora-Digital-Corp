# Plan de Ejecución — Zamora Evolution

## Fases

### Fase 1: Fundación de Automatización (FR1, FR7)
**Objetivo**: Conectar Zamora al ecosistema SDC (n8n, Engram, Neo4j)
**Riesgo**: Bajo — componentes ya probados
**Rollback**: Revertir cambios en `zamora.py` y eliminar workflows n8n

### Fase 2: Agente IA + Pagos (FR2, FR5)
**Objetivo**: Agente IA vía Hermes + pagos recurrentes Stripe/Mercado Pago
**Riesgo**: Medio — depende de API keys externas
**Rollback**: Deshabilitar webhooks de pago y agente

### Fase 3: Dashboard Cliente + Admin (FR3, FR6)
**Objetivo**: Portal con login para clientes y panel admin con KPIs
**Riesgo**: Medio — requiere UI/UX
**Rollback**: Mantener landing estática como fallback

### Fase 4: Contenido Automatizado (FR4, FR9)
**Objetivo**: Generación automática de contenido visual y redes sociales
**Riesgo**: Bajo — usa MCP tools ya existentes
**Rollback**: Deshabilitar workflows de contenido

### Fase 5: Pull-Requests y Despliegue
**Objetivo**: Commit, push y verificación en producción
**Riesgo**: Bajo

## Orden de ejecución
F1 → F2 → F3 → F4 → F5

Cada fase termina con verificación explícita y commit.
