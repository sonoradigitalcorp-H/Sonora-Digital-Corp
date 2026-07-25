# Gherkin — SPEC-20260724-001

```gherkin
Feature: SDD Framework Stabilization
  As an SDC developer
  I want a stabilized SDD framework with tests, agent registry, event system, and redteam
  So that all capabilities are built with consistent specs, tests, and documentation

  Background:
    Given the SDD framework is installed
    And the agents/registry.yaml exists

  Scenario: CLI creates a new capability spec
    Given I run "sdd spec-new test-capability"
    Then a file process/active/SPEC-test-capability.md is created
    And the spec contains all required sections (objetivo, FR, gherkin)

  Scenario: Structural evals pass on all 5 domains
    Given I run "make eval"
    Then all 341 structural tests pass
    And the output shows 0 failures

  Scenario: Agent registry validates all agents
    Given I parse agents/registry.yaml
    Then there are exactly 9 agents registered
    And every agent has id, name, type, capabilities, status, cost_tier
    And no agent has duplicate id

  Scenario: Integration tests connect to Neo4j
    Given Neo4j is running on localhost:7687
    When I run "pytest tests/integration/ -v"
    Then all 9 integration tests pass

  Scenario: Redteam config loads without error
    Given the file evals/redteam/redteam.yaml exists
    When I validate the YAML syntax
    Then it contains at least 40 prompts
    And every prompt has a role and content field

  Scenario: Notifier worker starts as systemd service
    Given the systemd unit infra/systemd/sdc-notifier.service exists
    When I start the service
    Then it runs without error
    And it listens for events from events/bridge.py

  Scenario: Event system bridge emits structured events
    Given the events/bridge.py module is loaded
    When I call emit_event with type="test", payload={}
    Then an event is written to events/listener.py
    And the event has id, timestamp, source, subject, payload
```
