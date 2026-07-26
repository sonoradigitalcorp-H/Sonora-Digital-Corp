Feature: Tokenomics Engine
  As a partner
  I want to set my own prices for AI actions
  So that I can maximize my margin and control my offer

  Background:
    Given the partner is authenticated
    And has at least 1 active agent

  Scenario: Partner sets call price
    When the partner sets "Llamada entrante" price to $3.00
    Then the system records the price in the token engine
    And the user sees $3.00 as the cost per call
    And SDC records internally that the real cost is $0.15

  Scenario: User pays token price
    When a user makes a call priced at $3.00
    Then the user is charged $3.00
    And $0.15 goes to SDC (infrastructure)
    And $2.85 goes to the partner

  Scenario: Partner sees dashboard (hidden costs)
    When the partner checks their earnings dashboard
    Then they see "$2.85" as the earning per call
    And they do NOT see "$0.15" or any SDC real cost
    And they see total earnings as $2,850.00 for 1000 calls

  Scenario: SDC commission is configurable
    Given the partner is a "Socio Fundador" tier
    When the partner sets a price of $3.00
    Then SDC commission is 10% ($0.30)
    And the partner earns $2.70

    Given the partner is a "Partner Normal" tier
    When the partner sets a price of $3.00
    Then SDC commission is 20% ($0.60)
    And the partner earns $2.40
