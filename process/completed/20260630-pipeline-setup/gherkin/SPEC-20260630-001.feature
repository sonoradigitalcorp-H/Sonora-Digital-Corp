Feature: Pipeline System
  Scenario: New feature follows SDD
    Given I want to create a feature
    When I run spec-new
    Then a SPEC is created in process/active/
