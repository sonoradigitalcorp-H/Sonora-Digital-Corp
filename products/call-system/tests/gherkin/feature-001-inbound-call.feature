Feature: Inbound Call
  As a potential client
  I want to call the system via WebRTC
  So that I can talk to an AI assistant

  Background:
    Given the call server is running on port 8000
    And I have a browser with WebRTC support

  Scenario: New caller provides name and gets registered
    Given I open the call page
    When I click "Llamar"
    And I say "Hola, soy Juan Pérez"
    Then the system responds "¡Hola Juan! Bienvenido a Sonora Digital Corp."
    And a new tenant "Juan Pérez" is created

  Scenario: Returning caller is recognized
    Given tenant "Juan Pérez" already exists with phone "+5216621234567"
    When I call and say "Soy Juan Pérez"
    Then the system greets me by name
    And the call is logged under my existing tenant

  Scenario: Caller uses objection
    Given I am on a call with the system
    When I say "No me interesa"
    Then the system uses the objection handling method
    And the objection is logged
