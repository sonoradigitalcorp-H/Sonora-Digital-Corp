Feature: Cognitive Kernel Foundations
  Unify truth, events, planning, verification, and knowledge graph

  Background:
    Given the system has truth/ directory at project root
    And Neo4j is running on 127.0.0.1:7687
    And Python 3.14 is available

  # ── A1: Truth YAML ──

  Scenario: Truth YAML files are valid
    Given truth/ directory exists
    When I validate each YAML file against its schema
    Then all files have required fields (version, domain, rules)
    And no two files have conflicting rules

  Scenario: Policies are migrated from TRUTH.md to truth/
    Given TRUTH.md contains policies P1-P8
    When I run migrate-policies script
    Then each policy exists in the corresponding truth/ YAML file
    And the YAML version is machine-parseable

  Scenario: Truth Guardian reads from truth/
    Given truth-guardian is running
    When I check its configuration source
    Then it reads rules from truth/ instead of TRUTH.md

  # ── A2: Universal Event Bus ──

  Scenario: Event is emitted with valid schema
    Given emit-event.py is installed
    When I emit an event with all required fields
    Then the event is appended to state/events/events.jsonl
    And the JSON is valid against the schema

  Scenario: Event with invalid schema is rejected
    Given emit-event.py is installed
    When I emit an event missing required fields
    Then the script exits with non-zero code
    And the error message specifies which field is missing

  Scenario: Event bus rotates at 10k lines
    Given state/events/events.jsonl has 10000 lines
    When I emit one more event
    Then the file is archived to events.archive.N.jsonl
    And a fresh events.jsonl is started

  Scenario: Legacy events are migrated
    Given 15 events.jsonl files exist in process/completed/
    When I run migrate-events.py
    Then state/events/events.jsonl contains all events
    And the count matches the sum of all legacy files

  # ── A3: Planning Gate ──

  Scenario: Plan is created before execution
    Given no active plan exists
    When I run plan-gate.py with a task objective
    Then a PLAN.yaml is generated
    And it contains decomposed tasks with dependencies
    And an event "plan.created" is emitted

  Scenario: Plan is validated against truth/
    Given truth/ has policies about architecture
    When plan-gate.py validates the plan
    Then it checks the plan does not violate truth/ rules

  # ── A4: Verification Pipeline ──

  Scenario: Truth Gate passes with valid output
    Given verify-gate.py is installed
    When the output does not contradict truth/
    Then the truth gate passes
    And an event "gate.passed" is emitted

  Scenario: Truth Gate fails with violating output
    Given verify-gate.py is installed
    When the output contradicts a truth/ rule
    Then the truth gate fails with STOP
    And the error explains which rule was violated
    And suggests a fix

  Scenario: All three gates run in sequence
    Given verify-gate.py is installed
    When I run it against a plan
    Then truth gate, security gate, and cost gate execute in order
    And each gate emits an event

  # ── A5: Knowledge Graph ──

  Scenario: Graph is populated from events
    Given state/events/events.jsonl has events
    When I run populate-graph.py
    Then Neo4j has nodes for each event type
    And relationships connect related nodes

  Scenario: Traceability query works
    Given Neo4j has populated data
    When I query "Why does this file exist?"
    Then the result shows Feature -> Spec -> Task -> Commit -> PR -> Deploy

  Scenario: Agent query works
    Given Neo4j has populated data
    When I query "Which agents touched this service?"
    Then the result shows agent names and commit counts

  # ── A6: CONDUCT.md + CI ──

  Scenario: CONDUCT.md enforces gates
    Given CONDUCT.md exists
    When I check the required steps
    Then Planning Gate is listed as mandatory
    And Verification Pipeline is listed as mandatory
    And Event Bus is listed as a requirement

  Scenario: CI runs truth validation
    Given a GitHub PR is opened
    When CI runs
    Then it validates truth/ YAML files
    And runs the test suite
    And runs verify-gate
