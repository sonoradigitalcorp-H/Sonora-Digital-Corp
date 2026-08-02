Feature: Jarvis WebSocket Bridge
  As a Jarvis user
  I want real-time communication with Jarvis
  So that I get instant responses and updates

  Background:
    Given the WebSocket server is running
    And the client is authenticated
    And the backend services are available

  Scenario: Happy path - Establish connection and exchange messages
    Given the client connects to the WebSocket server
    When the connection is established
    Then the server should acknowledge the connection
    And the client should receive a "connected" message
    When the client sends a text input message
    Then the server should process the message
    And the client should receive response chunks
    And the client should receive a "response_end" message

  Scenario: Happy path - Voice input streaming
    Given the client is connected via WebSocket
    When the client sends voice_chunk messages
    Then the server should buffer the audio chunks
    When the client sends a voice_end message
    Then the server should process the complete audio
    And the client should receive the transcription
    And the client should receive the response

  Scenario: Edge case - Connection drop and reconnection
    Given the client is connected to the WebSocket server
    When the network connection is interrupted
    Then the client should detect the disconnection
    And the client should attempt to reconnect
    And the client should use exponential backoff
    When the connection is restored
    Then the client should re-authenticate
    And the client should resume receiving messages