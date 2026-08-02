Feature: Agent City
  As a visitor
  I want to see agents represented as houses in a miniature city
  So that I can intuitively explore the system

  Scenario: City shows all tenants as houses
    Given there are 5 tenants in the registry
    When I open the main page
    Then I see 5 houses arranged in a grid
    And each house has the tenant's name and a colored roof

  Scenario: Hover on house shows back side
    Given I am viewing a house
    When I hover over it
    Then the house tilts to show the back side
    And the back side shows a hermetic phrase

  Scenario: Click on house opens Yu-Gi-Oh card
    Given I am viewing a house
    When I click on it
    Then a Yu-Gi-Oh style card appears
    And the card shows: name, stats, description, and services

  Scenario: Card can be flipped
    Given a Yu-Gi-Oh card is open
    When I click "Voltear"
    Then the card flips to show services
