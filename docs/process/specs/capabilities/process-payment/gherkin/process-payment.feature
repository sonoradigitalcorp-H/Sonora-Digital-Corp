Feature: Process Payment
  As a finance agent
  I want to process payments via Stripe or Mercado Pago
  So that clients can pay for services

  @P1 @security
  Scenario: Process successful payment
    Given a valid payment intent of $500
    When I process the payment
    Then the payment is completed
    And a receipt is generated

  @P2 @security
  Scenario: Process refund
    Given a completed payment of $500
    When I process a full refund
    Then the refund is completed
    And the payment status changes to "refunded"

  @security
  Scenario: Reject invalid payment
    Given an invalid payment intent
    When I attempt to process the payment
    Then the system rejects with error "INVALID_PAYMENT"
