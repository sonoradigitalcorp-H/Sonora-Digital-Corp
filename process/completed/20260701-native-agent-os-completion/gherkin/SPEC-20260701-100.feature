Feature: Native Agent OS Completion
  Scenario: Security audit runs
    Given the gateway is up
    When I call audit_run
    Then I get a score >= 70%
  
  Scenario: Billing generates invoice
    Given a tenant exists
    When I call billing_invoice
    Then an invoice is created
  
  Scenario: Auto-heal revives services
    Given a service is down
    When auto_heal runs
    Then it attempts recovery
