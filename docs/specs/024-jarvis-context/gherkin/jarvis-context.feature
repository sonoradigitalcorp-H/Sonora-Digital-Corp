Feature: Jarvis Context Engine
  As a Jarvis user
  I want the system to remember my context across sessions
  So that I don't have to repeat myself

  Background:
    Given the Context Engine is running
    And the tenant "test-tenant" exists
    And all data sources are available

  Scenario: Happy path - Search returns fused context from all sources
    Given I have data in engram, postgres, and qdrant
    When I search for "previous meeting notes"
    Then the search should return results from all sources
    And the fusion engine should combine results by relevance
    And the response should be within 200ms
    And each result should include source and score

  Scenario: Edge case - Engram source unavailable
    Given engram service is down
    And I have data in postgres and qdrant
    When I search for "client information"
    Then the search should return results from postgres and qdrant
    And a warning should be logged about engram unavailability
    And the response should still be within 200ms

  Scenario: Edge case - All sources unavailable
    Given all external services are down
    When I search for "any context"
    Then the search should return an empty result
    And an error should be returned with source status
    And no exception should be thrown