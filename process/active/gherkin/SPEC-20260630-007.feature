Feature: Native Agent OS — MCP Gateway Unificado
  Como operador de Sonora Digital Corp
  Quiero que el MCP Gateway sea el entry point único con auth
  Para eliminar las 4 capas de routing y tener capability-based routing

  Scenario: Happy Path — Autenticación y llamada a tool
    Given el MCP Gateway está corriendo en :18989
    When envío POST /api/auth/token con client_id="sdc-core" y client_secret válido
    Then recibo un access_token JWT con expiry 3600s
    And el token tiene scope "admin"
    When envío GET /api/tools con Authorization: Bearer <token>
    Then recibo 200 con lista de tools
    And la lista contiene "capability_resolve", "skills_list", "adk_list_agents"

  Scenario: Happy Path — CapabilityRegistry resuelve capability
    Given el MCP Gateway está autenticado
    When envío POST /api/capability/resolve con task="generate a sales proposal"
    Then recibo capability="Sales Execution"
    And confidence >= 0.3
    And agent != null

  Scenario: Happy Path — Skill Marketplace unificado
    Given el SkillRegistry está cargado
    When llamo a tool "skills_list"
    Then recibo >= 100 skills
    And las skills incluyen fuentes telegram, enterprise, opencode, registry

  Scenario: Happy Path — ADK con agente declarativo
    Given el ADK runtime está activo
    When llamo a tool "adk_list_agents"
    Then recibo agentes registrados
    And al menos "sales-agent" está presente

  Scenario: Happy Path — Multi-Provider routing
    Given el Provider Router está configurado
    When resuelvo provider para capability "research"
    Then el provider es "openrouter"
    And el modelo es "google/gemini-2.5-flash"

  Scenario: Edge Case — Token inválido
    Given el MCP Gateway está corriendo
    When envío GET /api/tools con Authorization: Bearer token_invalido
    Then recibo 401 Unauthorized
    And el error contiene "Token inválido o expirado"

  Scenario: Edge Case — Sin autenticación
    Given el MCP Gateway está corriendo
    When envío GET /api/tools sin header Authorization
    Then recibo 401 Unauthorized
    And el error contiene "token Bearer"

  Scenario: Edge Case — Tool no encontrada
    Given el MCP Gateway está autenticado
    When envío POST /api/call con tool="tool_inexistente"
    Then recibo 404
    And el error contiene "no encontrada"

  Scenario: Edge Case — Capability sin match
    Given el CapabilityRegistry está cargado
    When resuelvo task="xyz123 random noise"
    Then recibo capability con fallback=true
    And agent es "ResearchAgent"

  Scenario: Edge Case — Rate limit excedido
    Given el tenant "free" tiene rate limit 10 req/min
    When se excede el límite
    Then recibo 429
    And el error contiene "Rate limit"
