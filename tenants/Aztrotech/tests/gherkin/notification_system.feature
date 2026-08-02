Feature: Notification System - Alerts and summaries
  As César (CEO of AstroTech)
  I want to receive notifications about leads and system status
  So that I can act quickly on opportunities

  Background:
    Given the notification bot is running
    And the n8n bridge is active on port 8767

  # ── LEAD NOTIFICATIONS ──────────────────────────────────────

  Scenario: Hot lead notification
    When a lead with score 85 is detected
    Then a notification should be sent to César
    And the notification should include lead name
    And the notification should include phone number
    And the notification should include score
    And the notification should include urgency level

  Scenario: Warm lead notification
    When a lead with score 50 is detected
    Then a notification should be sent to César
    And the notification should include lead details

  Scenario: Cold lead no notification
    When a lead with score 20 is detected
    Then NO notification should be sent immediately
    But the lead should be logged in database

  Scenario: Multiple hot leads
    When 3 hot leads are detected in 1 hour
    Then César should receive 3 separate notifications
    And each should have different lead details

  # ── DAILY SUMMARIES ────────────────────────────────────────

  Scenario: Daily summary at 9am
    Given it is 9:00 AM
    When the daily summary runs
    Then César should receive a summary
    And it should include conversations count
    And it should include leads count
    And it should include hot leads count
    And it should include token cost

  Scenario: Daily summary with no activity
    Given it is 9:00 AM
    And there were no conversations yesterday
    When the daily summary runs
    Then César should receive "No hubo actividad ayer"

  # ── SYSTEM ALERTS ───────────────────────────────────────────

  Scenario: TTS server down alert
    When the TTS server stops responding
    Then an alert should be sent to César
    And the alert should indicate TTS is down

  Scenario: Qdrant down alert
    When Qdrant stops responding
    Then an alert should be sent to César
    And the alert should indicate RAG is unavailable

  Scenario: Bot restart alert
    When the main bot restarts
    Then César should be notified
    And the notification should include restart time

  # ── N8N INTEGRATION ─────────────────────────────────────────

  Scenario: n8n bridge health check
    When I check n8n bridge status
    Then the response should be "ok"
    And it should include conversation count
    And it should include TTS status
    And it should include Qdrant status

  Scenario: n8n lead webhook
    When n8n sends a lead_hot webhook
    Then the lead should be saved to database
    And a notification should be sent to César

  Scenario: n8n followup trigger
    When n8n sends a followup webhook
    Then the followup should be logged
    And the lead should be marked for followup

  # ── AUTO-HEALING ────────────────────────────────────────────

  Scenario: Auto-heal detects bot down
    Given the bot service is stopped
    When the auto-heal cron runs
    Then the bot should be restarted
    And a log entry should be created

  Scenario: Auto-heal detects TTS down
    Given the TTS service is stopped
    When the auto-heal cron runs
    Then the TTS should be restarted

  Scenario: Auto-heal detects Postgres down
    Given the Postgres container is stopped
    When the auto-heal cron runs
    Then the Postgres container should be restarted

  Scenario: Auto-heal detects Redis down
    Given the Redis container is stopped
    When the auto-heal cron runs
    Then the Redis container should be restarted

  # ── NOTIFICATION BOT COMMANDS ────────────────────────────────

  Scenario: /leads command
    When César sends "/leads"
    Then the bot should show recent leads
    And it should include lead names
    And it should include scores

  Scenario: /hot command
    When César sends "/hot"
    Then the bot should show hot leads only
    And it should sort by score descending

  Scenario: /summary command
    When César sends "/summary"
    Then the bot should show daily summary
    And it should include all metrics

  Scenario: /health command
    When César sends "/health"
    Then the bot should show system health
    And it should check TTS status
    And it should check Postgres status

  Scenario: /start command
    When César sends "/start"
    Then the bot should show available commands
    And explain its purpose
