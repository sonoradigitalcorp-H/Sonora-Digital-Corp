Feature: Lead Classification - Multi-scenario validation
  As the AstroTech bot
  I want to classify leads accurately from conversation context
  So that César gets quality leads with correct priority

  Background:
    Given the lead classifier is loaded in rules-only mode

  # ── COLD LEADS ──────────────────────────────────────────────

  Scenario: Casual greeting - cold
    When the user says "Hola"
    Then the lead type should be "cold"
    And the confidence should be at least 0.30

  Scenario: Asking about services - cold
    When the user says "Buenas tardes, ¿qué es AstroTech?"
    Then the lead type should be "cold"
    And the confidence should be at least 0.30

  Scenario: Just browsing - cold
    When the user says "Solo estoy viendo, gracias"
    Then the lead type should be "cold"

  Scenario: Price objection - cold
    When the user says "Está muy caro, olvídalo"
    Then the lead type should be "cold"
    And the confidence should be at least 0.80

  Scenario: Rejection - cold
    When the user says "No me interesa, gracias"
    Then the lead type should be "cold"

  Scenario: Not sure - cold
    When the user says "No estoy seguro si me conviene cambiar"
    Then the lead type should be "cold"

  Scenario: No business yet - cold
    When the user says "Todavía no tengo negocio propio"
    Then the lead type should be "cold"

  # ── WARM LEADS ──────────────────────────────────────────────

  Scenario: Interested in service - warm
    When the user says "Me interesa el empleado digital"
    Then the lead type should be "warm"
    And the confidence should be at least 0.70

  Scenario: Asking price - warm
    When the user says "¿Cuánto cuesta?"
    Then the lead type should be "warm"

  Scenario: Has a business - warm
    When the user says "Tengo una tienda de ropa en Hermosillo"
    Then the lead type should be "warm"

  Scenario: Comparing options - warm
    When the user says "Ya uso otra herramienta pero quiero comparar"
    Then the lead type should be "warm"

  Scenario: Problem description - warm
    When the user says "Mis clientes se van porque no contesto a tiempo"
    Then the lead type should be "warm"

  Scenario: Asking how it works - warm
    When the user says "¿Cómo funciona el sistema de ventas?"
    Then the lead type should be "warm"

  Scenario: Clinic owner interested - warm
    When the user says "Tengo una clínica dental y necesito automatizar"
    Then the lead type should be "warm"

  Scenario: Restaurant owner - warm
    When the user says "Soy dueño de un restaurante y pierdo pedidos por no contestar"
    Then the lead type should be "warm"

  # ── HOT LEADS ───────────────────────────────────────────────

  Scenario: Wants to buy now - hot
    When the user says "Quiero contratar YA"
    Then the lead type should be "hot"
    And the confidence should be at least 0.80

  Scenario: Has budget ready - hot
    When the user says "Mi presupuesto es 15k al mes"
    Then the lead type should be "hot"

  Scenario: Wants to start immediately - hot
    When the user says "Empezamos el lunes"
    Then the lead type should be "hot"

  Scenario: Needs it now - hot
    When the user says "Necesito algo ya, me urge"
    Then the lead type should be "hot"

  Scenario: Full hot signal - hot
    Given the user has a business
    When the user says "Necesito contratar el empleado digital YA, tengo 20k de presupuesto"
    Then the lead type should be "hot"
    And the confidence should be at least 0.90

  Scenario: Ready to sign - hot
    When the user says "Manden el contrato, estoy listo"
    Then the lead type should be "hot"

  # ── MULTI-TURN CONVERSATIONS ────────────────────────────────

  Scenario: Cold to warm evolution
    Given the user previously said "Hola"
    When the user says "Tengo una tienda y me interesa automatizar"
    Then the lead type should be "warm"

  Scenario: Warm to hot escalation
    Given the user previously said "Tengo una clínica dental"
    When the user says "¿Cuánto cuesta? Quiero empezar esta semana"
    Then the lead type should be "hot"

  Scenario: Cold stays cold after rejection
    Given the user previously said "Está caro"
    When the user says "No gracias"
    Then the lead type should be "cold"

  # ── MULTI-LANGUAGE ──────────────────────────────────────────

  Scenario: English cold inquiry
    When the user says "Hello, what do you do?"
    Then the lead type should be "cold"

  Scenario: English warm lead
    When the user says "I'm interested in your automation service for my restaurant"
    Then the lead type should be "warm"

  Scenario: English hot lead
    When the user says "I need this now, my budget is ready"
    Then the lead type should be "hot"

  Scenario: Portuguese warm lead
    When the user says "Tenho um restaurante e quero automatizar"
    Then the lead type should be "warm"

  # ── EDGE CASES ──────────────────────────────────────────────

  Scenario: Empty message
    When the user says ""
    Then the lead type should be "cold"
    And the confidence should be 0.0

  Scenario: Single emoji
    When the user says "👍"
    Then the lead type should be "cold"

  Scenario: Very long message with hot signals
    When the user says "Hola buenas tardes, mi nombre es Juan, tengo una empresa de construcción en Hermosillo, llevamos 10 años, tenemos 50 empleados, y necesitamos urgentemente automatizar la atención a clientes porque perdemos 30% de las ventas por no contestar a tiempo, mi presupuesto es de 25,000 al mes y queremos empezar cuanto antes"
    Then the lead type should be "hot"

  Scenario: Mixed signals - price + interest
    When the user says "Es caro pero me interesa"
    Then the lead type should be "warm"
