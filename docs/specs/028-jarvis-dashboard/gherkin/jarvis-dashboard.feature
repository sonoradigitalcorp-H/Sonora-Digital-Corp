Feature: Jarvis Dashboard UI
  As a Jarvis user
  I want an interactive dashboard to monitor Jarvis
  So that I can see what Jarvis is doing in real-time

  Background:
    Given the dashboard is loaded
    And the user is authenticated
    And the WebSocket connection is established

  Scenario: Happy path - Display 3D scene with voice activity
    Given the dashboard loads successfully
    When the 3D scene initializes
    Then the Jarvis avatar should be visible
    And the particle effects should be ready
    When the user activates the microphone
    Then the voice visualization should respond to audio
    And the waveform should display in real-time

  Scenario: Happy path - Show action feed with screenshots
    Given Jarvis is executing actions
    When an action completes
    Then the action should appear in the action feed
    And the action status should be displayed
    When a screenshot is captured
    Then the screenshot should appear inline in the feed
    And the thumbnail should be clickable for full view

  Scenario: Edge case - High memory usage optimization
    Given the dashboard is running with many client worlds
    When memory usage exceeds 500MB
    Then the dashboard should reduce particle effects
    And the dashboard should lazy-load off-screen elements
    And a warning should be displayed to the user
    And the dashboard should continue functioning