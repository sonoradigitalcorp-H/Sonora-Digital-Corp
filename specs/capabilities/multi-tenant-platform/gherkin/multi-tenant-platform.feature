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
    Then no tenant names (astrotech, sonora-digital, abe-music) should appear

  @FR3
  Scenario: TenantResolver loads context at runtime
    Given a valid tenant_id "astrotech"
    When the resolver loads its context
    Then it should return prompt.md content
    And it should return allowed_tools from tools.yaml
    And it should return mcp_servers from mcp.yaml

  @FR4
  Scenario: Tenant skills are isolated
    Given tenant "astrotech" has skills/ directory
    And tenant "sonora-digital" has different skills/
    When the orchestrator processes a request for astrotech
    Then it should NOT load skills from sonora-digital/

  @FR5
  Scenario: Qdrant collections are tenant-scoped
    Given the RAG pipeline is active
    When a vector search is performed for tenant "astrotech"
    Then the query should include filter: { tenant_id: "astrotech" }
    Or the query should target collection "tenant_astrotech_memory"

  @FR6
  Scenario: Neo4j databases are tenant-scoped
    Given a Cypher query is executed
    When the query originates from tenant "abe-music"
    Then the query should target database "abe_music" or include WHERE n.tenant_id = "abe_music"

  @FR7
  Scenario: Postgres RLS prevents cross-tenant access
    Given postgres tables have tenant_id columns
    When a query is executed with current_setting('app.current_tenant') = 'astrotech'
    Then it should only return rows with tenant_id = 'astrotech'

  @FR8
  Scenario: Gateway routes by tenant
    Given a webhook arrives at /webhook
    When the header X-Tenant-ID is "astrotech"
    Then the gateway routes to astrotech's agent instance

  @FR9
  Scenario: New tenant from template
    Given the _template/ directory exists
    When I copy it to tenants/nuevo-cliente/
    And replace {{TENANT_ID}} with "nuevo-cliente"
    Then the tenant should be operational in < 5 minutes

  @FR10
  Scenario: clients/ is deprecated
    Given the archive/ directory exists
    When I list tenants/ for active client configs
    Then all clients should be in tenants/, not in clients/

  @FR12
  Scenario: Policy Engine validates tool access
    Given tenant "astrotech" has tools.yaml with blocked_tools: [github_deploy]
    When the agent attempts to use github_deploy
    Then the Policy Engine should block the call
