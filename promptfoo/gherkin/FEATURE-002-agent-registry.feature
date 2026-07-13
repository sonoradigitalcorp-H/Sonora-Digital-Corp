Feature: Agent Registry
  As a creator agent
  I want to define agents per tenant with specific tools and memory
  So that each company has a complete corps of agents

  Scenario: Tenant abe-music has exactly 6 agents
    Given Agents are registered for tenant "abe-music"
    When I query the registry
    Then I find exactly 6 agents
    And they are named: ceo, marketing, content, sales, support, voice

  Scenario: Tenant sdc has exactly 3 agents
    Given Agents are registered for tenant "sdc"
    When I query the registry
    Then I find exactly 3 agents
    And they are named: creator, quality, monitor

  Scenario: Each agent has a valid definition file
    Given Agent "content-agent" is defined for tenant "abe-music"
    When I read its definition file
    Then it has valid YAML frontmatter
    And it contains: name, tenant, role, tools, memory, channel, triggers
    And all listed tools exist in the tool registry

  Scenario: Agent tools exist in the MCP registry
    Given Agent "content-agent" uses tool "rag_search"
    When I check the tool registry
    Then rag_search is registered with its documentation

  Scenario: No two agents share the same Redis channel
    Given All agents are registered
    When I check their communication channels
    Then no channel is shared between agents
    And each channel follows the format "agent:{name}:{event}"

  Scenario: Agent triggers reference valid pipelines
    Given Agent "content-agent" has trigger "cron:06:00"
    When I check the cron-pipelines registry
    Then there is a pipeline scheduled at 06:00

  Scenario: Creator agent deploys a full company
    Given I run the creator agent to deploy "New Company"
    When it completes
    Then a tenant is created in Hasura
    And 6 agent definition files are created
    And the smart app is deployed at newcompany.sonoracorp.com
    And a Telegram notification confirms deployment
