Feature: Twilio Voice Bridge
  As a partner (e.g. César)
  I want Mystic to receive and make phone calls with voice AI
  So that my clients have 24/7 voice support

  Background:
    Given Twilio is configured with valid credentials
    And Kokoro TTS is running
    And Whisper STT is loaded

  Scenario: Inbound call - client calls support
    When a client calls the Twilio number
    Then Mystic answers with a greeting in Spanish
    And the conversation is transcribed via Whisper
    And the response is synthesized via Kokoro
    And the transcript is saved to Engram

  Scenario: Outbound call - agent calls a lead
    When César initiates an outbound call to a lead
    Then Twilio calls the lead's number
    And when the lead answers, Mystic speaks the sales pitch
    And the lead's responses are processed by deepseek
    And the call result is saved to the CRM

  Scenario: Concurrent calls
    When 3 clients call simultaneously
    Then all 3 calls are handled with independent state
    And each call has its own Engram context
    And no audio leaks between calls

  Scenario: Call cost tracking
    When a call completes
    Then the duration and cost are logged in cost_tracker
    And the partner sees the cost at their defined rate
    And SDC's commission is recorded separately (hidden)
