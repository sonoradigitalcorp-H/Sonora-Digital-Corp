Feature: Integration Tests — Real Components
  As a developer
  I want components to work correctly with real dependencies
  So that the system works end-to-end

  Scenario: edge-tts generates valid 16kHz WAV
    Given The edge-tts Python module is available
    When A Spanish text is synthesized
    Then A WAV file is created with valid header
    And The WAV is 16kHz mono 16-bit PCM

  Scenario: WAV decodes to correct PCM frame count
    Given A WAV file of exactly 3 seconds
    When The WAV is decoded by decodeWAV
    Then The output has 50 frames (3s * 16000 / 960)

  Scenario: whisper transcribes Spanish audio
    Given A WAV file with spoken Spanish
    When Whisper transcribes the audio
    Then The output text is non-empty
    And The output matches the spoken content

  Scenario: Neo4j stores and retrieves a lead
    Given A running Neo4j instance
    When A lead with unique ID is saved
    Then The lead is retrievable by ID
    And The lead has the correct name and phone

  Scenario: Neo4j stores call history for a lead
    Given A lead exists in Neo4j
    When A call entry is added via SaveCall
    Then The call is linked to the lead
    And The call has timestamp and duration

  Scenario: OpenRouter responds within 10 seconds
    Given A valid OpenRouter API key
    When A test message is sent
    Then A non-empty response is received within 10s
