Feature: Clone Person
  As a marketing client
  I want to clone my likeness and voice
  So that I can generate personalized advertising content

  Background:
    Given the system has a clone-agent running
    And consent form template is available

  @P1 @critical
  Scenario: Client places a clone order with valid inputs
    Given a client with 10 photos and 45s of audio
    And a signed consent form
    When the clone order is placed
    Then the system creates an order with status "pending"
    And the system starts training LoRA model
    And the system starts training voice clone
    And the order status changes to "training"

  @P1 @critical
  Scenario: Training completes successfully
    Given an order in "training" status
    When LoRA training completes with loss < 0.15
    And voice training completes with similarity > 85%
    Then the system updates order status to "models_ready"
    And model URIs are available in the order

  @P2
  Scenario: Content generation from trained models
    Given an order in "models_ready" status
    And a brand creative brief
    When content generation is requested for 3 variants
    Then the system generates 3 video variants
    And each variant includes the required disclosure label

  @P3
  Scenario: Delivery to client
    Given an order with generated content
    When delivery is requested
    Then the system packages all assets
    And sends a delivery notification to the client
    And original media is marked for deletion in 30 days

  @security @critical
  Scenario: Training rejected without consent
    Given a client with 10 photos and 45s of audio
    And no signed consent form
    When the clone order is placed
    Then the system rejects the order with error "CONSENT_REQUIRED"
