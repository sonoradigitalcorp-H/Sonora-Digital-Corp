# SPEC-029: Hermes MCP Integration

**Status:** Draft
**Tier:** 1 (Foundation)
**Score:** 75/100
**Created:** 2026-08-02

## 1. Objective

Conectar Hermes Gateway como servidor MCP (Model Context Protocol) a OpenCode, permitiendo acceso a las 18 skills de Hermes desde el entorno de desarrollo.

## 2. User Stories

- Como desarrollador, quiero invocar skills de Hermes desde OpenCode
- Como operador, quiero configurar la conexión MCP fácilmente
- Como usuario, quiero que las skills aparezcan como herramientas disponibles

## 3. Functional Requirements

| ID | Requirement | Priority | Est. Hours |
|----|------------|----------|------------|
| FR1 | HTTP MCP config: configuración del servidor MCP vía HTTP | P0 | 6 |
| FR2 | 18 skills accessible: todas las skills de Hermes disponibles | P0 | 4 |
| FR3 | Tool invocation: invocación de tools con params y respuesta | P0 | 8 |

## 4. Non-Functional Requirements

| ID | Requirement | Target |
|----|------------|--------|
| NFR1 | Tool invocation latency | < 2s |
| NFR2 | Availability | 99.5% |
| NFR3 | Concurrent tool calls | > 5 |

## 5. Hermes Skills Inventory

| # | Skill | Description |
|---|-------|-------------|
| 1 | calendar | Gestión de calendario |
| 2 | email | Envío y gestión de correo |
| 3 | tasks | Gestión de tareas |
| 4 | search | Búsqueda de información |
| 5 | control | Control de navegador |
| 6 | query | Consultas a datos |
| 7 | alert | Sistema de alertas |
| 8 | reminder | Recordatorios |
| 9 | navigate | Navegación UI |
| 10 | report | Generación de reportes |
| 11 | crm | Gestión CRM |
| 12 | invoice | Facturación |
| 13 | inventory | Inventario |
| 14 | analytics | Análisis de datos |
| 15 | support | Soporte al cliente |
| 16 | marketing | Campañas marketing |
| 17 | social | Redes sociales |
| 18 | api | Integraciones API |

## 6. Technical Architecture

```
┌─────────────────────────────────────────────┐
│              OpenCode                        │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐   │
│  │         MCP Client                  │   │
│  └──────────────┬──────────────────────┘   │
│                 │ HTTP                       │
└─────────────────┼───────────────────────────┘
                  │
┌─────────────────┼───────────────────────────┐
│           Hermes Gateway                     │
├─────────────────┼───────────────────────────┤
│  ┌──────────────┴──────────────────────┐   │
│  │         MCP Server                  │   │
│  ├─────────────────────────────────────┤   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │   │
│  │  │Cal  │ │Email│ │Task │ │ ... │  │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘  │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

## 7. Data Model

```typescript
interface MCPTool {
  name: string;
  description: string;
  inputSchema: JSONSchema;
}

interface MCPResponse {
  content: Array<{
    type: 'text' | 'image';
    text?: string;
    data?: string;
  }>;
}

interface HermesConfig {
  endpoint: string;
  api_key?: string;
  timeout: number;
  retry_count: number;
}
```

## 8. Configuration

```json
{
  "mcpServers": {
    "hermes": {
      "type": "http",
      "url": "http://localhost:8080/mcp",
      "headers": {
        "Authorization": "Bearer ${HERMES_API_KEY}"
      }
    }
  }
}
```

## 9. Error Handling

- **Connection timeout:** Retry with exponential backoff
- **Authentication failure:** Log and notify operator
- **Tool not found:** Return clear error message
- **Invalid params:** Validate before sending

## 10. Security Considerations

- API key stored in environment variables
- TLS required in production
- Rate limiting per tool
- Audit logging for all invocations

## 11. Testing Strategy

- Unit tests for MCP client
- Integration tests with mock Hermes server
- E2E tests for each tool invocation
- Load tests for concurrent calls

## 12. Deployment

- Configuration in opencode.json
- Hermes Gateway running separately
- Health check endpoint

## 13. Monitoring

| Metric | Alert Threshold |
|--------|----------------|
| Tool invocation latency | > 3s |
| Error rate | > 5% |
| Connection failures | > 3/min |

## 14. Dependencies

| Dependency | Type | Purpose |
|------------|------|---------|
| Hermes Gateway | External | MCP server |
| HTTP Client | Library | MCP communication |

## 15. Success Criteria

- [ ] All 3 functional requirements implemented
- [ ] All 18 Hermes skills accessible via MCP
- [ ] Tool invocation working end-to-end
- [ ] Configuration documented
- [ ] 80% test coverage