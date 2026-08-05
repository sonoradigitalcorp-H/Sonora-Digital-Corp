Feature: Event Bus
  As a user of Harvis OS
  I want events to be published and consumed
  So that components can communicate asynchronously

  Background:
    Given the Event Bus is initialized

  Scenario: Publish event
    When I publish event "task.created" from "dispatcher"
    Then the event should be stored
    And the event should have a valid id

  Scenario: List events
    Given I have published 3 events
    When I request the list of events
    Then I should get at least 3 events

  Scenario: Event statistics
    Given I have published events
    When I request event statistics
    Then I should get total events count
    And I should get events by type breakdown
