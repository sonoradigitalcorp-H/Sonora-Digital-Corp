Feature: Jarvis Action Router
  As a Jarvis user
  I want Jarvis to execute real actions on my behalf
  So that tasks are completed automatically

  Background:
    Given the Action Router is running
    And Playwright browser is initialized
    And database connection is established

  Scenario: Happy path - Navigate to URL and take screenshot
    Given I request to open "https://example.com"
    When the action router executes the action
    Then the browser should navigate to the URL
    And a screenshot should be captured
    And the result should include the screenshot path
    And the action status should be "completed"

  Scenario: Happy path - Database query with parameterization
    Given I request to query "SELECT * FROM users WHERE id = $1" with params [1]
    When the action router executes the action
    Then the query should execute with parameterized inputs
    And the result should include the query data
    And no SQL injection should be possible

  Scenario: Edge case - Destructive action requires confirmation
    Given I request to delete record with id 42
    When the action router receives the request
    Then the action status should be "confirming"
    And a confirmation request should be sent to the client
    When the user confirms the action
    Then the action should execute
    And the action status should be "completed"

  Scenario: Edge case - Browser crash triggers recovery
    Given the browser process crashes during navigation
    When the action router detects the crash
    Then a new browser instance should be started
    And the action should be retried automatically
    And the result should include recovery information