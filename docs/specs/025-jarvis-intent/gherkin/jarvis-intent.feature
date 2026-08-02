Feature: Jarvis Intent Classifier
  As a Jarvis user
  I want the system to understand my voice commands
  So that I can interact naturally with Jarvis

  Background:
    Given the Intent Classifier is running
    And the intent database is loaded
    And OpenRouter is available as fallback

  Scenario: Happy path - Classify calendar intent in Spanish
    Given the user says "Agenda una reunión mañana a las 3pm"
    When the classifier processes the input
    Then the intent should be "calendar"
    And the confidence should be above 0.7
    And parameters should include date "tomorrow" and time "3pm"

  Scenario: Happy path - Classify email intent in English
    Given the user says "Send an email to john@example.com"
    When the classifier processes the input
    Then the intent should be "email"
    And the confidence should be above 0.7
    And parameters should include recipient "john@example.com"

  Scenario: Happy path - Classify task intent with synonyms
    Given the user says "Mark my homework as done"
    When the classifier processes the input
    Then the intent should be "task"
    And the confidence should be above 0.7
    And parameters should include action "complete"

  Scenario: Edge case - Low confidence triggers LLM fallback
    Given the user says "do the thing with the stuff"
    When the classifier processes the input
    Then the keyword confidence should be below 0.7
    And OpenRouter should be called for classification
    And the response should include source "llm"

  Scenario: Edge case - Empty input handling
    Given the user sends an empty string
    When the classifier processes the input
    Then an error should be returned
    And the error message should indicate invalid input
    And no LLM call should be made