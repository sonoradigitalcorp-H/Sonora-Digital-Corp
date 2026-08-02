Feature: Redis Streams Nervous System
  As a system architect
  I want agent context and pipeline events published to Redis Streams
  So that the system is resilient and consumers can subscribe in real-time

  Background:
    Given Redis is configured with REDIS_HOST, REDIS_PORT
    And the orchestrator is initialized

  Scenario: Context persists in Redis Stream
    When an agent executes a task
    And push_context is called
    Then the context entry is available in Redis Stream "context:history"
    And get_context returns the entry

  Scenario: Pipeline events are dual-published
    When a lead is captured
    And _emit_event is called
    Then the event is written to events.jsonl
    And the event is pushed to Redis Stream "events:pipeline"

  Scenario: Fallback when Redis is down
    Given Redis is not available
    When push_context is called
    Then it falls back to local list
    And no exception is raised

  Scenario: Multiple agents write to stream
    Given 5 agents execute tasks sequentially
    When stream_read is called with count=10
    Then all 5 entries are returned
