Feature: Domain Architecture
  As a system engineer
  I want containers organized by domain with labels and survey
  So that the system architecture is explicit and monitorable

  Background:
    Given Docker is running
    And docker-compose.yml defines all services

  Scenario: All containers have domain labels
    When I run "docker ps --filter label=sdc.domain"
    Then containers are grouped by data, core, and ux

  Scenario: Survey reports all services
    When I run "bash scripts/agents-survey.sh"
    Then it shows health status for all endpoints
    And it shows Redis Stream lengths

  Scenario: Consumer groups exist
    When I check Redis Stream consumer groups
    Then "agents-core" and "agents-ux" groups exist for "events:pipeline"

  Scenario: Core depends on data, not on ux
    Given core containers have data dependencies
    When ux containers are stopped
    Then core containers continue to operate
