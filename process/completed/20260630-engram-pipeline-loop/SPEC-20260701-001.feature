Feature: Engram Learning Loop
  As a system architect
  I want the pipeline to auto-store and auto-query learnings
  So that the system improves with every operation

  Background:
    Given Engram is initialized
    And process-pipeline.sh is installed

  Scenario: Spec completion stores learning
    When a spec is completed via "process-pipeline.sh complete"
    Then Engram contains a new memory with the spec_id
    And the memory has importance ≥ 1

  Scenario: Agent execution queries context
    When an agent is about to run
    Then it receives relevant past learnings in its context
    And the query returns at least 1 result if memories exist

  Scenario: Error stores as lección
    When a service fails (non-zero exit)
    Then a memory is stored with tag "error"
    And the error details are preserved in context
