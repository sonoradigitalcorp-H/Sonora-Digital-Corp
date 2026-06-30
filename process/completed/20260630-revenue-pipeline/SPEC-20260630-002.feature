Feature: Sales Pipeline Automation
  As a business owner
  I want leads to flow through a fully automated sales pipeline
  So that revenue is generated without manual intervention

  Background:
    Given Neo4j is running
    And Mercado Pago credentials are configured
    And Telegram bot is active

  Scenario: Lead captured via Telegram and converted to customer
    Given a new contact sends "/cotizar" to the Telegram bot
    When the bot captures their nicho and plan preference
    And the lead is scored and qualified
    And a proposal is generated and sent
    When the lead accepts and pays via Mercado Pago
    Then the payment is confirmed
    And a customer is created in Neo4j
    And a welcome message is sent
    And the enterprise score is updated

  Scenario: Lead captured via web form
    Given a visitor submits the sales form on the web
    When the lead is created in Neo4j with source "web"
    And the lead score is calculated
    Then the lead appears in the dashboard

  Scenario: Proposal rejected
    Given a lead has received a proposal
    When the lead rejects the proposal
    Then the deal is marked as "lost"
    And the reason is logged

  Scenario: Duplicate lead from multiple sources
    Given a lead already exists in Neo4j from Telegram
    When the same email submits a web form
    Then the existing lead is updated with the new source
    And no duplicate is created
