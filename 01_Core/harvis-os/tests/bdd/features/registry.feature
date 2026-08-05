Feature: Agent Registry
  As a user of Harvis OS
  I want to manage available agents
  So that the system knows which agents are available

  Background:
    Given the Agent Registry is initialized

  Scenario: List all agents
    When I request the list of agents
    Then I should get at least 4 agents
    And each agent should have an id, name, and status

  Scenario: Get specific agent
    When I request agent "openhands"
    Then I should get the agent details
    And the agent status should be "online"

  Scenario: Agent health check
    When I check health of agent "openhands"
    Then the health status should be "healthy"

  Scenario: List agents by capability
    When I request agents with capability "code"
    Then I should get at least 2 agents
    And all agents should have "code" capability
