Feature: Voice Pipeline - End-to-end audio flow
  As a user chatting with AstroTech bot
  I want to receive voice responses
  So that I can listen to the bot's answers

  Background:
    Given the TTS server is running on port 8765
    And the voice pipeline is configured

  Scenario: TTS generates audio from text
    When I request TTS for "Hola, bienvenido a AstroTech"
    Then the audio file should be generated
    And the audio format should be WAV
    And the audio size should be greater than 10000 bytes

  Scenario: TTS converts to OGG opus
    Given I have a WAV audio file
    When I convert it to OGG opus
    Then the OGG file should exist
    And the OGG size should be less than the WAV size

  Scenario: Voice mode activation
    When the user says "modo voz"
    Then the bot should activate voice mode
    And the context should have "voz" set to true

  Scenario: Voice mode deactivation
    Given voice mode is active
    When the user says "modo texto"
    Then the bot should deactivate voice mode
    And the context should have "voz" set to false

  Scenario: TTS with different voices
    When I request TTS with voice "cesar" for "Prueba"
    Then the audio should use es-MX-DaliaNeural voice

  Scenario: TTS handles long text
    When I request TTS for a 500 character message
    Then the audio should be generated successfully
    And the audio duration should be less than 60 seconds

  Scenario: TTS handles special characters
    When I request TTS for "¿Cómo estás? ¡Muy bien! El precio es $1,500 MXN"
    Then the audio should be generated successfully

  Scenario: TTS handles emoji in text
    When I request TTS for "Hola 👋 bienvenido a AstroTech 🚀"
    Then the audio should be generated successfully

  Scenario: Voice pipeline end-to-end
    When a user sends a voice message
    Then the bot should transcribe it with STT
    And process it through the conversation engine
    And generate a TTS response
    And send it as a voice message

  Scenario: TTS server health check
    When I check TTS server health
    Then the response should contain "status": "ok"
    And the engine should be "edge-tts"

  Scenario: TTS server voices endpoint
    When I check available voices
    Then the response should include "cesar"
    And the voice should be "es-MX-DaliaNeural"
