Feature: Hermes MCP Integration
  As a developer using OpenCode
  I want to access Hermes Gateway skills via MCP
  So that I can invoke Hermes tools from my development environment

  Background:
    Given the Hermes MCP server is running
    And the OpenCode MCP client is configured
    And the API key is valid

  Scenario: Happy path - Invoke Hermes skill via MCP
    Given OpenCode is connected to Hermes MCP
    When I request to list available tools
    Then I should receive a list of 18 Hermes skills
    When I invoke the "calendar" tool with params {"action": "list", "date": "2026-08-02"}
    Then the tool should execute successfully
    And I should receive the calendar data
    And the response should be in MCP format

  Scenario: Edge case - Authentication failure
    Given OpenCode has an invalid API key
    When I request to list available tools
    Then I should receive an authentication error
    And the error message should indicate invalid credentials
    And no tool execution should occur