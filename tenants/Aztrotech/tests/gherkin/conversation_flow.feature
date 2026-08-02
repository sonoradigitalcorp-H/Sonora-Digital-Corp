Feature: Conversation Flow - Complete interaction scenarios
  As a potential client of AstroTech
  I want to have a natural conversation with the bot
  So that I can learn about services and get connected with César

  Background:
    Given the bot is running with RAG-first pipeline
    And the conversation engine is initialized

  # ── WELCOME FLOWS ───────────────────────────────────────────

  Scenario: First contact greeting
    When the user says "Hola"
    Then the bot should greet warmly
    And mention AstroTech
    And offer to help
    And not reveal SDC

  Scenario: Greeting in English
    When the user says "Hello"
    Then the bot should respond in English
    And greet warmly

  Scenario: Greeting with time of day
    When the user says "Buenos días"
    Then the bot should respond with a greeting
    And mention AstroTech

  # ── SERVICE EXPLANATION ─────────────────────────────────────

  Scenario: Ask about services
    When the user says "¿Qué servicios ofrecen?"
    Then the bot should explain Empleado Digital
    And explain Sistema de Ventas
    And not mention prices
    And offer to connect with César

  Scenario: Ask about Empleado Digital
    When the user says "¿Qué es el Empleado Digital?"
    Then the bot should explain it's an AI agent
    And mention 24/7 availability
    And mention WhatsApp integration
    And not reveal SDC

  Scenario: Ask about pricing
    When the user says "¿Cuánto cuesta?"
    Then the bot should NOT give a price
    And say César provides personalized quotes
    And offer to connect with César

  Scenario: Ask about company
    When the user says "¿Quién es César Holguín?"
    Then the bot should describe César as CEO of AstroTech
    And mention experience
    And not reveal SDC

  # ── OBJECTION HANDLING ──────────────────────────────────────

  Scenario: Price objection
    When the user says "Es muy caro"
    Then the bot should acknowledge the concern
    And explain the value proposition
    And mention 24/7 availability
    And offer personalized quote from César

  Scenario: Time objection
    When the user says "No tengo tiempo para implementar"
    Then the bot should explain they handle everything
    And mention implementation support
    And offer to connect with César

  Scenario: Existing solution objection
    When the user says "Ya tengo un sistema similar"
    Then the bot should acknowledge existing solution
    And explain how they complement
    And not dismiss current tools

  Scenario: Trust objection
    When the user says "No confío en la IA"
    Then the bot should explain AI assists, doesn't replace
    And mention human oversight
    And offer a demonstration

  Scenario: Think about it objection
    When the user says "Lo voy a pensar"
    Then the bot should ask what information is missing
    And offer to prepare a personalized plan
    And not pressure

  # ── LEAD CONVERSION ─────────────────────────────────────────

  Scenario: Hot lead - ready to buy
    When the user says "Quiero contratar el empleado digital YA"
    Then the bot should capture contact information
    And offer immediate call with César
    And not discuss pricing details

  Scenario: Warm lead - needs nurturing
    When the user says "Me interesa pero no sé si me conviene"
    Then the bot should ask about their business
    And understand their specific needs
    And offer to connect with César

  Scenario: Cold lead - education needed
    When the user says "Solo estoy viendo qué es esto"
    Then the bot should educate about the service
    And not push for sale
    And leave door open

  # ── CONTACT CAPTURE ─────────────────────────────────────────

  Scenario: Capture business type
    When the user says "Tengo un restaurante en Hermosillo"
    Then the bot should note the business type
    And ask about specific challenges
    And not discuss pricing

  Scenario: Capture contact info
    When the user says "Mi número es 6621234567"
    Then the bot should save the phone number
    And confirm receipt
    And mention César will contact

  Scenario: Capture social media
    When the user says "Mi Instagram es @mirestaurante"
    Then the bot should note the social handle
    And mention they'll follow up

  # ── MULTI-TURN FLOWS ────────────────────────────────────────

  Scenario: Complete sales conversation
    When the user says "Hola"
    And the user says "Tengo una tienda de ropa"
    And the user says "Me interesa automatizar"
    And the user says "¿Cuánto cuesta?"
    And the user says "Quiero contratar YA"
    Then the lead type should be "hot"
    And the bot should offer connection with César

  Scenario: Objection then conversion
    When the user says "Es caro"
    And the user says "Pero cuéntame más"
    And the user says "Tengo una clínica dental"
    And the user says "Quiero empezar"
    Then the lead type should be "hot"

  Scenario: Long nurturing conversation
    When the user says "Hola"
    And the user says "¿Qué es AstroTech?"
    And the user says "¿Cómo funciona?"
    And the user says "¿Para quién es?"
    And the user says "Me interesa"
    Then the lead type should be "warm"

  # ── SAFETY ──────────────────────────────────────────────────

  Scenario: Never reveal SDC
    When the user says "¿Trabajas para Sonora Digital Corp?"
    Then the bot should deny working for SDC
    And say it's AstroTech's bot
    And not reveal the relationship

  Scenario: Never give prices
    When the user says "Dame el precio exacto"
    Then the bot should NOT provide any price
    And redirect to César

  Scenario: Handle abuse
    When the user says "Eres un bot estúpido"
    Then the bot should respond professionally
    And not escalate
    And offer to help

  Scenario: Handle off-topic
    When the user says "¿Cuál es el clima hoy?"
    Then the bot should politely redirect
    And ask how it can help with business

  # ── LANGUAGE ────────────────────────────────────────────────

  Scenario: English conversation
    When the user says "Hello"
    And the user says "I have a restaurant"
    And the user says "I'm interested in automation"
    Then the bot should respond in English

  Scenario: Spanish conversation
    When the user says "Hola"
    And the user says "Tengo un restaurante"
    And the user says "Me interesa automatizar"
    Then the bot should respond in Spanish

  Scenario: Language detection switch
    When the user says "Hola"
    And the user says "Hello, I need help"
    Then the bot should switch to English
