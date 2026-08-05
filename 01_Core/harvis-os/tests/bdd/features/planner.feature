Feature: Task Planning
  As a user of Harvis OS
  I want complex tasks to be broken into steps
  So that they can be executed systematically

  Background:
    Given the Planner is initialized

  Scenario: Plan CRUD task
    When I request a plan for "Crear endpoint REST para usuarios"
    Then the plan should have at least 4 steps
    And the plan should require "openhands" agent
    And the plan status should be "pending"

  Scenario: Plan bugfix task
    When I request a plan for "Fix login error"
    Then the plan should have at least 4 steps
    And the plan status should be "pending"

  Scenario: Approve plan
    Given I have a plan
    When I approve the plan
    Then the plan status should be "approved"

  Scenario: Reject plan
    Given I have a plan
    When I reject the plan with reason "Not needed"
    Then the plan status should be "failed"
