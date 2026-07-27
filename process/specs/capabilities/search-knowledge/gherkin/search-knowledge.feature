Feature: Search Knowledge
  As a system operator
  I want to search across all memory stores
  So that I can find relevant knowledge quickly

  Background:
    Given the system has Neo4j and Qdrant running

  @P1 @critical
  Scenario: Basic semantic search
    Given documents stored in Qdrant with embeddings
    When I search for "artist revenue trends"
    Then results are ranked by cosine similarity
    And each result includes source provenance
    And top 10 results are returned within 2s

  @P2
  Scenario: Graph traversal search
    Given a Neo4j graph with artist relationships
    When I search for "collaborators of Bad Bunny"
    Then the system traverses max 3 hops
    And returns related artist nodes

  @P2
  Scenario: Empty query rejected
    Given no query text
    When I submit an empty search
    Then the system returns no results
    And status is "invalid_query"
