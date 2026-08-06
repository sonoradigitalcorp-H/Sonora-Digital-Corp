Feature: Task Classification
  As a user of Harvis OS
  I want my tasks to be automatically classified
  So that they are routed to the correct agent

  Background:
    Given the Dispatcher is initialized

  Scenario: Classify code task
    When I send a task "Create a function to validate emails"
    Then the task should be classified as "code"
    And the assigned agent should be "openhands"
    And the confidence should be greater than 0.8

  Scenario: Classify git task
    When I send a task "Make a commit with the changes"
    Then the task should be classified as "git"
    And the assigned agent should be "aider"
    And the confidence should be greater than 0.8

  Scenario: Classify deploy task
    When I send a task "Deploy the application to production"
    Then the task should be classified as "deploy"
    And the assigned agent should be "openhands"
    And the confidence should be greater than 0.8

  Scenario: Classify unknown task
    When I send a task "Something random that doesn't match"
    Then the task should be classified as "other"
    And the assigned agent should be "planner"
    And the confidence should be exactly 0.5

  Scenario: Simple task
    When I send a task "Do a commit"
    Then the task should be classified as "git"
    And the assigned agent should be "aider"
