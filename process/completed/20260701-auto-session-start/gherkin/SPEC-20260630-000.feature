# Gherkin — SPEC-20260630-000

```gherkin
Feature: Auto Session Start
  As a user
  I want to see project status automatically when I start a session
  So that I don't waste time checking branch, git status, and context manually

  Background:
    Given I am in ~/sdc/

  @happy
  Scenario: Session start shows status
    Given I start a new session
    When the agent runs session-status.sh
    Then I see: branch name, changes pending, other active branches, last session summary

  @edge
  Scenario: No previous session saved
    Given state/ultima-sesion.json does not exist
    When the agent runs session-status.sh
    Then I see "(es la primera sesión o no se guardó resumen)" instead of an error

  @happy
  Scenario: Close session saves summary
    Given I am finishing my work
    When I confirm I want to save a summary
    Then state/ultima-sesion.json is created with branch, last commit, and resumen
```