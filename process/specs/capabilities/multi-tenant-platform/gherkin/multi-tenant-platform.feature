Feature: Multi-Tenant Platform Isolation
  As a platform operator
  I want each tenant to have isolated configuration, memory, and tools
  So that tenants never access each other's data and onboarding is instantaneous

  Background:
    Given the SDD framework is initialized
    And the TenantResolver is available in core/tenants/

  @FR1 @FR2
  Scenario: Core is agnostic of tenant identity
    Given the repository structure
    When I search for hardcoded tenant names in core/
    Then no tenant IDs should appear hardcoded in core/

  @FR3
  Scenario: TenantResolver loads context at runtime
    Given a valid tenant_id "sonora-digital"
    When the resolver loads its context
    Then it should return prompt.md content
    And it should return allowed_tools from tools.yaml
    And it should return mcp_servers from mcp.yaml

  @FR4
  Scenario: Tenant skills are isolated
    Given tenant "sonora-digital" has skills/ directory
    And tenant "abe-music" has different skills/
    When the orchestrator processes a request for sonora-digital
    Then it should NOT load skills from other tenants

  @FR5
  Scenario: Qdrant collections are tenant-scoped
    Given the RAG pipeline is active
    When a vector search is performed for a tenant
    Then the query should include a tenant_id filter
    Or the query should target the tenant-specific collection

  @FR6
  Scenario: Neo4j databases are tenant-scoped
    Given a Cypher query is executed
    When the query originates from tenant "abe-music"
    Then the query should target database or include WHERE n.tenant_id = tenant_id

  @FR7
  Scenario: Postgres RLS prevents cross-tenant access
    Given postgres tables have tenant_id columns
    When a query is executed with current_setting('app.current_tenant') = 'sonora-digital'
    Then it should only return rows with matching tenant_id

  @FR8
  Scenario: Gateway routes by tenant
    Given a webhook arrives at /webhook
    When the header X-Tenant-ID is set
    Then the gateway routes to the correct tenant's agent instance

  @FR9
  Scenario: New client from template
    Given the _template/ directory exists
    When I copy it to clients/nuevo-cliente/
    And replace {{TENANT_ID}} with "nuevo-cliente"
    Then the tenant should be operational in < 5 minutes

  @FR10
  Scenario: clients/ is the standard
    Given the repository structure
    When I list tenants for active client configs
    Then all clients should be in clients/ directory

  @FR12
  Scenario: Policy Engine validates tool access
    Given tenant "sonora-digital" has tools.yaml with blocked_tools: [github_deploy]
    When the agent attempts to use github_deploy
    Then the Policy Engine should block the call
