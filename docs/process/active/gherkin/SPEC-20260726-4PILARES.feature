Feature: Multi-Tenant Platform — 4 Pillars Architecture
  As a platform operator (Mystic)
  I want Sonora Platform to be a SaaS multi-tenant platform with 4 pillars
  So that I can scale to hundreds of clients without rewriting the core

  Background:
    Given the system has Postgres with RLS enabled
    And the system has Redis with namespace isolation
    And the system has Qdrant with per-tenant collections

  Scenario: Happy path — New tenant signs up and activates
    Given a new tenant "Acme Corp" signs up for the Pro plan ($149/mes)
    When the tenant completes Stripe checkout
    Then the tenant is created in Postgres with plan "pro" and status "trial"
    And a Qdrant collection "tenant_{id}" is created
    And Redis namespace "tenant:{id}:" is initialized
    And a welcome email is sent
    And the tenant can login at their custom subdomain
    And the tenant sees features: 3 agents, WhatsApp+Web, 10K interactions

  Scenario: Edge case — Tenant upgrades mid-cycle with prorating
    Given tenant "Acme Corp" is on Starter plan ($49/mes) since day 1
    When on day 15 the tenant upgrades to Pro ($149/mes)
    Then the plan changes immediately to "pro"
    And features are activated instantly (more agents, more channels)
    And the next invoice is prorated: (days_remaining / 30) * ($149 - $49)
    And the tenant can immediately use Pro features
    And no data is lost during the transition

  Scenario: Tenant data isolation — Cross-tenant access denied
    Given Tenant A has a client record "Juan Pérez" with phone "+521234567890"
    And Tenant B has a client record "María García" with phone "+529876543210"
    When Tenant A queries their clients via API
    Then Tenant A sees only "Juan Pérez"
    And Tenant A does NOT see "María García"
    And any query without tenant_id returns 403 Forbidden

  Scenario: Partner white-label — Partner sees their price, not SDC cost
    Given Partner César (AztroTech) has commission 30%
    And César sets call price at $3.00 for his clients
    When a client makes a call
    Then the client is charged $3.00
    And SDC deducts its real cost ($0.15)
    And SDC deducts its commission (5% = $0.15)
    And César sees in his dashboard: "Earned: $2.70"
    And César does NOT see SDC's real cost ($0.15)
    And César does NOT see SDC's commission (5%)

  Scenario: Agent orchestrates capabilities — Sales Agent calls AI + Memory + WhatsApp
    Given the Sales Agent receives a new lead via WhatsApp channel
    When the Orchestrator routes the lead to Sales Agent
    Then Sales Agent uses AI Capability to analyze lead intent
    And Sales Agent uses Memory Capability to check if lead exists in Engram
    And Sales Agent uses WhatsApp Channel Capability to send follow-up
    And all operations include tenant_id in context
    And each capability call is rate-limited per tenant plan

  Scenario: Grace period expiration — Non-paying tenant is soft-locked
    Given tenant has status "trial" with trial_ends_at = 7 days ago
    When the daily cron runs
    Then tenant status changes to "suspended"
    And all features return 402 Payment Required
    And data is preserved (not deleted)
    And the tenant receives "Payment required" email
    And when the tenant pays, status returns to "active" with data intact

  Scenario: Marketplace agent installation
    Given the Agent Marketplace has a "Cold Caller Pro" agent published by Partner X
    When tenant "Acme Corp" installs "Cold Caller Pro"
    Then the agent harness is copied to Acme's namespace
    And the agent appears in Acme's agent dashboard
    And Partner X earns 80% of the $99 installation fee
    And SDC earns 20% of the $99 installation fee
    And the agent passes all certification tests before installation

  Scenario: Rate limiting per tenant — One tenant cannot degrade others
    Given Tenant A (Starter plan, 1K interactions/day limit)
    And Tenant B (Enterprise plan, unlimited)
    When Tenant A sends 1500 requests in one hour (exceeds limit)
    Then Tenant A's requests are rate-limited with 429 Too Many Requests
    And Tenant B continues to get responses normally
    And an alert is logged: "Tenant A exceeded rate limit"
    And Tenant A's requests are queued with backpressure, not dropped
