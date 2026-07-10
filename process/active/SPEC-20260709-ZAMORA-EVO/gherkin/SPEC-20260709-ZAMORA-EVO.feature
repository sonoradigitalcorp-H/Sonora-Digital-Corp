Feature: Zamora Evolution
  As a visitor or client of Alejandro Zamora Brand Studio
  I want automated lead capture, AI agent support, recurring payments, and client dashboard
  So that the brand studio operates 24/7 without manual intervention

  Background:
    Given the Zamora system is operational
    And n8n is running on port 5678
    And Hermes Gateway is running on port 8643

  @happy-path
  Scenario: Lead capture via booking form
    Given a visitor is on the Zamora landing page
    When they fill the booking form with name, email, phone, and description
    And select 2 services
    And submit the form
    Then a lead is created in the CRM
    And a WhatsApp confirmation is sent to the visitor within 30 seconds
    And the admin receives a notification via Telegram
    And the lead is stored in Engram for follow-up

  @happy-path
  Scenario: AI agent answers pricing question via WhatsApp
    Given a client sends "Cuánto cuesta el plan Agente IA?" via WhatsApp
    When the Hermes agent receives the message
    Then the agent queries the pricing data from the Zamora API
    And responds with the correct price ($1,380 MXN/mes) and plan features
    And the conversation is stored in Engram

  @happy-path
  Scenario: Client views dashboard with active plan
    Given a client has an active "Conquistador" subscription
    When they log into zamora.sonoradigitalcorp.com
    Then they see their plan details
    And their content delivery progress
    And their analytics metrics
    And their payment history

  @edge-case
  Scenario: Duplicate lead detection
    Given a lead with email "test@example.com" already exists in CRM
    When the same email submits the booking form again
    Then the system detects the duplicate
    And updates the existing lead with new information
    And does not create a duplicate entry
    And sends a "Welcome back" message instead of new lead notification

  @edge-case
  Scenario: Failed recurring payment
    Given a client has an active subscription
    When Stripe reports a payment failure
    Then the system logs the failure in zamora-payments.json
    And sends a notification to the client via WhatsApp
    And retries the payment 3 times with 24h intervals
    And if all retries fail, downgrades the plan to restricted access

  @edge-case
  Scenario: AI agent without context fallback
    Given Engram is unavailable
    When a client asks about their project status via WhatsApp
    Then the agent detects Engram connection failure
    And responds with a generic message: "En este momento no tengo acceso a tus datos. Un agente humano te contactará pronto."
    And logs the error for admin review
