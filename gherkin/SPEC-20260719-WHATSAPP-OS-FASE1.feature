# Gherkin — SPEC-20260719-WHATSAPP-OS-FASE1

```gherkin
Feature: Sonora OS v3 — WhatsApp Foundation
  As a Sonora OS operator
  I want a unified WhatsApp MCP server with persistent webhook
  So that all WhatsApp messaging is event-driven and fully automated

  Background:
    Given the WhatsApp MCP server is running
    And the event bus is connected
    And the system phone is "5216623538272"

  Scenario: Send text message via unified MCP
    Given a client with phone "5216622681111"
    When the operator calls "whatsapp_send_text" with message "Hola, bienvenido"
    Then the message is sent successfully
    And event "whatsapp:message:sent" is emitted
    And the payload contains "to" and "message_id"

  Scenario: Send voice note with auto-conversion
    Given a client with phone "5216622681111"
    And an MP3 file at "/tmp/sample.mp3"
    When the operator calls "whatsapp_send_voice"
    Then the MP3 is converted to OGG Opus
    And the voice note is sent successfully
    And event "whatsapp:message:sent" is emitted

  Scenario: Normalize Mexican phone number
    Given a client with phone "6622681111"
    When the operator calls "whatsapp_send_text"
    Then the number is normalized to "5216622681111@s.whatsapp.net"

  Scenario: Generate wa.me link with referral code
    Given a client with ref_code "REF-ABC123"
    When the operator calls "whatsapp_create_wa_me_link"
    Then the link "https://wa.me/5216623538272?text=REF-ABC123" is returned
    And event "whatsapp:wa_me_link:created" is emitted

  Scenario: Generate QR code for wa.me link
    Given a client with ref_code "REF-ABC123"
    When the operator calls "whatsapp_create_qr"
    Then a PNG QR code is saved to disk
    And event "whatsapp:qr:created" is emitted

  Scenario: Read QR code
    Given a QR code image at "/tmp/qr.png"
    When the operator calls "whatsapp_read_qr"
    Then the decoded data is returned
    And event "whatsapp:qr:read" is emitted

  Scenario: Generate audio waveform thumbnail
    Given an MP3 file at "/tmp/audio.mp3"
    When the operator calls "whatsapp_send_audio_thumbnail"
    Then a PNG waveform thumbnail is generated
    And the thumbnail is sent to the client
    And event "whatsapp:message:sent" is emitted

  Scenario: Get WhatsApp contacts
    When the operator calls "whatsapp_get_contacts"
    Then a list of contacts is returned
    And each contact has "name" and "phone"

  Scenario: Webhook receives incoming message
    Given the webhook is listening
    When a WhatsApp message arrives from "5216622681111" with text "Hola"
    Then the webhook emits "whatsapp:message:received"
    And the payload contains "from", "text", and "timestamp"

  Scenario: Webhook auto-reconnects on disconnect
    Given the webhook is listening
    When the connection drops
    Then the webhook reconnects within 60 seconds
    And emits "system:whatsapp:reconnected"

  Scenario: Catalog requested via WhatsApp
    Given a client sends "catálogo"
    When the webhook receives the message
    Then it emits "whatsapp:catalog:requested"
    And the system responds with the catalog text

  Scenario: Handle missing audio file
    Given a client with phone "5216622681111"
    And the file "/tmp/noexiste.mp3" does not exist
    When the operator calls "whatsapp_send_voice"
    Then the result is "{"sent": false, "error": "file not found: /tmp/noexiste.mp3"}"

  Scenario: Invalid QR code
    Given a non-QR image at "/tmp/not-qr.png"
    When the operator calls "whatsapp_read_qr"
    Then the result is "{"valid": false, "data": null}"
```
